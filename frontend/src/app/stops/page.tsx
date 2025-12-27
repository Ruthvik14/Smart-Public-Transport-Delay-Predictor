"use client";
import { useEffect, useState } from 'react';
import axios from 'axios';
import { Stop } from '@/lib/api';
import Link from 'next/link';

export default function StopsPage() {
    const [stops, setStops] = useState<Stop[]>([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');

    useEffect(() => {
        // Fetch nearby stops as a base list
        axios.get('http://localhost:8000/api/v1/stops/nearby?lat=40.4842&lon=-88.9937&radius=0.1')
            .then(res => setStops(res.data))
            .catch(console.error)
            .finally(() => setLoading(false));
    }, []);

    const filteredStops = stops.filter(s => s.stop_name.toLowerCase().includes(search.toLowerCase()));

    return (
        <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
            <header className="px-6 py-6 bg-slate-900 text-white shadow-xl">
                <div className="max-w-4xl mx-auto">
                    <Link href="/" className="text-slate-400 hover:text-white mb-4 block text-sm font-medium transition-colors">&larr; Back to Live Map</Link>
                    <h1 className="text-3xl font-black tracking-tight mb-2">Bus Stops</h1>
                    <p className="text-slate-400 text-lg">Search for a stop to view live schedules and delay predictions.</p>
                </div>
            </header>

            <main className="flex-1 max-w-4xl mx-auto w-full p-6 -mt-8">
                <div className="bg-white rounded-2xl shadow-xl border border-slate-100 overflow-hidden min-h-[500px] flex flex-col">
                    <div className="p-6 border-b border-slate-100 bg-white sticky top-0 z-10">
                        <div className="relative">
                            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                                <svg className="h-5 w-5 text-slate-400" viewBox="0 0 20 20" fill="currentColor">
                                    <path fillRule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clipRule="evenodd" />
                                </svg>
                            </div>
                            <input
                                type="text"
                                placeholder="Search by stop name or street..."
                                className="w-full pl-11 pr-4 py-3 bg-slate-50 border border-slate-200 text-slate-900 placeholder-slate-400 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all font-medium"
                                value={search}
                                onChange={(e) => setSearch(e.target.value)}
                            />
                        </div>
                    </div>

                    <div className="flex-1 overflow-y-auto max-h-[600px] p-2">
                        {loading && <div className="p-10 text-center text-slate-400 animate-pulse">Loading directory...</div>}

                        {!loading && filteredStops.length === 0 && (
                            <div className="p-10 text-center">
                                <p className="text-slate-500 font-medium">No nearby stops found.</p>
                                <p className="text-slate-400 text-sm mt-1">Try a different search term.</p>
                            </div>
                        )}

                        <div className="grid grid-cols-1 gap-2">
                            {filteredStops.map(stop => (
                                <Link key={stop.stop_id} href={`/stops/${stop.stop_id}`} className="block group">
                                    <div className="flex items-center justify-between p-4 hover:bg-blue-50 rounded-xl transition-all border border-transparent hover:border-blue-100 cursor-pointer">
                                        <div className="flex items-center gap-4">
                                            <div className="h-10 w-10 bg-slate-100 rounded-full flex items-center justify-center text-slate-400 group-hover:bg-blue-100 group-hover:text-blue-600 transition-colors">
                                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
                                            </div>
                                            <div>
                                                <h3 className="font-bold text-slate-800 text-base group-hover:text-blue-700 transition-colors">{stop.stop_name}</h3>
                                                <div className="flex items-center gap-2 mt-0.5">
                                                    <span className="text-xs font-mono bg-slate-100 text-slate-500 px-1.5 py-0.5 rounded border border-slate-200">#{stop.stop_code}</span>
                                                    <span className="text-xs text-slate-400">{stop.distance ? `${stop.distance.toFixed(2)} miles away` : 'Nearby'}</span>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="h-8 w-8 rounded-full bg-white border border-slate-200 flex items-center justify-center text-slate-300 group-hover:border-blue-200 group-hover:text-blue-500 transition-all opacity-0 group-hover:opacity-100 transform translate-x-2 group-hover:translate-x-0">
                                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
                                        </div>
                                    </div>
                                </Link>
                            ))}
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}
