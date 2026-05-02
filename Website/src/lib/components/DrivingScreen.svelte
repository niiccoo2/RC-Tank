<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import cam_off_icon from '$lib/assets/cam_off.svg';
	import { ws } from '$lib/components/WebSocketHandler.svelte';
	import { ip, status, gpsData, ping, voltage } from '$lib/stores';

	const MULTIPLIER: number = 1000;

	export let stream: MediaStream | null = null;
	export let startWebRTC: (ip: string) => Promise<MediaStream | null>;
	export let stopWebRTC: () => void;
	export let active: boolean = false;

	let animationFrame: number;
	let videoEl: HTMLVideoElement | null = null;
	let lastSendTime: number = 0;
	let videoSetting = true;
	let roundedLeftSpeed: number = 0;
	let roundedRightSpeed: number = 0;
	let refreshTimeMs: number = 100;
	let leftSpeed: number = 0;
	let rightSpeed: number = 0;
	let trottle: number = 0;
	let stick: number = 0;
	let carMode: boolean = true;
	let FrSkyMode = false;
	let lights: boolean = false;

	async function toggleVideo() {
		if (videoSetting == true) {
			stream = await startWebRTC($ip);
		} else {
			stopWebRTC();
		}
	}

	function changeRefresh(amount: number) {
		refreshTimeMs = refreshTimeMs + amount;
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

	async function updatePing() {
		try {
			let timeSent = await ws.twoWayMessage('ping', performance.now());

			if (typeof timeSent !== 'number') {
				console.error('ping did not return a number');
				return;
			}

			ping.set(`${Math.round(performance.now() - timeSent)}ms`);
		} catch (e) {
			console.error('Ping failed', e);
			ping.set('N/A');
		}
	}

	async function handeLightSwitch(value: boolean) {
		if (!ip) return;

		if (value) {
			// if on
			ws.send('lights', 100);
		} else {
			// if off
			ws.send('lights', 0);
		}
	}

	function pollGamepad() {
		if (!active) {
			animationFrame = requestAnimationFrame(pollGamepad);
			return;
		}

		const gamepads = navigator.getGamepads();
		const gamepad = gamepads[0];

		if (gamepad) {
			// console.log('Axes:', gamepad.axes);

			if (carMode) {
				if (FrSkyMode) {
					trottle = gamepad.axes[1]; // Left stick
					stick = gamepad.axes[3]; // Right stick

					if (Math.abs(trottle) < 0.1) trottle = 0;
				} else {
					trottle = -gamepad.axes[3]; // Right stick
					stick = gamepad.axes[0]; // Left stick
				}

				[leftSpeed, rightSpeed] = carToTracks(trottle, stick);
			} else {
				if (FrSkyMode) {
					leftSpeed = gamepad.axes[1]; // Left stick
					rightSpeed = gamepad.axes[2]; // Right stick
				} else {
					leftSpeed = -gamepad.axes[1]; // Left stick
					rightSpeed = -gamepad.axes[3]; // Right stick
				}
			}

			roundedLeftSpeed = Number(leftSpeed.toFixed(2));
			roundedRightSpeed = Number(rightSpeed.toFixed(2));

			// Only send if x ms has passed
			const now = Date.now();
			if (now - lastSendTime > refreshTimeMs) {
				sendCommand(leftSpeed, rightSpeed);
				lastSendTime = now;
			}
		}

		animationFrame = requestAnimationFrame(pollGamepad);
	}

	async function sendCommand(left: number, right: number) {
		left = left * MULTIPLIER;
		right = right * MULTIPLIER;

		if (!document.hidden) {
			if (ws.send('motor', { left, right }) == false) {
				console.log('WS Send error');
				status.set('Error');
			} else status.set('Connected');
		}
	}

	onMount(() => {
		pollGamepad();
		sendCommand(0, 0); // Ensure motors are stopped on load and check connection

		updatePing();

		setInterval(() => {
			updatePing();

			if ($status === 'Disconnected') {
				sendCommand(0, 0);
			}
		}, 1000);
	});

	onDestroy(() => {
		if (animationFrame) {
			cancelAnimationFrame(animationFrame);
		}
	});

	$: if (videoEl) {
		videoEl.srcObject = stream;
	}
</script>

<!-- <img src={`https://${ip}:5000/camera`} width="640" height="480" alt="RC Tank Camera Feed"> -->
<!-- Test Image -->
<div class="layout">
	<div class="side left">
		<div class="info_card px-4 py-2">
			<p>Left Speed: {roundedLeftSpeed}</p>
			<p>Right Speed: {roundedRightSpeed}</p>
		</div>

		<div class="info_card px-4 py-2">
			<p>Lat: {$gpsData.lat}</p>
			<p>Lon: {$gpsData.lon}</p>
			<p>Alt: {$gpsData.alt}</p>
		</div>
	</div>

	<div class="center">
		{#if videoSetting}
			{#if !stream}
				<img
					class="border black_background"
					src={`${cam_off_icon}`}
					width="640"
					height="480"
					alt="Test Cam Feed" />
				<p style="color: #FF0000; font-weight: bold;">{$status}</p>
			{:else}
				<!-- svelte-ignore a11y-media-has-caption -->
				<video
					bind:this={videoEl}
					autoplay
					playsinline
					class="border black_background"
					width="640"
					height="480"></video>
				<p style="color: #00FF00; font-weight: bold;">{$status}</p>
			{/if}
		{:else}
			<img
				class="border black_background"
				src={`${cam_off_icon}`}
				width="640"
				height="480"
				alt="Test Cam Feed" />
			{#if $status === 'Connected'}
				<p style="color: #00FF00; font-weight: bold;">
					Camera Off | {$status}
				</p>
			{:else if $status === 'Error'}
				<p style="color: #FF0000; font-weight: bold;">
					Camera Off | {$status}
				</p>
			{:else}
				<p style="color: #FF0000; font-weight: bold;">
					Camera Off | {$status}
				</p>
			{/if}
		{/if}
	</div>

	<div class="side right">
		<div class="space-y-2">
			<div>
				<p class="info_card px-4 py-2">Ping: {$ping}</p>
			</div>

			<div>
				<p class="info_card px-4 py-2">Battery Voltage: {$voltage}v</p>
			</div>
		</div>

		<div class="mt-2 space-y-2">
			<div class="info_card inline-flex items-center gap-3 px-3 py-2">
				<span class="py-1">Headlight:</span>
				<label class="switch m-0 ml-auto">
					<input type="checkbox" bind:checked={lights} on:change={() => handeLightSwitch(lights)} />
					<span class="slider round"></span>
				</label>
			</div>

			<div class="info_card inline-flex items-center gap-3 px-3 py-2">
				<span class="py-1">FrSky mode:</span>
				<label class="switch m-0 ml-auto">
					<input type="checkbox" bind:checked={FrSkyMode} />
					<span class="slider round"></span>
				</label>
			</div>

			<div class="info_card inline-flex items-center gap-3 px-3 py-2">
				<span class="py-1">Show Video:</span>
				<label class="switch m-0 ml-auto">
					<input type="checkbox" bind:checked={videoSetting} on:change={toggleVideo} />
					<span class="slider round"></span>
				</label>
			</div>

			<div class="info_card inline-flex items-center gap-3 px-3 py-2">
				<span class="py-1">Refresh:</span>
				<div class="inline-flex items-center gap-2 ml-auto">
					<button on:click={() => changeRefresh(-10)} class="cursor-pointer button px-2 py-1"
						>-</button>
					<p class="m-0">{refreshTimeMs}ms</p>
					<button on:click={() => changeRefresh(10)} class="cursor-pointer button px-2 py-1"
						>+</button>
				</div>
			</div>

			<div class="info_card inline-flex items-center gap-3 px-3 py-2">
				<span class="py-1">Car mode:</span>
				<label class="switch m-0 ml-auto">
					<input type="checkbox" bind:checked={carMode} />
					<span class="slider round"></span>
				</label>
			</div>
		</div>
	</div>
</div>
