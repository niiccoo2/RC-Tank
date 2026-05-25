import {
	ip,
	refreshTimeMs,
	roundedLeftSpeed,
	roundedRightSpeed,
	FrSkyMode,
	carMode,
	lights,
	status
} from '$lib/stores';
import { ws } from '$lib/components/WebSocketHandler.svelte';
import { get } from 'svelte/store';

let animationFrame: number;
let trottle: number = 0;
let stick: number = 0;
let button_states: boolean[] = new Array(16).fill(false);
let leftSpeed: number = 0;
let rightSpeed: number = 0;
let lastSendTime: number = 0;

const MULTIPLIER: number = 1000;

async function handleLightSwitch(value: boolean) {
	if (!ip) return;

	if (value) {
		// if on
		ws.send('lights', 100);
	} else {
		// if off
		ws.send('lights', 0);
	}
}

function carToTracks(trottle: number, stick: number) {
	let left: number;
	let right: number;
	const multiplier: number = 0.2;
	const cap: number = 1;

	if (stick != 0.0) {
		// Only cap the trottle if turning
		left = 0.9 * trottle + multiplier * stick;
		right = 0.9 * trottle - multiplier * stick;
	} else {
		left = trottle;
		right = trottle;
	}

	if (left > 1.0) {
		left = 1.0;
	} else if (left < -1.0) {
		left = -1.0;
	}

	if (right > 1.0) {
		right = 1.0;
	} else if (right < -1.0) {
		right = -1.0;
	}

	return [left, right];
}

async function sendCommand(left: number, right: number) {
	left = left * MULTIPLIER;
	right = right * MULTIPLIER;

	if (!document.hidden) {
		if (ws.send('motor', { left, right }) == false) {
			console.log('WS Send error');
			status.set('Error');
		} else if (get(status) !== 'Waypoint Mode') {
			// console.log('Setting status');
			status.set('Connected');
		}
	}
}

export function startPollingGamepad() {
	function pollGamepad() {
		const gamepads = navigator.getGamepads();
		const gamepad = gamepads[0];

		if (gamepad) {
			// console.log(gamepad.buttons[1]);

			if (gamepad.buttons[1].pressed && gamepad.buttons[1].pressed != button_states[1]) {
				// if B is pressed
				carMode.set(!get(carMode)); // toggle car mode
			}

			if (gamepad.buttons[5].pressed && gamepad.buttons[5].pressed != button_states[5]) {
				// if right bumper is pressed
				lights.set(!get(lights)); // toggle lights
				handleLightSwitch(get(lights));
			}

			if (carMode) {
				if (get(FrSkyMode)) {
					trottle = gamepad.axes[1]; // Left stick
					stick = gamepad.axes[3]; // Right stick

					if (Math.abs(trottle) < 0.1) trottle = 0;
				} else {
					trottle = -gamepad.axes[3]; // Right stick
					stick = gamepad.axes[0]; // Left stick

					// console.log('Throttle: ', -gamepad.axes[3]);
				}

				[leftSpeed, rightSpeed] = carToTracks(trottle, stick);
			} else {
				if (get(FrSkyMode)) {
					leftSpeed = gamepad.axes[1]; // Left stick
					rightSpeed = gamepad.axes[2]; // Right stick
				} else {
					leftSpeed = -gamepad.axes[1]; // Left stick
					rightSpeed = -gamepad.axes[3]; // Right stick
				}
			}

			roundedLeftSpeed.set(Number(leftSpeed.toFixed(2)));
			roundedRightSpeed.set(Number(rightSpeed.toFixed(2)));

			// Only send if x ms has passed
			const now = Date.now();
			if (now - lastSendTime > get(refreshTimeMs) && get(status) !== 'Waypoint Mode') {
				sendCommand(leftSpeed, rightSpeed);
				lastSendTime = now;
			}

			gamepad.buttons.forEach((item, index) => {
				button_states[index] = item.pressed;
			});
		}

		animationFrame = requestAnimationFrame(pollGamepad);
	}

	pollGamepad();
}
