<script lang="ts">
	import { ip, ping } from '$lib/stores';
	import RoutePlanner from '../lib/components/RoutePlanner.svelte';
	import Video from '$lib/components/Video.svelte';
	import { startWebRTC, stopWebRTC } from '$lib/components/WebRTC';
	import { ws } from '$lib/components/WebSocketHandler.svelte';
	import Telemetry from '$lib/components/Telemetry.svelte';
	import Settings from '$lib/components/Settings.svelte';
	import { startPollingGamepad } from '$lib/drivingController.svelte';
	import { onMount } from 'svelte';
	import { ntripStatus } from '$lib/stores';

	let videoRef: any = null;
	let routePlannerRef: any = null;
	let telemetryRef: any = null;
	let settingsRef: any = null;

	let ip_textbox: string = localStorage.getItem('ip') ?? ''; // ?? means if null
	let activeIndex: number = 0;
	let videoStream: MediaStream | null = null;
	let routePlanner: RoutePlanner;

	async function confirmIp() {
		localStorage.setItem('ip', ip_textbox);
		ip.set(ip_textbox);
		ws.connect($ip);
		await ws.waitForOpen();
		videoStream = await startWebRTC($ip);
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

	onMount(() => {
		startPollingGamepad();

		updatePing();

		setInterval(() => {
			// this runs every second
			updatePing();

			console.log($ntripStatus);

			// if ($status === 'Disconnected') { Don't know if we really need this... Is a pain to get working in the current config
			// 	sendCommand(STOP_SPEED, STOP_SPEED);
			// }
		}, 1000);
	});
</script>

{#if $ip}
	<main>
		<div class="horizontal_half_container">
			<div class="half video">
				<!-- <p>TOP LEFT</p> -->
				<Video bind:this={videoRef} bind:stream={videoStream} {startWebRTC} {stopWebRTC}></Video>
			</div>
			<div class="half map">
				<!-- <p>TOP RIGHT</p> -->
				<RoutePlanner bind:this={routePlannerRef}></RoutePlanner>
			</div>
		</div>
		<div class="horizontal_half_container">
			<div class="half">
				<!-- <p>BOTTOM LEFT</p> -->

				<Telemetry bind:this={telemetryRef}></Telemetry>
			</div>
			<div class="half">
				<!-- <p>BOTTOM RIGHT</p> -->
				<Settings
					bind:this={settingsRef}
					videoToggle={() => {
						videoRef?.toggleVideo();
					}}></Settings>
			</div>
		</div>
	</main>
{:else}
	<main style="min-height: 100vh; justify-content: center; align-content: center;">
		<div class="center">
			<div class="border black_background ip_picker">
				<input
					id={'ip_textbox'}
					bind:value={ip_textbox}
					placeholder="Tank IP"
					class="border focus:outline-none px-2 py-1 mt-4" />
				<button on:click={() => confirmIp()} class="px-4 py-2 cursor-pointer button px-2 py-1 mt-4">
					Confirm
				</button>
			</div>
		</div>
	</main>
{/if}
