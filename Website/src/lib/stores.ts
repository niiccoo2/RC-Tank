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
export const ping = writable('N/A');
export const antiDoxx = writable(true);
export const ntripStatus = writable({
	fixType: 0,
	rtk: '',
	diffSoln: 0,
	corrAge: 0,
	hAcc: 0,
	sats: 0
});
export const heading = writable(0);
export const selfDriving = writable(0); // 0 = off, 1 = waypoint mode, 2 = ML testing mode

export const FrSkyMode = writable(false);
export const videoSetting = writable(true);
export const refreshTimeMs = writable(100);
export const carMode = writable(true);
export const lights = writable(false);
export const roundedLeftSpeed = writable(0);
export const roundedRightSpeed = writable(0);

export const STOP_SPEED: number = 12340000;
