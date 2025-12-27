"use client";

import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import axios from 'axios';

// Fix Leaflet icon issue
// @ts-ignore
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Component to recenter map
function MapUpdater({ center }: { center: [number, number] }) {
    const map = useMap();
    useEffect(() => {
        map.setView(center, map.getZoom());
    }, [center, map]);
    return null;
}

export default function LiveMap({ vehicles, onStopSelect }: { vehicles: any[], onStopSelect?: (id: string) => void }) {
    // Default center: Bloomington-Normal (approx)
    const defaultCenter: [number, number] = [40.4842, -88.9937];

    return (
        <MapContainer
            center={defaultCenter}
            zoom={13}
            style={{ height: '100%', width: '100%' }}
            className="z-0"
        >
            <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />

            {vehicles.map((v) => (
                <Marker
                    key={v.vehicle_id}
                    position={[v.latitude, v.longitude]}
                    title={`Route ${v.route_id}`}
                >
                    <Popup>
                        <div className="text-sm">
                            <strong>Route {v.route_id}</strong><br />
                            Bus #{v.vehicle_id}<br />
                            Speed: {v.speed ? v.speed.toFixed(1) : 0} m/s
                        </div>
                    </Popup>
                </Marker>
            ))}

            {/* Optional: Add stops here if we pass them in props */}

        </MapContainer>
    );
}
