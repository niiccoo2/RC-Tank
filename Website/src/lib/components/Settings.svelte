<script lang="ts">
	import { ip, status, gpsData, ping, voltage, antiDoxx, STOP_SPEED } from '$lib/stores';
	import { ws } from '$lib/components/WebSocketHandler.svelte';
	import Video from '$lib/components/Video.svelte';

	let videoRef: any = null;

	let videoSetting = true;
	let refreshTimeMs: number = 100;
	let carMode: boolean = true;
	let FrSkyMode = false;
	let lights: boolean = false;

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

	function handleVideoToggle() {
		videoRef.toggleVideo();
	}

	function changeRefresh(amount: number) {
		refreshTimeMs = refreshTimeMs + amount;
	}
</script>

<div class="info_card inline-flex items-center gap-3 px-3 py-2">
	<span class="py-1">Anti doxx:</span>
	<label class="switch m-0 ml-auto">
		<input type="checkbox" bind:checked={$antiDoxx} />
		<span class="slider round"></span>
	</label>
</div>

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
		<input type="checkbox" bind:checked={videoSetting} on:change={handleVideoToggle} />
		<span class="slider round"></span>
	</label>
</div>

<div class="info_card inline-flex items-center gap-3 px-3 py-2">
	<span class="py-1">Refresh:</span>
	<div class="inline-flex items-center gap-2 ml-auto">
		<button on:click={() => changeRefresh(-10)} class="cursor-pointer button px-2 py-1">-</button>
		<p class="m-0">{refreshTimeMs}ms</p>
		<button on:click={() => changeRefresh(10)} class="cursor-pointer button px-2 py-1">+</button>
	</div>
</div>

<div class="info_card inline-flex items-center gap-3 px-3 py-2">
	<span class="py-1">Car mode:</span>
	<label class="switch m-0 ml-auto">
		<input type="checkbox" bind:checked={carMode} />
		<span class="slider round"></span>
	</label>
</div>
