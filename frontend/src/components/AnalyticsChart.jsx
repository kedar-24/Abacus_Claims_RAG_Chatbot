import React, { useMemo, memo } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { PieChart as PieChartIcon, TrendingDown, AlertTriangle } from 'lucide-react';

const COLORS = ['#ef4444', '#f59e0b', '#3b82f6', '#10b981', '#8b5cf6'];

const AnalyticsChart = memo(({ claims }) => {
    const { denialData, statusData, total, denialRate } = useMemo(() => {
        if (!claims || claims.length === 0) {
            return { denialData: [], statusData: [], total: 0, denialRate: 0 };
        }

        const denialCounts = {};
        const statusCounts = {};

        claims.forEach(c => {
            const status = c.status || 'Unknown';
            statusCounts[status] = (statusCounts[status] || 0) + 1;

            if (c.status === 'Denied') {
                const reason = c.denial_reason || 'Unknown';
                denialCounts[reason] = (denialCounts[reason] || 0) + 1;
            }
        });

        const denied = statusCounts['Denied'] || 0;
        const totalCount = claims.length;
        const rate = totalCount > 0 ? ((denied / totalCount) * 100).toFixed(1) : 0;

        return {
            denialData: Object.entries(denialCounts)
                .map(([name, value]) => ({ name, value }))
                .sort((a, b) => b.value - a.value)
                .slice(0, 5),
            statusData: Object.entries(statusCounts)
                .map(([name, value]) => ({ name, value })),
            total: totalCount,
            denialRate: rate
        };
    }, [claims]);

    // Early return for empty data
    if (!claims || claims.length === 0 || total === 0) return null;

    const getStatusColor = (name) => {
        switch (name) {
            case 'Denied': return '#ef4444';
            case 'Approved': return '#10b981';
            case 'Pending': return '#f59e0b';
            default: return '#64748b';
        }
    };

    return (
        <div className="space-y-5">
            {/* Section Header */}
            <div className="flex items-center gap-2">
                <PieChartIcon size={16} className="text-cyan-400" />
                <h4 className="text-sm font-semibold text-white">Analytics Overview</h4>
            </div>

            {/* Denial Rate Card */}
            {Number(denialRate) > 0 && (
                <div className="bg-gradient-to-br from-red-500/10 to-red-600/5 border border-red-500/20 rounded-xl p-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-red-500/20 flex items-center justify-center">
                                <TrendingDown size={20} className="text-red-400" />
                            </div>
                            <div>
                                <div className="text-red-400 text-xs font-medium">Denial Rate</div>
                                <div className="text-white text-2xl font-bold">{denialRate}%</div>
                            </div>
                        </div>
                        <AlertTriangle size={24} className="text-red-400/50" />
                    </div>
                </div>
            )}

            {/* Status Distribution */}
            <div className="bg-slate-900/60 rounded-xl border border-slate-700/40 p-4">
                <h5 className="text-xs text-slate-400 mb-4 font-medium uppercase tracking-wide">Status Breakdown</h5>
                <div className="space-y-3">
                    {statusData.map((item, index) => {
                        const percentage = total > 0 ? ((item.value / total) * 100).toFixed(0) : 0;
                        const color = getStatusColor(item.name);
                        return (
                            <div key={index} className="space-y-2">
                                <div className="flex justify-between items-center text-sm">
                                    <div className="flex items-center gap-2">
                                        <div className="w-2 h-2 rounded-full" style={{ backgroundColor: color }} />
                                        <span className="text-slate-300 font-medium">{item.name}</span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <span className="text-white font-bold">{item.value}</span>
                                        <span className="text-slate-500 text-xs">({percentage}%)</span>
                                    </div>
                                </div>
                                <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                                    <div
                                        className="h-full rounded-full"
                                        style={{
                                            width: `${percentage}%`,
                                            backgroundColor: color
                                        }}
                                    />
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Denial Reasons */}
            {denialData.length > 0 && (
                <div className="bg-slate-900/60 rounded-xl border border-slate-700/40 p-4">
                    <h5 className="text-xs text-slate-400 mb-4 font-medium uppercase tracking-wide">Top Denial Reasons</h5>
                    <div className="space-y-2">
                        {denialData.map((item, index) => {
                            const maxValue = denialData[0]?.value || 1;
                            const widthPercent = (item.value / maxValue) * 100;
                            return (
                                <div key={index} className="flex items-center gap-3">
                                    <div className="w-24 text-xs text-slate-400 truncate" title={item.name}>
                                        {item.name}
                                    </div>
                                    <div className="flex-1 h-6 bg-slate-800 rounded-lg overflow-hidden relative">
                                        <div
                                            className="h-full rounded-lg flex items-center justify-end pr-2"
                                            style={{
                                                width: `${widthPercent}%`,
                                                backgroundColor: COLORS[index % COLORS.length]
                                            }}
                                        >
                                            <span className="text-white text-xs font-medium">{item.value}</span>
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}
        </div>
    );
});

AnalyticsChart.displayName = 'AnalyticsChart';

export default AnalyticsChart;
