'use client';

import React, { useState } from 'react';
import Header from "@/components/Header";
import QueryInput from "@/components/QueryInput";
import StatCard from "@/components/StatCard";
import ChartContainer from "@/components/ChartContainer";
import InsightSection from "@/components/InsightSection";

interface StatCardData {
  title: string;
  stat: string; // Added stat property to match API response
  value: string;
}

interface ChartDataPoint {
  [key: string]: any;
}

interface ApiResponse {
  statCards: StatCardData[];
  chartData: ChartDataPoint[];
  insight: string;
}

export default function HomePage() {
  const [query, setQuery] = useState('');
  const [statCards, setStatCards] = useState<StatCardData[] | null>(null);
  const [chartData, setChartData] = useState<ChartDataPoint[] | null>(null);
  const [insight, setInsight] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleQueryChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value);
  };

  const handleSubmitQuery = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!query.trim()) {
      setError("Please enter a query.");
      return;
    }

    setIsLoading(true);
    setError(null);
    setStatCards(null);
    setChartData(null);
    setInsight(null);

    try {
      const response = await fetch('/api/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const data: ApiResponse = await response.json();
      setStatCards(data.statCards);
      setChartData(data.chartData);
      setInsight(data.insight);

    } catch (err: any) {
      setError(err.message || "An unexpected error occurred.");
      setStatCards(null); // Clear data on error
      setChartData(null);
      setInsight(null);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      <Header />
      <main className="flex-grow container mx-auto p-4 md:p-8">
        <QueryInput 
          value={query} 
          onChange={handleQueryChange} 
          onSubmit={handleSubmitQuery} 
          isLoading={isLoading} 
        />

        {error && (
          <div className="my-4 p-4 bg-red-100 text-red-700 border border-red-400 rounded-lg">
            <p>Error: {error}</p>
          </div>
        )}

        {isLoading && (
          <div className="my-8 text-center">
            <p className="text-xl text-gray-600">Loading data...</p> {/* Basic loading indicator */}
          </div>
        )}

        {!isLoading && !error && statCards && statCards.length > 0 && (
          <section className="my-8">
            <h2 className="text-2xl font-semibold text-gray-700 mb-4">Stats Summary</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {statCards.map((card, index) => (
                <StatCard key={index} title={`${card.title} - ${card.stat}`} value={card.value} />
              ))}
            </div>
          </section>
        )}

        {!isLoading && !error && chartData && (
          <section className="my-8">
            <h2 className="text-2xl font-semibold text-gray-700 mb-4">Chart Section</h2>
            <ChartContainer chartData={chartData} />
          </section>
        )}

        {!isLoading && !error && insight && (
          <section className="my-8">
            <InsightSection insight={insight} />
          </section>
        )}

        {/* Initial placeholder/welcome message if no data loaded yet and not loading/no error */}
        {!isLoading && !error && !statCards && !chartData && !insight && (
           <div className="text-center py-10">
             <p className="text-xl text-gray-500">Enter a query above to get started!</p>
           </div>
        )}

      </main>
      <footer className="bg-gray-800 text-white p-4 text-center">
        <p>&copy; {new Date().getFullYear()} HoopSense. All rights reserved.</p>
      </footer>
    </div>
  );
}
