import { NextResponse } from 'next/server';
import { GoogleGenerativeAI, HarmCategory, HarmBlockThreshold } from '@google/generative-ai';

const GEMINI_API_KEY = 'AIzaSyCYkS7NpcLUtWBRBdZl8QMSEadWYNqAeK0'; // Store securely in environment variables for production

const genAI = new GoogleGenerativeAI(GEMINI_API_KEY);
const model = genAI.getGenerativeModel({
  model: 'gemini-1.5-flash-latest', // Using gemini-1.5-flash as requested (implicitly by latest tag)
});

const generationConfig = {
  temperature: 0.7,
  topP: 0.95,
  topK: 64,
  maxOutputTokens: 8192,
  responseMimeType: 'application/json',
};

interface GeminiStructuredResponse {
  players?: string[];
  stat?: string;
  context?: string;
  seasons?: string[];
}

// Helper to generate a fallback or basic mocked response
const getFallbackResponse = (query?: string) => ({
  statCards: [
    { title: "Player A (Fallback)", stat: "Stat (Fallback)", value: "N/A" },
    { title: "Player B (Fallback)", stat: "Stat (Fallback)", value: "N/A" }
  ],
  chartData: [
    { season: "202X", playerA: 0, playerB: 0 },
  ],
  insight: `Could not fully process the query: '${query || "Unknown Query"}'. Displaying fallback data.`
});

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const userQuery = body.query;

    if (!userQuery || typeof userQuery !== 'string') {
      return NextResponse.json({ error: 'Query string is required.' }, { status: 400 });
    }

    const prompt = `
      Analyze the following user query about basketball player statistics: "${userQuery}"

      Extract the following information and return it as a VALID JSON object with ONLY these keys:
      - "players": An array of player names mentioned (e.g., ["Stephen Curry", "Damian Lillard"]). If no specific players, return an empty array or omit.
      - "stat": The specific statistic being asked about (e.g., "3PT%", "points per game", "rebounds").
      - "context": The context of the query, if any (e.g., "playoffs", "regular season", "clutch time"). Omit if not specified.
      - "seasons": An array of seasons or years mentioned (e.g., ["2021", "2022-2023"]). If no specific seasons, return an empty array or omit.

      Example Query: "Compare Curry and Lillard's 3PT% in 2021 playoffs"
      Expected JSON Output:
      {
        "players": ["Stephen Curry", "Damian Lillard"],
        "stat": "3PT%",
        "context": "playoffs",
        "seasons": ["2021"]
      }

      Example Query: "Lebron James total points last season"
      Expected JSON Output:
      {
        "players": ["Lebron James"],
        "stat": "total points",
        "seasons": ["last season"]
      }
      
      Ensure the output is a single, valid JSON object as described.
    `;

    let structuredData: GeminiStructuredResponse | null = null;

    try {
      const chatSession = model.startChat({
        generationConfig,
        history: [],
      });
      const result = await chatSession.sendMessage(prompt);
      const geminiResponseText = result.response.text();
      
      // Attempt to parse the JSON string from Gemini
      // The response might sometimes include ```json ... ```, so we try to strip it.
      let cleanedJsonString = geminiResponseText.replace(/^```json\n/, '').replace(/\n```$/, '');
      structuredData = JSON.parse(cleanedJsonString) as GeminiStructuredResponse;
      
    } catch (geminiError: any) {
      console.error("Gemini API Error or Parsing Failed:", geminiError);
      // Fallback if Gemini fails or response is not as expected
      const fallback = getFallbackResponse(userQuery);
      return NextResponse.json(fallback);
    }

    if (!structuredData || (!structuredData.players && !structuredData.stat)) {
        console.warn("Gemini response lacked expected structure, using fallback.", structuredData);
        const fallback = getFallbackResponse(userQuery);
        return NextResponse.json(fallback);
    }

    // Simulate data fetching/processing based on structuredData from Gemini
    // This is where you'd query your actual database or data source.
    // For now, create a semi-dynamic mocked response based on Gemini's output.

    const players = structuredData.players || ["Player 1", "Player 2"];
    const stat = structuredData.stat || "Requested Stat";
    const context = structuredData.context ? ` in ${structuredData.context}` : "";
    const seasons = structuredData.seasons && structuredData.seasons.length > 0 ? ` for season(s) ${structuredData.seasons.join(', ')}` : "";

    const statCards = players.map((player, index) => ({
      title: player,
      stat: `${stat}${context}${seasons}`,
      value: `${(Math.random() * 30 + 20).toFixed(1)}${stat.includes("%") ? "%" : ""}` // Mocked value
    }));

    const chartData = (
        structuredData.seasons && structuredData.seasons.length > 0 
        ? structuredData.seasons 
        : ["2021", "2022", "2023"] // Default seasons for chart if not specified
    ).map(season => {
      const dataPoint: { season: string, [key: string]: any } = { season };
      players.forEach(player => {
        dataPoint[player.toLowerCase().replace(/\s+/g, '')] = (Math.random() * 50).toFixed(1);
      });
      return dataPoint;
    });

    const insight = `Insight based on your query for ${players.join(' and ')}'s ${stat}${context}${seasons}. For instance, ${players[0]} showed strong performance. (This is a generated insight based on the structured query).`;

    const finalResponse = {
      statCards,
      chartData,
      insight
    };

    return NextResponse.json(finalResponse);

  } catch (error: any) {
    console.error("Overall API Error:", error);
    const fallback = getFallbackResponse("Unknown query due to server error");
    return NextResponse.json(fallback, { status: 500 });
  }
} 