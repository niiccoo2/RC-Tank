<script lang="ts">
	import cam_off_icon from '$lib/assets/cam_off.svg';
	import { ip, status, gpsData, ping, voltage, antiDoxx, STOP_SPEED } from '$lib/stores';
	import RoutePlanner from '$lib/components/RoutePlanner.svelte';
	import Video from '$lib/components/Video.svelte';
	import DrivingScreen from '$lib/components/DrivingScreen.svelte';
	import SelfDriving from '$lib/components/SelfDriving.svelte';
	import { startWebRTC, stopWebRTC } from '$lib/components/WebRTC';
	import { onDestroy, tick } from 'svelte';
	import { ws } from '$lib/components/WebSocketHandler.svelte';

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
</script>

{#if $ip}
	<main>
		<div class="half horizontal_half_container">
			<div class="half">
				<!-- <p>TOP LEFT</p> -->
				<div style="height: 50vh; width: 50vw;">
					<Video bind:stream={videoStream} {startWebRTC} {stopWebRTC}></Video>
				</div>
			</div>
			<div class="half">
				<!-- <p>TOP RIGHT</p> -->
				<div class="border" style="width: 50vw; height: 50vh;">
					<RoutePlanner></RoutePlanner>
					<!-- Should add the border into the component -->
				</div>
			</div>
		</div>
		<div class="half horizontal_half_container">
			<div class="half">
				<p>BOTTOM LEFT</p>
			</div>
			<div class="half">
				<p>BOTTOM RIGHT</p>
			</div>
		</div>
	</main>
{:else}
	<main style="min-height: 100vh;">
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
