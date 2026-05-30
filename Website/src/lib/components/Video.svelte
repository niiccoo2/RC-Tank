<script lang="ts">
	import cam_off_icon from '$lib/assets/cam_off.svg';
	import { ip, status, videoSetting } from '$lib/stores';

	const MULTIPLIER: number = 1000;

	export let stream: MediaStream | null = null;
	export let startWebRTC: (ip: string) => Promise<MediaStream | null>;
	export let stopWebRTC: () => void;

	let videoEl: HTMLVideoElement | null = null;

	export async function toggleVideo() {
		if ($videoSetting == true) {
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
<div class="video-box">
	{#if $videoSetting}
		{#if !stream}
			<img class="video-frame border" src={`${cam_off_icon}`} alt="Test Cam Feed" />
		{:else}
			<!-- svelte-ignore a11y-media-has-caption -->
			<video bind:this={videoEl} autoplay playsinline class="video-frame border"> </video>
		{/if}
	{:else}
		<img class="video-frame border" src={`${cam_off_icon}`} alt="Test Cam Feed" />
	{/if}
</div>

<p style="color: {$status === 'Connected' ? '#00FF00' : '#FF0000'}; font-weight: bold;">
	{#if !$videoSetting}Camera Off |
	{/if}{$status}
</p>
