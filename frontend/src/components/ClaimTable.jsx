import React, { useMemo, memo, useState } from 'react';
import { CheckCircle, XCircle, AlertCircle, ChevronDown, ChevronUp, DollarSign, User, Stethoscope } from 'lucide-react';

const ClaimTable = memo(({ claims }) => {
    const [expanded, setExpanded] = useState(null);

    if (!claims || claims.length === 0) return null;

    const displayedClaims = claims;

    const formatAmount = (amount) => {
        const num = parseFloat(amount);
        return isNaN(num) ? amount : `$${num.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
    };

    const getStatusConfig = (status) => {
        switch (status?.toLowerCase()) {
            case 'approved':
                return {
                    bg: 'bg-emerald-500/10',
                    border: 'border-emerald-500/30',
                    text: 'text-emerald-400',
                    icon: <CheckCircle size={14} />
                };
            case 'denied':
                return {
                    bg: 'bg-red-500/10',
                    border: 'border-red-500/30',
                    text: 'text-red-400',
                    icon: <XCircle size={14} />
                };
            case 'pending':
                return {
                    bg: 'bg-amber-500/10',
                    border: 'border-amber-500/30',
                    text: 'text-amber-400',
                    icon: <AlertCircle size={14} />
                };
            default:
                return {
                    bg: 'bg-slate-500/10',
                    border: 'border-slate-500/30',
                    text: 'text-slate-400',
                    icon: null
                };
        }
    };

    return (
        <div className="bg-slate-900/60 rounded-2xl border border-slate-700/40 overflow-hidden">
            <div className="px-5 py-4 border-b border-slate-700/40 flex items-center justify-between">
                <h4 className="text-sm font-semibold text-white flex items-center gap-2">
                    <User size={16} className="text-cyan-400" />
                    Claims Details
                </h4>
                <span className="text-xs text-slate-500 bg-slate-800/60 px-3 py-1 rounded-full">
                    {claims.length} records
                </span>
            </div>

            <div className="overflow-auto max-h-[450px] custom-scrollbar">
                <div className="divide-y divide-slate-700/30">
                    {displayedClaims.map((claim, idx) => {
                        const statusConfig = getStatusConfig(claim.status);
                        const isExpanded = expanded === idx;

                        return (
                            <div key={claim.claim_id || idx} className="hover:bg-slate-800/30 transition-colors">
                                {/* Main Row */}
                                <div
                                    className="px-5 py-4 flex items-center gap-4 cursor-pointer"
                                    onClick={() => setExpanded(isExpanded ? null : idx)}
                                >
                                    {/* Status Badge */}
                                    <div className={`shrink-0 px-3 py-1.5 rounded-lg border ${statusConfig.bg} ${statusConfig.border} ${statusConfig.text} text-xs font-medium flex items-center gap-1.5`}>
                                        {statusConfig.icon}
                                        {claim.status}
                                    </div>

                                    {/* Patient & Provider */}
                                    <div className="flex-1 min-w-0">
                                        <div className="text-white font-medium text-sm truncate">{claim.patient_name}</div>
                                        <div className="text-slate-500 text-xs flex items-center gap-1 mt-0.5">
                                            <Stethoscope size={12} />
                                            {claim.provider_name} • {claim.diagnosis}
                                        </div>
                                    </div>

                                    {/* Amount */}
                                    <div className="shrink-0 text-right">
                                        <div className="text-cyan-400 font-mono font-semibold text-sm flex items-center gap-1">
                                            <DollarSign size={14} />
                                            {formatAmount(claim.claim_amount).replace('$', '')}
                                        </div>
                                        {claim.status === 'Denied' && claim.denial_reason && (
                                            <div className="text-red-400/70 text-xs mt-0.5">{claim.denial_reason}</div>
                                        )}
                                    </div>

                                    {/* Expand Icon */}
                                    <button className="shrink-0 text-slate-500 hover:text-white transition-colors p-1">
                                        {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                                    </button>
                                </div>

                                {/* Expanded Details */}
                                {isExpanded && (
                                    <div className="px-5 pb-4 pt-0">
                                        <div className="bg-slate-800/50 rounded-xl p-4 grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
                                            <div>
                                                <div className="text-slate-500 mb-1">Claim ID</div>
                                                <div className="text-white font-mono">{claim.claim_id?.slice(0, 8) || 'N/A'}...</div>
                                            </div>
                                            <div>
                                                <div className="text-slate-500 mb-1">Date</div>
                                                <div className="text-white">{claim.date || 'N/A'}</div>
                                            </div>
                                            <div>
                                                <div className="text-slate-500 mb-1">Specialty</div>
                                                <div className="text-white">{claim.specialty || 'N/A'}</div>
                                            </div>
                                            <div>
                                                <div className="text-slate-500 mb-1">Patient ID</div>
                                                <div className="text-white font-mono">{claim.patient_id?.slice(0, 8) || 'N/A'}...</div>
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
});

ClaimTable.displayName = 'ClaimTable';

export default ClaimTable;
