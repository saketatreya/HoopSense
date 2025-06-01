import React from 'react';

const InsightSection: React.FC = () => {
  return (
    <div className="bg-blue-50 p-6 rounded-lg shadow-md">
      <h3 className="text-xl font-semibold text-blue-800">Did You Know?</h3>
      <p className="text-blue-700 mt-2">
        Interesting facts and LLM-generated summaries will appear here.
      </p>
    </div>
  );
};

export default InsightSection; 