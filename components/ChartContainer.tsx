import React from 'react';

interface ChartDataPoint {
  [key: string]: any; // Allow any other properties
}

interface ChartContainerProps {
  chartData: ChartDataPoint[] | null;
}

const ChartContainer: React.FC<ChartContainerProps> = ({ chartData }) => {
  return (
    <div className="bg-white p-6 rounded-lg shadow-md min-h-[300px] flex flex-col items-center justify-center">
      {chartData && chartData.length > 0 ? (
        <pre className="text-xs overflow-auto text-gray-800 w-full text-left">
          {JSON.stringify(chartData, null, 2)}
        </pre>
      ) : (
        <p className="text-gray-500">Chart will be displayed here once data is available.</p>
      )}
    </div>
  );
};

export default ChartContainer; 