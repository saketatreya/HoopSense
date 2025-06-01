# HoopSense 🏀

HoopSense is a Next.js application designed to provide insights into NBA player and team statistics. Users can ask natural language queries and receive summaries, comparisons, and data visualizations.

## Features

*   **Natural Language Query to SQL**: Uses Google Gemini to translate natural language questions about basketball into SQL queries.
*   **PostgreSQL Database Interaction**: Executes generated SQL against a PostgreSQL database to fetch data.
*   **Data Visualization**: Generates charts from query results using Altair.
*   **Dynamic DB Schema Prompting**: Automatically fetches the database schema to provide relevant context to the LLM.
*   **Configurable Environment**: Uses `.env` files for managing API keys and database credentials for Python scripts.
*   **Stats API Integration (Initial Mock)**: The frontend currently interacts with a Next.js API route that uses Gemini for query structuring and returns mocked data. Future integration can leverage the Python query engine.
*   **NBA Data Fetching Script**: Includes a Python script (`fetch_nba_stats.py`) to fetch NBA data using `nba_api` and store it locally as CSV files for potential database population.

## Tech Stack

*   **Frontend**: Next.js (App Router), React, TypeScript, Tailwind CSS
*   **Backend API (Current)**: Next.js API Routes (with Gemini for query structuring)
*   **Language Model**: Google Gemini 1.5 Flash
*   **Python Query Engine (`query_engine.py`)**: 
    *   NL-to-SQL: Google Gemini
    *   Database: PostgreSQL (`psycopg2`)
    *   Charting: Altair
    *   Environment Management: `python-dotenv`
*   **Data Fetching Script (`fetch_nba_stats.py`)**: `nba_api`, `pandas`

## Project Structure

```
hoopsense/
├── app/                    # Next.js App Router (frontend pages and API routes)
│   ├── api/query/route.ts  # API endpoint for user queries (currently mock/Gemini structure)
│   └── ...                 # Frontend pages (page.tsx, layout.tsx)
├── components/             # Reusable React components
├── public/                 # Static assets
├── scripts/                # Python scripts
│   ├── query_engine.py     # Converts NL to SQL, queries DB, generates charts
│   ├── fetch_nba_stats.py  # Fetches NBA data to CSVs
│   └── .env                # (Gitignored) Environment variables for Python scripts
│   └── .env.example        # Example for .env file
├── data/                   # (Gitignored) Directory for storing fetched CSV data from fetch_nba_stats.py
├── .env.local              # (Gitignored) Environment variables for Next.js app (e.g., frontend API keys)
├── .gitignore              # Git ignore rules
├── README.md               # This file
└── ...                     # Other Next.js project files (package.json, tsconfig.json, etc.)
```

## Getting Started

### Prerequisites

*   Node.js (v18 or later recommended)
*   npm (or yarn/pnpm)
*   Python (v3.7 or later)
*   `pip` (Python package installer)
*   PostgreSQL server (running and accessible)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/saketatreya/HoopSense.git
    cd HoopSense/hoopsense
    ```

2.  **Install frontend dependencies:**
    ```bash
    npm install
    ```

3.  **Set up Next.js environment variables (Frontend):**
    *   Create a `.env.local` file in the `hoopsense` root directory.
    *   If your Next.js app needs any client-side accessible API keys in the future (not currently the case for the Gemini key used by the backend API route), you would add them here, prefixed with `NEXT_PUBLIC_`.
    *   _Note: The Gemini API key for the `app/api/query/route.ts` is currently hardcoded. For production, this backend API key should be a true environment variable on the server, not exposed to the client and not in `.env.local`._

4.  **Set up Python script environment variables (Backend Query Engine):**
    *   Navigate to the `hoopsense/scripts/` directory.
    *   Create a `.env` file by copying `.env.example` (if you haven't already).
        ```bash
        cp .env.example .env 
        ```
    *   Edit `hoopsense/scripts/.env` and provide your actual:
        *   `GEMINI_API_KEY`
        *   `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` for your PostgreSQL database.
        *   Optionally, set `LOG_LEVEL` (e.g., `DEBUG`, `INFO`).

5.  **Install Python dependencies:**
    From the `hoopsense` root directory (or directly within the `scripts` environment if you manage it separately):
    ```bash
    pip install google-generative-ai psycopg2-binary pandas altair python-dotenv nba_api
    ```

### Running the Next.js Development Server (Frontend)

1.  From the `hoopsense` root directory:
    ```bash
    npm run dev
    ```
    Open [http://localhost:3000](http://localhost:3000) in your browser. The frontend will interact with the Next.js API route at `/api/query`.

### Running Python Scripts

1.  **Fetching NBA Data (to CSVs):**
    From the `hoopsense` root directory:
    ```bash
    python scripts/fetch_nba_stats.py
    ```
    This populates the `hoopsense/data/` directory. Modify parameters in the script for different seasons/data types.

2.  **Testing the NL-to-SQL Query Engine:**
    Before running, ensure your `hoopsense/scripts/.env` is correctly configured and your PostgreSQL database is set up and accessible. The script will attempt to dynamically fetch your DB schema.
    From the `hoopsense` root directory:
    ```bash
    python scripts/query_engine.py
    ```
    This script will run test queries (defined in its `if __name__ == '__main__':` block), convert them to SQL using Gemini, execute against your database (or use a mock if DB creds in `.env` are still placeholders), and attempt to generate Altair chart JSONs.

## Future Integration

The Next.js API route (`app/api/query/route.ts`) currently uses Gemini for structuring queries and returns mocked data. A future step is to modify this API route to call the Python `query_engine.py` script (or a service built from it) to get real data and visualizations from the PostgreSQL database.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue.

## License

This project is open source (details to be added if a specific license is chosen).

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
