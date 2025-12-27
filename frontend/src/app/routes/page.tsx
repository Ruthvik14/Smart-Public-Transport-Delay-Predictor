"use client";
import { useEffect, useState } from 'react';
import axios from 'axios';
import Link from 'next/link';

interface Route {
    route_id: string;
    route_short_name: string;
    route_long_name: string;
}

export default function RoutesPage() {
    const [routes, setRoutes] = useState<Route[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // We haven't built getAllRoutes yet, but let's assume we add it or use the endpoints we have.
        // Checking endpoints.py... oh wait, I need to add /routes endpoint too if it's missing. 
        // Wait, endpoints.py has `get_routes`! (See Step 459).

        axios.get('http://localhost:8000/api/v1/routes')
            .then(res => setRoutes(res.data))
            .catch(console.error)
            .finally(() => setLoading(false));
    }, []);

    return (
        <div className="min-h-screen bg-slate-50 p-6 flex flex-col gap-6">
            <header>
                <Link href="/" className="text-blue-600 hover:underline text-sm mb-2 block">&larr; Back to Map</Link>
                <h1 className="text-3xl font-bold text-slate-900">Bus Routes</h1>
                <p className="text-slate-500">Select a route to view its path and active buses.</p>
            </header>

            {loading && <div className="text-center py-10">Loading routes...</div>}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {routes.map(route => (
                    <div key={route.route_id} className="bg-white p-6 rounded-xl shadow-sm border border-slate-100 flex items-center gap-4">
                        <div className="bg-blue-600 text-white h-12 w-12 flex items-center justify-center rounded-lg font-black text-xl shadow-md">
                            {route.route_short_name}
                        </div>
                        <div>
                            <h3 className="font-bold text-slate-800 text-lg">{route.route_long_name}</h3>
                            <span className="text-slate-400 text-sm">Route ID: {route.route_id}</span>
                        </div>
                    </div>
                ))}
                {!loading && routes.length === 0 && (
                    <div className="col-span-full text-center text-slate-400 py-10">
                        No routes found.
                    </div>
                )}
            </div>
        </div>
    );
}
