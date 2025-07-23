import React from 'react';

interface RevenueChartProps {
  data: Record<string, {
    revenue: number;
    expenses: number;
    profit: number;
  }>;
}

export default function RevenueChart({ data }: RevenueChartProps) {
  const months = Object.keys(data).sort();
  const maxValue = Math.max(
    ...months.map(month => Math.max(data[month].revenue, data[month].expenses))
  );

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-green-500 rounded"></div>
          <span className="text-sm text-gray-600">Revenue</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-red-500 rounded"></div>
          <span className="text-sm text-gray-600">Expenses</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-blue-500 rounded"></div>
          <span className="text-sm text-gray-600">Profit</span>
        </div>
      </div>

      <div className="relative h-64">
        <div className="flex items-end justify-between h-full space-x-2">
          {months.map((month) => {
            const monthData = data[month];
            const revenueHeight = (monthData.revenue / maxValue) * 100;
            const expensesHeight = (monthData.expenses / maxValue) * 100;
            const profitHeight = (monthData.profit / maxValue) * 100;

            return (
              <div key={month} className="flex-1 flex flex-col items-center">
                <div className="w-full flex items-end justify-center space-x-1 mb-2" style={{ height: '200px' }}>
                  <div
                    className="bg-green-500 rounded-t w-4"
                    style={{ height: `${revenueHeight}%` }}
                    title={`Revenue: ${monthData.revenue.toLocaleString()} MAD`}
                  ></div>
                  <div
                    className="bg-red-500 rounded-t w-4"
                    style={{ height: `${expensesHeight}%` }}
                    title={`Expenses: ${monthData.expenses.toLocaleString()} MAD`}
                  ></div>
                  <div
                    className="bg-blue-500 rounded-t w-4"
                    style={{ height: `${profitHeight}%` }}
                    title={`Profit: ${monthData.profit.toLocaleString()} MAD`}
                  ></div>
                </div>
                <span className="text-xs text-gray-500 transform -rotate-45 origin-left">
                  {month}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}