# HoopSense 🏀

HoopSense is a Next.js application designed to provide insights into NBA player and team statistics. Users can ask natural language queries (e.g., "Compare Steph Curry and Lillard's 3PT% in the 2021 playoffs") and receive summaries, comparisons, and (eventually) visualizations.

## Features

*   **Natural Language Queries**: Uses Google Gemini to understand user queries about NBA stats.
*   **Stat Comparisons**: Displays key statistics for players or teams based on the query.
*   **Data Visualization (Planned)**: Will include charts to visually represent statistical data.
*   **Insights**: Provides LLM-generated summaries and interesting facts related to the query.
*   **Local Data Fetching**: Includes a Python script to fetch NBA data using `nba_api` and store it locally as CSV files.

## Tech Stack

*   **Frontend**: Next.js (App Router), React, TypeScript, Tailwind CSS
*   **Backend API**: Next.js API Routes
*   **Language Model**: Google Gemini 2.5 Flash
*   **Data Fetching (Python Script)**: `nba_api`, `pandas`

## Project Structure

```
hoopsense/
├── app/                    # Next.js App Router (frontend pages and API routes)
│   ├── api/query/route.ts  # API endpoint for handling user queries
│   └── page.tsx            # Homepage
│   └── layout.tsx          # Main layout
│   └── globals.css         # Global styles
├── components/             # Reusable React components
├── public/                 # Static assets
├── scripts/                # Utility scripts
│   └── fetch_nba_stats.py  # Python script to fetch NBA data
├── data/                   # (Gitignored) Directory for storing fetched CSV data
├── .env.local.example      # Example environment variables (create .env.local)
├── .eslintrc.json          # ESLint configuration
├── .gitignore              # Git ignore rules
├── next.config.js          # Next.js configuration
├── package.json            # Project dependencies and scripts
├── postcss.config.js       # PostCSS configuration (for Tailwind)
├── tailwind.config.ts      # Tailwind CSS configuration
└── tsconfig.json           # TypeScript configuration
└── README.md               # This file
```

## Getting Started

### Prerequisites

*   Node.js (v18 or later recommended)
*   npm (or yarn/pnpm)
*   Python (v3.7 or later for the data fetching script)
*   `pip` (Python package installer)

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

3.  **Set up environment variables:**
    *   Create a `.env.local` file in the `hoopsense` directory by copying `.env.local.example` (if it existed - currently it does not, but it's good practice for API keys).
    *   Add your Google Gemini API Key to `.env.local`:
        ```
        GEMINI_API_KEY=YOUR_GEMINI_API_KEY
        ```
    *   _Note: Currently, the Gemini API key is hardcoded in `app/api/query/route.ts`. It is strongly recommended to move this to an environment variable as described above for better security._

4.  **Install Python dependencies (for data fetching script):**
    ```bash
    pip install nba_api pandas
    ```

### Running the Development Server

1.  **Start the Next.js development server:**
    ```bash
    npm run dev
    ```
    Open [http://localhost:3000](http://localhost:3000) in your browser.

### Fetching NBA Data (Optional)

To populate the local `data/` directory with NBA statistics (which can be used for future local data processing features):

1.  **Navigate to the scripts directory (if you are in `hoopsense` root):**
    ```bash
    # No, stay in the hoopsense root for the next command, 
    # or run from anywhere with: python scripts/fetch_nba_stats.py 
    ```
2.  **Run the Python script:**
    ```bash
    python scripts/fetch_nba_stats.py 
    ```
    This will create CSV files in the `hoopsense/data/` directory. You can modify the `SEASON`, `SEASON_TYPE`, etc., parameters at the top of the `fetch_nba_stats.py` script to fetch different datasets.

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
