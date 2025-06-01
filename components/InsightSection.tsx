import React from 'react';

interface InsightSectionProps {
  insight: string | null;
}

const InsightSection: React.FC<InsightSectionProps> = ({ insight }) => {
  return (
    <div className="bg-blue-50 p-6 rounded-lg shadow-md">
      <h3 className="text-xl font-semibold text-blue-800">Did You Know?</h3>
      {insight ? (
        <p className="text-blue-700 mt-2">{insight}</p>
      ) : (
        <p className="text-blue-700 mt-2">
          Submit a query to see interesting facts and LLM-generated summaries here.
        </p>
      )}
    </div>
  );
};

export default InsightSection; 