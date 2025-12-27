"use client";
import { useEffect, useState } from 'react';
import axios from 'axios';

export default function AdminDashboard() {
    const [metrics, setMetrics] = useState<any>(null);
    const [health, setHealth] = useState<any>(null);

    useEffect(() => {
        axios.get('http://localhost:8000/api/v1/admin/metrics').then(r => setMetrics(r.data)).catch(console.error);
        axios.get('http://localhost:8000/api/v1/admin/health').then(r => setHealth(r.data)).catch(console.error);
    }, []);

    if (!metrics) return <div className="p-8">Loading Admin Dashboard...</div>;

    return (
        <div className="p-8 bg-gray-50 min-h-screen">
            <h1 className="text-3xl font-bold mb-6">System Admin</h1>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                {/* Health Cards */}
                <div className="bg-white p-6 rounded-xl shadow-sm">
                    <h3 className="text-gray-500 text-sm uppercase">System Status</h3>
                    <div className="mt-2 flex items-center gap-2">
                        <div className={`w-3 h-3 rounded-full ${health?.database === 'ok' ? 'bg-green-500' : 'bg-red-500'}`}></div>
                        <span>Database: {health?.database}</span>
                    </div>
                    <div className="mt-2 flex items-center gap-2">
                        <div className={`w-3 h-3 rounded-full ${health?.redis === 'ok' ? 'bg-green-500' : 'bg-red-500'}`}></div>
                        <span>Redis: {health?.redis}</span>
                    </div>
                </div>

                {/* Real-time Card */}
                <div className="bg-white p-6 rounded-xl shadow-sm">
                    <h3 className="text-gray-500 text-sm uppercase">Live Traffic</h3>
                    <div className="text-4xl font-bold text-blue-600 mt-2">{metrics.realtime.active_vehicles}</div>
                    <p className="text-sm text-gray-400">Active Vehicles</p>
                </div>

                {/* Engagement Card */}
                <div className="bg-white p-6 rounded-xl shadow-sm">
                    <h3 className="text-gray-500 text-sm uppercase">Alerts</h3>
                    <div className="flex justify-between mt-2">
                        <div>
                            <span className="text-2xl font-bold">{metrics.engagement.subscriptions}</span>
                            <span className="block text-xs text-gray-400">Active Subs</span>
                        </div>
                        <div>
                            <span className="text-2xl font-bold text-red-500">{metrics.engagement.alerts_triggered}</span>
                            <span className="block text-xs text-gray-400">Triggered Events</span>
                        </div>
                    </div>
                </div>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-sm">
                <h3 className="text-lg font-bold mb-4">Static Data Stats</h3>
                <div className="grid grid-cols-3 gap-4 text-center">
                    <div className="p-4 bg-gray-50 rounded">
                        <div className="text-xl font-bold">{metrics.counts.stops}</div>
                        <div className="text-xs uppercase text-gray-500">Stops</div>
                    </div>
                    <div className="p-4 bg-gray-50 rounded">
                        <div className="text-xl font-bold">{metrics.counts.routes}</div>
                        <div className="text-xs uppercase text-gray-500">Routes</div>
                    </div>
                    <div className="p-4 bg-gray-50 rounded">
                        <div className="text-xl font-bold">{metrics.counts.trips}</div>
                        <div className="text-xs uppercase text-gray-500">Trips</div>
                    </div>
                </div>
            </div>
        </div>
    );
}
