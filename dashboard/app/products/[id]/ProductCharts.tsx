"use client";

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export function ProductCharts({ priceHistory, stockHistory }: { priceHistory: any[], stockHistory: any[] }) {
  const hasPrices = priceHistory.some(p => p.price !== null);
  
  // Custom tooltip styles for the dark theme
  const customTooltipStyle = {
    backgroundColor: '#171D2B', // panel
    border: '1px solid #2A3244', // hairline
    color: '#E7E5DE', // text-primary
    fontFamily: 'var(--font-plex), monospace',
    fontSize: '12px'
  };

  return (
    <div className="space-y-6 mt-6">
      <div className="border border-hairline bg-panel p-4 sm:p-6 rounded-sm">
        <h3 className="text-sm font-bold uppercase tracking-wider text-text-primary mb-6">Price History</h3>
        {!hasPrices ? (
          <div className="flex items-center justify-center h-64 bg-ink/30 border border-dashed border-hairline rounded-sm">
            <p className="text-neutral font-mono text-xs uppercase">PRICE_DATA_UNAVAILABLE</p>
          </div>
        ) : (
          <div className="h-64 font-mono text-xs">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={priceHistory}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2A3244" vertical={false} />
                <XAxis 
                  dataKey="timestamp" 
                  stroke="#8A93A6"
                  tick={{ fill: '#8A93A6' }}
                  tickFormatter={(tick) => new Date(tick).toLocaleDateString([], { month: 'short', day: 'numeric' })}
                  tickMargin={10}
                />
                <YAxis 
                  domain={['auto', 'auto']} 
                  stroke="#8A93A6"
                  tick={{ fill: '#8A93A6' }}
                  tickMargin={10}
                />
                <Tooltip 
                  contentStyle={customTooltipStyle}
                  labelFormatter={(label: any) => new Date(label as string | number).toLocaleString()}
                  formatter={(value: any) => [`${value}`, 'PRICE']}
                />
                <Line type="stepAfter" dataKey="price" stroke="#E8A33D" strokeWidth={2} dot={false} activeDot={{ r: 4, fill: '#E8A33D', stroke: '#171D2B' }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      <div className="border border-hairline bg-panel p-4 sm:p-6 rounded-sm">
        <h3 className="text-sm font-bold uppercase tracking-wider text-text-primary mb-6">Stock History</h3>
        {stockHistory.length === 0 ? (
          <div className="flex items-center justify-center h-64 bg-ink/30 border border-dashed border-hairline rounded-sm">
            <p className="text-neutral font-mono text-xs uppercase">NO_STOCK_DATA_RECORDED</p>
          </div>
        ) : (
          <div className="h-64 font-mono text-xs">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={stockHistory}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2A3244" vertical={false} />
                <XAxis 
                  dataKey="timestamp"
                  stroke="#8A93A6"
                  tick={{ fill: '#8A93A6' }}
                  tickFormatter={(tick) => new Date(tick).toLocaleDateString([], { month: 'short', day: 'numeric' })}
                  tickMargin={10}
                />
                <YAxis 
                  ticks={[0, 1]} 
                  tickFormatter={(tick) => tick === 1 ? 'IN_STOCK' : 'OUT_OF_STOCK'} 
                  domain={[0, 1]} 
                  stroke="#8A93A6"
                  tick={{ fill: '#8A93A6' }}
                  tickMargin={10}
                />
                <Tooltip 
                  contentStyle={customTooltipStyle}
                  labelFormatter={(label: any) => new Date(label as string | number).toLocaleString()}
                  formatter={(value: any) => [value ? 'IN_STOCK' : 'OUT_OF_STOCK', 'STATUS']}
                />
                <Line type="stepAfter" dataKey={(d) => d.in_stock ? 1 : 0} stroke="#3FAE8C" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </div>
  );
}
