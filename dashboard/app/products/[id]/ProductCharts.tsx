"use client";

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export function ProductCharts({ priceHistory, stockHistory }: { priceHistory: any[], stockHistory: any[] }) {
  const hasPrices = priceHistory.some(p => p.price !== null);
  
  return (
    <div className="space-y-8 mt-6">
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Price History</h3>
        {!hasPrices ? (
          <div className="flex items-center justify-center h-64 bg-gray-50 rounded border border-dashed border-gray-300">
            <p className="text-gray-500">Price data is unavailable for this product.</p>
          </div>
        ) : (
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={priceHistory}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="timestamp" 
                  tickFormatter={(tick) => new Date(tick).toLocaleDateString()}
                />
                <YAxis domain={['auto', 'auto']} />
                <Tooltip 
                  labelFormatter={(label) => new Date(label).toLocaleString()}
                  formatter={(value: any) => [`${value}`, 'Price']}
                />
                <Line type="monotone" dataKey="price" stroke="#2563eb" activeDot={{ r: 8 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Stock History</h3>
        {stockHistory.length === 0 ? (
          <div className="flex items-center justify-center h-64 bg-gray-50 rounded border border-dashed border-gray-300">
            <p className="text-gray-500">No stock data recorded yet.</p>
          </div>
        ) : (
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={stockHistory}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="timestamp"
                  tickFormatter={(tick) => new Date(tick).toLocaleDateString()}
                />
                <YAxis ticks={[0, 1]} tickFormatter={(tick) => tick === 1 ? 'In Stock' : 'Out'} domain={[0, 1]} />
                <Tooltip 
                  labelFormatter={(label) => new Date(label).toLocaleString()}
                  formatter={(value: any) => [value ? 'In Stock' : 'Out of Stock', 'Status']}
                />
                <Line type="stepAfter" dataKey={(d) => d.in_stock ? 1 : 0} stroke="#16a34a" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </div>
  );
}
