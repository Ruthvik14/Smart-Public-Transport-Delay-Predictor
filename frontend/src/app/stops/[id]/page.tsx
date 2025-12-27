"use client";
import { useEffect, useState } from 'react';
import axios from 'axios';
import { Arrival } from '@/lib/api';
import Link from 'next/link';
import { useParams } from 'next/navigation';

export default function StopDetailsPage() {
    const { id } = useParams();
    const [arrivals, setArrivals] = useState<Arrival[]>([]);
    const [loading, setLoading] = useState(true);
    const [stopName, setStopName] = useState('Stop Details');

    useEffect(() => {
        // 1. Fetch Arrivals
        const fetchArrivals = async () => {
            try {
                const res = await axios.get(`http://localhost:8000/api/v1/stops/${id}/arrivals`);
                setArrivals(res.data);
                if (res.data.length > 0) {
                    // Hacky way to get stop name from first arrival headsign or we should fetch stop details separately
                    // For better UX, we'd fetch stop details from /stops/{id} endpoint
                }
            } catch (e) {
                console.error(e);
            } finally {
                setLoading(false);
            }
        };

        fetchArrivals();
        const interval = setInterval(fetchArrivals, 10000); // Poll every 10s
        return () => clearInterval(interval);
    }, [id]);

    return (
        <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
            <header className="px-6 py-4 bg-slate-900 text-white shadow-lg sticky top-0 z-10">
                <div className="max-w-3xl mx-auto flex items-center justify-between">
                    <Link href="/stops" className="text-slate-400 hover:text-white transition-colors text-sm font-medium flex items-center gap-1">
                        &larr; All Stops
                    </Link>
                    <h1 className="font-bold text-lg">Stop #{id}</h1>
                </div>
            </header>

            <main className="flex-1 max-w-3xl mx-auto w-full p-6">
                <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
                    <div className="p-6 border-b border-slate-100 bg-gradient-to-r from-blue-50 to-white">
                        <h2 className="text-2xl font-bold text-slate-800">Live Arrivals</h2>
                        <p className="text-slate-500 text-sm mt-1">Real-time predictions based on current traffic.</p>
                    </div>

                    {loading && <div className="p-10 text-center text-slate-400 animate-pulse">Loading arrival data...</div>}

                    {!loading && arrivals.length === 0 && (
                        <div className="p-10 text-center text-slate-500">
                            No buses scheduled for the next hour.
                        </div>
                    )}

                    <div className="divide-y divide-slate-100">
                        {arrivals.map((arrival, idx) => (
                            <div key={idx} className="p-4 hover:bg-slate-50 transition-colors flex justify-between items-center group">
                                <div>
                                    <div className="flex items-center gap-3">
                                        <span className="bg-blue-600 text-white font-bold px-2 py-1 rounded text-lg h-10 w-12 flex items-center justify-center">
                                            {arrival.route_id}
                                        </span>
                                        <div>
                                            <h3 className="font-bold text-slate-800 text-lg group-hover:text-blue-700 transition-colors">
                                                {arrival.headsign}
                                            </h3>
                                            <div className="flex items-center gap-2 mt-1">
                                                {arrival.status === 'LATE' && (
                                                    <span className="text-xs font-bold text-red-600 bg-red-50 px-2 py-0.5 rounded-full border border-red-100">LATE</span>
                                                )}
                                                {arrival.status === 'ON_TIME' && (
                                                    <span className="text-xs font-bold text-green-600 bg-green-50 px-2 py-0.5 rounded-full border border-green-100">ON TIME</span>
                                                )}
                                                <span className="text-xs text-slate-400">Trip: {arrival.trip_id}</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <div className="text-right">
                                    <div className="text-2xl font-black text-slate-800 tracking-tight">
                                        {arrival.delay_minutes > 1 ? (
                                            <span className="text-red-500">+{arrival.delay_minutes.toFixed(0)} min</span>
                                        ) : (
                                            <span className="text-green-600">Now</span>
                                        )}
                                    </div>
                                    <div className="text-xs text-slate-400 font-medium">
                                        {arrival.predicted_arrival ? 'Est. Arrival' : 'Scheduled'}
                                    </div>
                                    {arrival.probability_late_5min !== undefined && arrival.probability_late_5min > 0.5 && (
                                        <div className="text-[10px] text-orange-500 font-bold mt-1">
                                            {(arrival.probability_late_5min * 100).toFixed(0)}% Risk of Delay
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </main>
        </div>
    );
}
