import os
import json
import logging
import pandas as pd
import altair as alt
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
from google.generative_ai import GoogleGenerativeAI

# --- Load Environment Variables ---
# Create a .env file in this directory (scripts/) based on .env.example
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=dotenv_path)

# --- Configuration ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DB_NAME = os.getenv("DB_NAME", "your_db_name")
DB_USER = os.getenv("DB_USER", "your_db_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "your_db_password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# --- Logging Setup ---
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# --- Gemini Configuration ---
if not GEMINI_API_KEY:
    logger.error("GEMINI_API_KEY is not set. Please provide your API key in the .env file.")
    raise ValueError("GEMINI_API_KEY is not set.")
genAI = GoogleGenerativeAI(api_key=GEMINI_API_KEY)
model = genAI.get_generative_model(model_name='gemini-1.5-flash-latest')
generation_config = {
    "temperature": 0.2,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 4096,
    "response_mime_type": "application/json",
}

def get_db_connection():
    """Establishes and returns a PostgreSQL database connection."""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        logger.info(f"Successfully connected to PostgreSQL database '{DB_NAME}' on {DB_HOST}:{DB_PORT}")
        return conn
    except psycopg2.Error as e:
        logger.error(f"Error connecting to PostgreSQL database: {e}")
        raise

def fetch_database_schema_dynamically() -> str:
    """Fetches schema information (tables, columns, types) from the PostgreSQL database."""
    schema_parts = ["Database Schema Overview (Dynamically Fetched):\n"]
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get table names
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()

        for i, (table_name,) in enumerate(tables):
            schema_parts.append(f"{i+1}. `{table_name}` table:")
            
            # Get columns for each table
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = %s
                ORDER BY ordinal_position;
            """, (table_name,))
            columns = cursor.fetchall()
            for col_name, data_type, is_nullable, col_default in columns:
                col_desc = f"    *   `{col_name}` ({data_type.upper()})"
                if is_nullable == 'NO':
                    col_desc += ", NOT NULL"
                if col_default:
                    col_desc += f", DEFAULT {col_default}"
                schema_parts.append(col_desc)
            
            # Get primary keys for the table
            cursor.execute("""
                SELECT kcu.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu 
                    ON tc.constraint_name = kcu.constraint_name AND tc.table_schema = kcu.table_schema
                WHERE tc.constraint_type = 'PRIMARY KEY' AND tc.table_name = %s AND tc.table_schema = 'public';
            """, (table_name,))
            pk_columns = [row[0] for row in cursor.fetchall()]
            if pk_columns:
                schema_parts.append(f"        Primary Key(s): ({', '.join(pk_columns)})")

            # Get foreign keys for the table
            cursor.execute("""
                SELECT 
                    kcu.column_name, 
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name 
                FROM information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name=%s AND tc.table_schema = 'public';
            """, (table_name,))
            fk_constraints = cursor.fetchall()
            if fk_constraints:
                schema_parts.append("        Foreign Key(s):")
                for col, f_table, f_col in fk_constraints:
                     schema_parts.append(f"            `{col}` REFERENCES `{f_table}`(`{f_col}`)")
            schema_parts.append("") # Add a newline for readability

        cursor.close()
        logger.info("Successfully fetched database schema.")
        # Add general advice for Gemini
        schema_parts.append("General SQL Generation Guidelines:")
        schema_parts.append("- Prioritize PostgreSQL compatible SQL.")
        schema_parts.append("- Use table aliases for clarity if joining multiple tables.")
        schema_parts.append("- For percentage calculations (e.g., 3PT%), if not directly available, calculate using appropriate fields (e.g., (SUM(fg3m) * 100.0 / SUM(fg3a)) AS three_point_percentage). Handle potential division by zero if necessary.")
        schema_parts.append("- Pay close attention to data types for comparisons, aggregations, and functions.")
        return "\n".join(schema_parts)
    except psycopg2.Error as e:
        logger.error(f"Error fetching database schema: {e}")
        return f"Error fetching schema: Could not connect or query information_schema. {e}" # Fallback schema
    finally:
        if conn:
            conn.close()

DATABASE_SCHEMA_DESCRIPTION = fetch_database_schema_dynamically()
logger.debug(f"Dynamically Fetched Schema for Prompt:\n{DATABASE_SCHEMA_DESCRIPTION}")

def get_nl_to_sql(natural_language_query: str) -> tuple[str | None, str | None]:
    """Converts natural language query to SQL using Gemini."""
    prompt = f"""
    Given the following database schema:
    {DATABASE_SCHEMA_DESCRIPTION}

    Convert the following natural language basketball question into a syntactically correct PostgreSQL query. 
    Return ONLY a JSON object containing two keys: "sql_query" (the generated SQL string) and "query_explanation" (a brief natural language explanation of what the SQL query is trying to achieve).
    Do not include any other text, greetings, or markdown formatting outside of this JSON object.

    Natural Language Question: "{natural_language_query}"

    JSON Output:
    """
    logger.debug(f"Sending following prompt to Gemini:\n{prompt}")
    try:
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        response_text = response.text
        logger.debug(f"Raw Gemini response text: {response_text}")
        
        if response_text.strip().startswith("```json"):
            response_text = response_text.strip()[7:-3].strip()
        elif response_text.strip().startswith("```"):
             response_text = response_text.strip()[3:-3].strip()

        data = json.loads(response_text)
        sql_query = data.get("sql_query")
        query_explanation = data.get("query_explanation")
        
        if not sql_query:
            logger.warning("Gemini did not return an SQL query in the expected JSON structure.")
            return None, "Gemini did not return an SQL query."
        logger.info(f"Successfully converted NL to SQL. Explanation: {query_explanation}")
        logger.debug(f"Generated SQL: {sql_query}")
        return sql_query, query_explanation
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding Gemini JSON response: {e}. Raw response: \"{response_text if 'response_text' in locals() else 'N/A'}\"")
        return None, f"Error decoding LLM response: {e}. Raw output: {response_text if 'response_text' in locals() else 'N/A'}"
    except Exception as e:
        logger.error(f"Error calling Gemini API: {e}", exc_info=True)
        return None, f"Error interacting with LLM: {e}"

def execute_sql_query(sql_query: str) -> tuple[pd.DataFrame | None, str | None]:
    """Executes the SQL query against the PostgreSQL database and returns a DataFrame."""
    conn = None
    try:
        conn = get_db_connection()
        logger.info(f"Executing SQL: {sql_query}")
        df = pd.read_sql_query(sql_query, conn)
        logger.info(f"SQL query executed successfully, returned {len(df)} rows.")
        return df, None
    except psycopg2.Error as e:
        logger.error(f"Database error during query execution: {e}. SQL: {sql_query}")
        db_error_message = f"Database error: {e}. Check SQL syntax and DB connection."
        if "relation" in str(e).lower() and "does not exist" in str(e).lower():
            db_error_message += " This often means a table name in the SQL query is incorrect or doesn't exist in your database schema described to the LLM."
        elif "column" in str(e).lower() and "does not exist" in str(e).lower():
            db_error_message += " This often means a column name in the SQL query is incorrect for the specified table(s)."
        return None, db_error_message
    except Exception as e:
        logger.error(f"An unexpected error occurred during SQL execution: {e}. SQL: {sql_query}", exc_info=True)
        return None, f"An unexpected error occurred: {e}"
    finally:
        if conn:
            conn.close()
            logger.info("Database connection closed.")

def sanitize_and_coerce_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """Attempts to sanitize and coerce dtypes for better Altair compatibility."""
    if df is None or df.empty:
        return df
    df_copy = df.copy()
    for col in df_copy.columns:
        # Attempt to convert to numeric if possible, handling errors by keeping original
        try:
            df_copy[col] = pd.to_numeric(df_copy[col])
            logger.debug(f"Column '{col}' coerced to numeric.")
            continue # Skip to next column if numeric conversion is successful
        except (ValueError, TypeError):
            pass # Not numeric, try datetime

        # Attempt to convert to datetime if possible, handling errors
        try:
            df_copy[col] = pd.to_datetime(df_copy[col])
            logger.debug(f"Column '{col}' coerced to datetime.")
            continue
        except (ValueError, TypeError):
            pass # Not datetime, leave as object/string
        
        if df_copy[col].dtype == 'object':
             try:
                # For object columns, try to strip whitespace if they are strings
                df_copy[col] = df_copy[col].astype(str).str.strip()
             except AttributeError: # Not a string series
                pass 
    logger.info("Data types sanitized/coerced for charting.")
    return df_copy 

def create_altair_chart(df: pd.DataFrame, nl_query: str) -> dict | None:
    """Creates a generic Altair chart from the DataFrame. Returns a structured dict."""
    output = {"chart_spec": None, "summary_stats": None, "chart_type": "none", "message": None}
    if df is None or df.empty:
        output["message"] = "No data provided to create chart."
        return output

    df_sanitized = sanitize_and_coerce_dtypes(df.copy()) # Work with a sanitized copy
    output["summary_stats"] = df_sanitized.describe(include='all').to_dict()

    chart_title = f"Result for: {nl_query[:50]}{'...' if len(nl_query) > 50 else ''}"
    num_rows, num_cols = df_sanitized.shape
    chart = None

    try:
        if num_cols == 1 and pd.api.types.is_numeric_dtype(df_sanitized.iloc[:, 0].dtype):
            col_name = df_sanitized.columns[0]
            df_chart = pd.DataFrame({'label': [col_name], 'value': [df_sanitized.iloc[0,0]]})
            chart = alt.Chart(df_chart).mark_bar().encode(
                x=alt.X('label:N', title=''),
                y=alt.Y('value:Q', title=col_name),
                tooltip=['label:N', 'value:Q']
            ).properties(title=chart_title)
            output["chart_type"] = "bar_single_value"

        elif num_cols >= 2:
            numeric_cols = [col for col in df_sanitized.columns if pd.api.types.is_numeric_dtype(df_sanitized[col].dtype)]
            string_cols = [col for col in df_sanitized.columns if pd.api.types.is_string_dtype(df_sanitized[col].dtype) or pd.api.types.is_categorical_dtype(df_sanitized[col].dtype)]
            datetime_cols = [col for col in df_sanitized.columns if pd.api.types.is_datetime64_any_dtype(df_sanitized[col].dtype)]

            if datetime_cols and numeric_cols:
                x_col, y_col = datetime_cols[0], numeric_cols[0]
                chart = alt.Chart(df_sanitized).mark_line().encode(
                    x=alt.X(f'{x_col}:T', title=x_col),
                    y=alt.Y(f'{y_col}:Q', title=y_col),
                    tooltip=[alt.Tooltip(f'{x_col}:T', title=x_col), alt.Tooltip(f'{y_col}:Q', title=y_col)]
                ).properties(title=chart_title)
                output["chart_type"] = "line"
            elif string_cols and numeric_cols:
                x_col, y_col = string_cols[0], numeric_cols[0]
                df_subset = df_sanitized
                if df_sanitized[x_col].nunique() > 20:
                     # Attempt to sort by y_col if it's truly numeric after sanitization
                     if pd.api.types.is_numeric_dtype(df_sanitized[y_col].dtype):
                         df_subset = df_sanitized.nlargest(20, y_col)
                     else: # Fallback if y_col is not numeric for some reason
                         df_subset = df_sanitized.head(20) 
                     chart_title += " (Top 20 categories)"
                
                chart = alt.Chart(df_subset).mark_bar().encode(
                    x=alt.X(f'{x_col}:N', sort='-y', title=x_col),
                    y=alt.Y(f'{y_col}:Q', title=y_col),
                    tooltip=[alt.Tooltip(f'{x_col}:N', title=x_col), alt.Tooltip(f'{y_col}:Q', title=y_col)] + \
                              [alt.Tooltip(f'{nc}:Q', title=nc) for nc in numeric_cols[1:3] if nc in df_subset.columns]
                ).properties(title=chart_title)
                output["chart_type"] = "bar"
            elif len(numeric_cols) >= 2:
                x_col, y_col = numeric_cols[0], numeric_cols[1]
                color_col = string_cols[0] if string_cols and df_sanitized[string_cols[0]].nunique() < 10 else None
                encode_params = {
                    'x': alt.X(f'{x_col}:Q', title=x_col),
                    'y': alt.Y(f'{y_col}:Q', title=y_col),
                    'tooltip': [alt.Tooltip(f'{x_col}:Q', title=x_col), alt.Tooltip(f'{y_col}:Q', title=y_col)]
                }
                if color_col:
                    encode_params['color'] = alt.Color(f'{color_col}:N', title=color_col)
                    encode_params['tooltip'].append(alt.Tooltip(f'{color_col}:N', title=color_col))
                
                chart = alt.Chart(df_sanitized).mark_circle(size=60).encode(**encode_params).properties(title=chart_title)
                output["chart_type"] = "scatter"
            else:
                output["message"] = "Data retrieved, but a specific chart could not be automatically generated based on column types. Please examine the raw data."
        else:
            output["message"] = "Data not suitable for standard charting (e.g., single non-numeric column or too few columns)."
        
        if chart:
            output["chart_spec"] = chart.to_dict() # Use to_dict() for JSON serializable spec
            logger.info(f"Altair chart ({output['chart_type']}) generated successfully.")
        else:
            logger.warning(f"Altair chart object was not created. Message: {output.get('message')}")

    except Exception as e:
        logger.error(f"Error creating Altair chart: {e}", exc_info=True)
        output["message"] = f"Error during chart generation: {e}"
        output["chart_spec"] = None # Ensure spec is None on error
    
    return output

def process_nl_query(natural_language_query: str) -> dict:
    """Processes a natural language query, converts to SQL, executes, and visualizes."""
    output = {
        "natural_query": natural_language_query,
        "sql_query": None,
        "query_explanation": None,
        "chart_info": {"chart_spec": None, "summary_stats": None, "chart_type": "none", "message": "Processing started..."},
        "data_preview": None,
        "explanation": None,
        "error": None
    }
    logger.info(f"Processing natural language query: '{natural_language_query}'")

    sql_query, query_explanation = get_nl_to_sql(natural_language_query)
    output["sql_query"] = sql_query
    output["query_explanation"] = query_explanation

    if not sql_query:
        output["error"] = "Failed to convert natural language query to SQL."
        output["explanation"] = query_explanation or "The language model could not generate an SQL query."
        logger.warning(f"NL to SQL failed for query: '{natural_language_query}'. Reason: {output['explanation']}")
        return output

    df, db_error = execute_sql_query(sql_query)

    if db_error:
        output["error"] = "Database query execution failed."
        output["explanation"] = db_error
        logger.error(f"DB execution failed for SQL: '{sql_query}'. Reason: {db_error}")
        return output
    
    if df is None:
        output["error"] = "Database query returned no data or failed silently."
        output["explanation"] = "The SQL query executed but returned no data, or an unknown database error occurred."
        logger.warning(f"DB query returned None for SQL: '{sql_query}'")
        return output
    
    if df.empty:
        output["explanation"] = "The query executed successfully but returned no results."
        output["data_preview"] = {}
        logger.info(f"Query returned no results for SQL: '{sql_query}'")
        output["chart_info"]["message"] = "Query returned no results, so no chart can be generated."
        return output
        
    output["data_preview"] = df.head().to_dict(orient='records')

    chart_info_dict = create_altair_chart(df, natural_language_query)
    output["chart_info"] = chart_info_dict
    
    if chart_info_dict.get("chart_spec"):
        output["explanation"] = query_explanation or "Query processed and chart generated."
    elif chart_info_dict.get("message"):
        output["explanation"] = chart_info_dict["message"]
    else:
        output["explanation"] = query_explanation or "Query processed, data retrieved, but chart could not be fully generated or data was unsuitable."
        if not output["error"]:
             output["error"] = chart_info_dict.get("message", "Chart generation failed or data was unsuitable.")

    logger.info(f"Successfully processed query: '{natural_language_query}'")
    return output

if __name__ == '__main__':
    logger.info("Query Engine Module started for direct testing.")
    
    # --- Mocking for testing without a live DB (if DB_USER is still 'your_db_user') ---
    # This allows testing NL-to-SQL and basic chart logic without a full DB setup.
    # To use your actual DB, ensure .env is configured and comment out/remove this mock block.
    if DB_USER == 'your_db_user': # A simple check to see if DB creds are default
        logger.warning("Default DB credentials detected. Using MOCKED database execution.")
        logger.warning("To use actual DB: configure .env and remove/comment out mock_execute_sql_query block.")
        _original_execute_sql_query = execute_sql_query
        
        # Global variable to hold the current natural query for mock access
        current_natural_query_for_mock = ""

        def mock_execute_sql_query(sql_query: str):
            logger.info(f"MOCK EXEC SQL for '{current_natural_query_for_mock}': {sql_query}")
            if "Steph Curry" in current_natural_query_for_mock and "points" in current_natural_query_for_mock:
                mock_df = pd.DataFrame([{'player_name': 'Stephen Curry', 'avg_pts': 29.4, 'season': '2022-23'}])
                return mock_df, None
            elif "LeBron James" in current_natural_query_for_mock and "Kevin Durant" in current_natural_query_for_mock:
                mock_df = pd.DataFrame([
                    {'player_name': 'LeBron James', 'total_rebounds': 150, 'season': '2023 Playoffs'},
                    {'player_name': 'Kevin Durant', 'total_rebounds': 120, 'season': '2023 Playoffs'}
                ])
                return mock_df, None
            elif "Los Angeles Lakers" in current_natural_query_for_mock:
                 mock_df = pd.DataFrame([
                    {'player_name': 'LeBron James', 'position': 'F'},
                    {'player_name': 'Anthony Davis', 'position': 'F-C'}
                ])
                 return mock_df, None
            elif "shot chart" in current_natural_query_for_mock:
                mock_df = pd.DataFrame([
                    {'x_coordinate': 10, 'y_coordinate': 50, 'shot_made_flag': True, 'player_name': 'Klay Thompson'},
                    {'x_coordinate': -100, 'y_coordinate': 200, 'shot_made_flag': False, 'player_name': 'Klay Thompson'},
                    {'x_coordinate': 0, 'y_coordinate': 0, 'shot_made_flag': True, 'player_name': 'Klay Thompson'},
                ])
                return mock_df, None
            elif "highest average points scored" in current_natural_query_for_mock:
                mock_df = pd.DataFrame([
                    {'team_name': 'Sacramento Kings', 'avg_pts_scored': 120.7},
                    {'team_name': 'Boston Celtics', 'avg_pts_scored': 118.5},
                    {'team_name': 'Denver Nuggets', 'avg_pts_scored': 117.2},
                ])
                return mock_df, None
            logger.warning(f"Query '{current_natural_query_for_mock}' not recognized by mock setup. Returning empty DataFrame.")
            return pd.DataFrame(), None # Return empty DF instead of error for mock
        
        execute_sql_query = mock_execute_sql_query # Apply the mock
    # ------------------------------------------------------------

    test_queries = [
        "What were Steph Curry's average points per game in the 2022-23 season?",
        "Compare total rebounds for LeBron James and Kevin Durant in the 2023 playoffs.",
        "List all players from the Los Angeles Lakers and their positions.",
        "Show me the shot chart for Klay Thompson from his last 10 games.",
        "Which team had the highest average points scored in the 2023 regular season?",
        "Average assists for point guards in the 2024 season so far?"
    ]

    for i, natural_query in enumerate(test_queries):
        print(f"\n{'-'*15} Test Query {i+1} {'-'*15}")
        logger.info(f"Starting test query {i+1}: '{natural_query}'")
        
        if 'execute_sql_query' in globals() and globals()['execute_sql_query'].__name__ == 'mock_execute_sql_query':
            current_natural_query_for_mock = natural_query # Set for mock to access
        
        result = process_nl_query(natural_query)
        
        print(f"Natural Language Query: {result['natural_query']}")
        print(f"Generated SQL: {result['sql_query']}")
        print(f"Query Explanation from LLM: {result['query_explanation']}")
        print(f"Overall Explanation/Status: {result['explanation']}")
        
        if result["error"]:
            print(f"Error: {result['error']}")
        
        if result["chart_info"] and result["chart_info"].get("chart_spec"):
            print(f"Chart Type: {result['chart_info']['chart_type']}")
            # print("Chart JSON Spec (first 300 chars):", str(result["chart_info"]["chart_spec"])[:300]+"...")
            # print("Summary Stats:", json.dumps(result["chart_info"]["summary_stats"], indent=2))
        elif result["data_preview"]:
            print(f"Data Preview: {result['data_preview']}")
        print(f"{'~'*50}")

    # Restore original execute_sql_query if it was mocked
    if '_original_execute_sql_query' in locals() and DB_USER == 'your_db_user':
         execute_sql_query = _original_execute_sql_query
         logger.info("Restored original database execution function.")

