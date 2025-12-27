import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
    baseURL: API_BASE_URL,
});

export interface Stop {
    stop_id: string;
    stop_name: string;
    stop_lat: number;
    stop_lon: number;
    stop_code?: string;
    distance?: number;
}

export interface Arrival {
    trip_id: string;
    route_id: string;
    headsign: string;
    scheduled_arrival: string;
    predicted_arrival?: string;
    delay_minutes: number;
    status: 'ON_TIME' | 'LATE' | 'EARLY' | 'SCHEDULED';
    probability_late_5min?: number;
}

export const searchStops = async (query: string): Promise<Stop[]> => {
    const response = await api.get(`/stops/search?q=${query}`);
    return response.data;
};

export const getNearbyStops = async (lat: number, lon: number): Promise<Stop[]> => {
    const response = await api.get(`/stops/nearby?lat=${lat}&lon=${lon}`);
    return response.data;
};

export const getStopArrivals = async (stopId: string): Promise<Arrival[]> => {
    const response = await api.get(`/stops/${stopId}/arrivals`);
    return response.data;
};
