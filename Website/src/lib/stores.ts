import { writable } from 'svelte/store';

export const status = writable('Disconnected');
export const ip = writable('');
