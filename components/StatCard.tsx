import React from 'react';

interface StatCardProps {
  title: string;
  value: string;
}

const StatCard: React.FC<StatCardProps> = ({ title, value }) => {
  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h3 className="text-xl font-semibold text-gray-700">{title}</h3>
      <p className="text-3xl font-bold text-gray-900 mt-2">{value}</p>
    </div>
  );
};

export default StatCard; 