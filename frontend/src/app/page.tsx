"use client";
import { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import Link from 'next/link';
import axios from 'axios';
import { getNearbyStops, Stop } from '@/lib/api';

// Dynamically import map to avoid SSR issues with Leaflet
const LiveMap = dynamic(() => import('@/components/LiveMap'), {
  loading: () => (
    <div className="flex items-center justify-center h-full bg-slate-50">
      <div className="animate-pulse flex flex-col items-center">
        <div className="h-12 w-12 bg-blue-200 rounded-full mb-4"></div>
        <p className="text-blue-500 font-medium">Loading Live Map...</p>
      </div>
    </div>
  ),
  ssr: false
});

export default function Home() {
  const [vehicles, setVehicles] = useState([]);
  const [stops, setStops] = useState<Stop[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchVehicles = async () => {
      try {
        const res = await axios.get('http://localhost:8000/api/v1/vehicles');
        setVehicles(res.data);
      } catch (e) {
        console.error(e);
      }
    };

    fetchVehicles();
    const interval = setInterval(fetchVehicles, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    // Center: Bloomington Normal
    getNearbyStops(40.4842, -88.9937)
      .then(setStops)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="flex h-screen flex-col bg-slate-50 font-sans">
      {/* Modern Header with Navigation */}
      <header className="px-4 py-3 bg-slate-900 shadow-xl z-50 flex justify-between items-center text-white shrink-0">
        <div className="flex items-center gap-2">
          <div className="bg-blue-600 p-1.5 rounded-lg">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
          </div>
          <div>
            <h1 className="text-base font-bold tracking-tight leading-tight">Connect Transit</h1>
          </div>
        </div>

        {/* Navigation Links - ALWAYS VISIBLE NOW */}
        <nav className="flex items-center gap-3 md:gap-6 text-xs md:text-sm font-medium text-slate-300">
          <Link href="/" className="text-white hover:text-blue-400 transition-colors">Live Map</Link>
          <Link href="/stops" className="hover:text-blue-400 transition-colors">Stops</Link>
          <Link href="/routes" className="hover:text-blue-400 transition-colors">Routes</Link>
          <Link href="/admin" className="hover:text-blue-400 transition-colors">Admin</Link>
        </nav>

        <div className="hidden sm:block text-[10px] font-bold bg-blue-600/20 text-blue-400 px-2 py-0.5 rounded-full border border-blue-500/30 uppercase tracking-wider">
          Beta
        </div>
      </header>

      <div className="flex-1 relative z-0 overflow-hidden">
        <LiveMap vehicles={vehicles} />

        {/* Fixed Info Panel - Changed to FIXED positioning to escape container clipping */}
        <div className="fixed top-20 right-4 z-[9999] w-72 md:w-80 flex flex-col gap-3 pointer-events-none">

          {/* Active Stats */}
          <div className="bg-white/95 backdrop-blur shadow-2xl rounded-xl border border-slate-200 p-4 pointer-events-auto">
            <div className="flex justify-between items-center">
              <h3 className="text-slate-500 text-xs font-bold uppercase tracking-wider">System Pulse</h3>
              <span className="flex h-2 w-2 rounded-full bg-green-500 animate-pulse"></span>
            </div>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-3xl font-black text-slate-800">{vehicles.length}</span>
              <span className="text-sm font-medium text-slate-500">Buses Active</span>
            </div>
          </div>

          {/* Nearby Stops List */}
          <div className="bg-white/95 backdrop-blur shadow-2xl rounded-xl border border-slate-200 overflow-hidden pointer-events-auto max-h-[60vh] flex flex-col">
            <div className="p-3 border-b border-slate-100 bg-slate-50 flex justify-between items-center">
              <h3 className="font-bold text-slate-700 text-sm">Nearby Stops</h3>
              <button className="text-xs text-blue-600 hover:underline">View All</button>
            </div>

            <div className="overflow-y-auto p-2 space-y-1">
              {loading && <div className="p-4 text-center text-xs text-slate-400">Scanning location...</div>}

              {!loading && stops.length === 0 && (
                <div className="p-6 text-center">
                  <p className="text-slate-800 font-medium text-sm">No stops found nearby</p>
                  <p className="text-slate-400 text-xs mt-1">Try zooming out.</p>
                </div>
              )}

              {stops.map(stop => (
                <Link key={stop.stop_id} href={`/stops/${stop.stop_id}`} className="block group">
                  <div className="flex justify-between items-center p-2 hover:bg-blue-50 rounded-lg transition-all border border-transparent hover:border-blue-100">
                    <div>
                      <div className="font-semibold text-slate-700 text-sm group-hover:text-blue-700">
                        {stop.stop_name}
                      </div>
                      <div className="text-[10px] text-slate-400 font-mono mt-0.5 uppercase">
                        Code: {stop.stop_code}
                      </div>
                    </div>
                    <div className="text-xs font-bold text-slate-500 bg-slate-100 px-2 py-1 rounded group-hover:bg-blue-600 group-hover:text-white transition-colors">
                      Go
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
