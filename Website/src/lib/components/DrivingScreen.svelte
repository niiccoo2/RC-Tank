<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import cam_off_icon from '$lib/assets/cam_off.svg';

	type GPSResponse = {
		lat: number;
		lon: number;
		alt: number;
	};

	const MULTIPLIER: number = 1000;

	export let ip: string = '';
	export let stream: MediaStream | null = null;

	let animationFrame: number;
	let videoEl: HTMLVideoElement | null = null;
	let lastSendTime: number = 0;
	let status: string = 'Disconnected';
	let videoSetting = true;
	let ping: string = 'N/A';
	let roundedLeftSpeed: number = 0;
	let roundedRightSpeed: number = 0;
	let refreshTimeMs: number = 100;
	let leftSpeed: number = 0;
	let rightSpeed: number = 0;
	let trottle: number = 0;
	let stick: number = 0;
	let carMode: boolean = true;
	let FrSkyMode = true;
	let voltage: number = 0;
	let lights: boolean = false;
	let gpsInterval: NodeJS.Timeout;

	let gpsData: GPSResponse = {
		lat: 0,
		lon: 0,
		alt: 0,
	};

	async function updateGPSData() {
		if (ip) {
			const response = await fetch(`https://${ip}:5000/gps`, {
				method: 'GET',
				headers: { 'Content-Type': 'application/json' }
			});

			gpsData = await response.json();
		} else {
			return;
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

	async function pingAddress(ip: string) {
		let latency: number | null = null;
		let error: string | null = null;

		if (!ip) {
			console.log('IP is not set. pingAddress is returning.');
			return 'IP is not set.';
		}

		try {
			const start = performance.now();
			// request a small resource
			await fetch(ip, { method: 'HEAD', mode: 'no-cors' });
			const end = performance.now();
			latency = Math.round(end - start);
			error = null;
			return String(latency + 'ms');
		} catch (e) {
			latency = null;
			error = 'Error';
			return error;
		}
	}

	async function updatePing() {
		ping = await pingAddress(`https://${ip}:5000/health`);
	}

	async function handeLightSwitch(value: boolean) {
		if (value) {
			const response = await fetch(`https://${ip}:5000/lights_on`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' }
			});
		} else {
			const response = await fetch(`https://${ip}:5000/lights_off`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' }
			});
		}
	}

	function pollGamepad() {
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

		// left = applyExpo(left);
		// right = applyExpo(right);

		if (!ip) {
			console.log('IP is not set. sendCommand returning.');
			return;
		} else {
			// console.log(`Sending command to ${ip} - Left: ${left}, Right: ${right}`);
			try {
				const response = await fetch(`https://${ip}:5000/motor`, {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({ left, right })
				});
				const data = await response.json();
				voltage = data.voltage;
				status = 'Connected';
				return data;
			} catch (e) {
				status = 'Error';
				console.error(e);
			}
		}
	}

	onMount(() => {
		pollGamepad();
		sendCommand(0, 0); // Ensure motors are stopped on load and check connection

		updatePing();

		gpsInterval = setInterval(updateGPSData, 1000);

		setInterval(() => {
			updatePing();

			if (status === 'Disconnected') {
				sendCommand(0, 0);
			}
		}, 5000);
	});

	onDestroy(() => {
		if (animationFrame) {
			cancelAnimationFrame(animationFrame);
		}

		if (gpsInterval) {
			clearInterval(gpsInterval);
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
			<p>Lat: {gpsData.lat}</p>
			<p>Lon: {gpsData.lon}</p>
			<p>Alt: {gpsData.alt}</p>
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
				<p style="color: #FF0000; font-weight: bold;">{status}</p>
			{:else}
				<!-- svelte-ignore a11y-media-has-caption -->
				<video
					bind:this={videoEl}
					autoplay
					playsinline
					class="border black_background"
					width="640"
					height="480"></video>
				<p style="color: #00FF00; font-weight: bold;">{status}</p>
			{/if}
		{:else}
			<img
				class="border black_background"
				src={`${cam_off_icon}`}
				width="640"
				height="480"
				alt="Test Cam Feed" />
			{#if status === 'Connected'}
				<p style="color: #00FF00; font-weight: bold;">
					Camera Off | {status}
				</p>
			{:else if status === 'Error'}
				<p style="color: #FF0000; font-weight: bold;">
					Camera Off | {status}
				</p>
			{:else}
				<p style="color: #FF0000; font-weight: bold;">
					Camera Off | {status}
				</p>
			{/if}
		{/if}
	</div>

	<div class="side right">
		<div class="space-y-2">
			<div>
				<p class="info_card px-4 py-2">Ping: {ping}</p>
			</div>

			<div>
				<p class="info_card px-4 py-2">Battery Voltage: {voltage}v</p>
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

			<!-- <div class="info_card inline-flex items-center gap-3 px-3 py-2">
					<span class="py-1">Show Video:</span>
					<label class="switch m-0 ml-auto">
						<input type="checkbox" bind:checked={videoSetting} />
						<span class="slider round"></span>
					</label>
				</div> -->

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
