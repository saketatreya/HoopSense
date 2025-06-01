import React from 'react';

const QueryInput: React.FC = () => {
  return (
    <div className="my-8 w-full max-w-2xl mx-auto">
      <input
        type="text"
        placeholder="e.g. Compare Steph Curry and Lillard's 3PT% in 2021 playoffs"
        className="w-full p-4 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      />
    </div>
  );
};

export default QueryInput; 