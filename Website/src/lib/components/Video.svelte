<script lang="ts">
	import cam_off_icon from '$lib/assets/cam_off.svg';
	import { ip, status } from '$lib/stores';

	const MULTIPLIER: number = 1000;

	export let stream: MediaStream | null = null;
	export let startWebRTC: (ip: string) => Promise<MediaStream | null>;
	export let stopWebRTC: () => void;

	let videoEl: HTMLVideoElement | null = null;
	let videoSetting = true;

	async function toggleVideo() {
		if (videoSetting == true) {
			stream = await startWebRTC($ip);
		} else {
			stopWebRTC();
		}
	}

	$: if (videoEl) {
		videoEl.srcObject = stream;
	}
</script>

<!-- <img src={`https://${ip}:5000/camera`} width="640" height="480" alt="RC Tank Camera Feed"> -->
<!-- Test Image -->
{#if videoSetting}
	{#if !stream}
		<img class="border black_background" src={`${cam_off_icon}`} alt="Test Cam Feed" />
		<p style="color: #FF0000; font-weight: bold;">{$status}</p>
	{:else}
		<!-- svelte-ignore a11y-media-has-caption -->
		<video bind:this={videoEl} autoplay playsinline class="border black_background"></video>
		<p style="color: #00FF00; font-weight: bold;">{$status}</p>
	{/if}
{:else}
	<img class="border black_background" src={`${cam_off_icon}`} alt="Test Cam Feed" />
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
