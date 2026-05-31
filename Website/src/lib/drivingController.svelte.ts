import {
	ip,
	refreshTimeMs,
	roundedLeftSpeed,
	roundedRightSpeed,
	FrSkyMode,
	carMode,
	lights,
	status,
	selfDriving
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

function handleAutoPilotToggle() {
	if (get(selfDriving)) {
		selfDriving.set(0);
		ws.send('self_driving_mode', 0);
		status.set('Connected');
	} else {
		selfDriving.set(1);
		ws.send('self_driving_mode', 1);
		status.set('Waypoint Mode');
	}
}

function handleMLToggle() {
	if (get(selfDriving)) {
		selfDriving.set(0);
		ws.send('self_driving_mode', 0);
		status.set('Connected');
	} else {
		selfDriving.set(2);
		ws.send('self_driving_mode', 2); // 2 for ML mode
		status.set('ML Mode');
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
		} else if (get(status) !== 'Waypoint Mode' || get(status) !== 'ML Mode') {
			// console.log('Setting status');
			status.set('Connected');
		}
	}
}

function isButtonPressed(gamepad: Gamepad | null, button: number) {
	if (gamepad)
		return (
			gamepad.buttons[button].pressed && gamepad.buttons[button].pressed != button_states[button]
		);
}

export function startPollingGamepad() {
	function pollGamepad() {
		const gamepads = navigator.getGamepads();
		const gamepad = gamepads[0];

		if (gamepad) {
			// console.log(gamepad.buttons[1]);

			if (isButtonPressed(gamepad, 1)) {
				// if B is pressed
				carMode.set(!get(carMode)); // toggle car mode
			}

			if (isButtonPressed(gamepad, 5)) {
				// if right bumper is pressed
				lights.set(!get(lights)); // toggle lights
				handleLightSwitch(get(lights));
			}

			if (isButtonPressed(gamepad, 2)) {
				// if x is pressed
				handleAutoPilotToggle();
			}

			if (isButtonPressed(gamepad, 3)) {
				// if y is pressed
				handleMLToggle();
			}

			if (get(carMode)) {
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
			if (
				now - lastSendTime > get(refreshTimeMs) &&
				get(status) !== 'Waypoint Mode' &&
				get(status) !== 'ML Mode'
			) {
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
