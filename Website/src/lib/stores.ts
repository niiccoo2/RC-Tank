import { writable, type Writable } from 'svelte/store';

type GPSResponse = {
	lat: number;
	lon: number;
	alt: number;
};

export const status = writable('Disconnected');
export const ip = writable('');
export const gpsData: Writable<GPSResponse> = writable({ lat: 0, lon: 0, alt: 0 });
export const voltage = writable(0);
