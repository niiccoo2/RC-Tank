<script lang="ts">
	import {
		ip,
		refreshTimeMs,
		antiDoxx,
		videoSetting,
		FrSkyMode,
		carMode,
		lights
	} from '$lib/stores';
	import { ws } from '$lib/components/WebSocketHandler.svelte';
	// import { $state } from 'svelte';

	let { videoToggle } = $props();

	async function handeLightSwitch(e: Event) {
		lights.set((e.target as HTMLInputElement).checked);
		console.log('Got lights command', $lights);

		if (!$ip) return;

		if ($lights) {
			// if on
			ws.send('lights', 100);
		} else {
			// if off
			ws.send('lights', 0);
		}
	}

	function handleVideoToggle(e: Event) {
		videoSetting.set((e.target as HTMLInputElement).checked);
		videoToggle();
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
		<input type="checkbox" checked={$lights} onchange={(e) => handeLightSwitch(e)} />
		<span class="slider round"></span>
	</label>
</div>

<div class="info_card inline-flex items-center gap-3 px-3 py-2">
	<span class="py-1">FrSky mode:</span>
	<label class="switch m-0 ml-auto">
		<input
			type="checkbox"
			checked={$FrSkyMode}
			onchange={(e) => FrSkyMode.set((e.target as HTMLInputElement).checked)} />
		<span class="slider round"></span>
	</label>
</div>

<div class="info_card inline-flex items-center gap-3 px-3 py-2">
	<span class="py-1">Show Video:</span>
	<label class="switch m-0 ml-auto">
		<input type="checkbox" checked={$videoSetting} onchange={(e) => handleVideoToggle(e)} />
		<span class="slider round"></span>
	</label>
</div>

<div class="info_card inline-flex items-center gap-3 px-3 py-2">
	<span class="py-1">Refresh:</span>
	<div class="inline-flex items-center gap-2 ml-auto">
		<button
			onclick={() => refreshTimeMs.set($refreshTimeMs - 10)}
			class="cursor-pointer button px-2 py-1">-</button>
		<p class="m-0">{$refreshTimeMs}ms</p>
		<button
			onclick={() => refreshTimeMs.set($refreshTimeMs + 10)}
			class="cursor-pointer button px-2 py-1">+</button>
	</div>
</div>

<div class="info_card inline-flex items-center gap-3 px-3 py-2">
	<span class="py-1">Car mode:</span>
	<label class="switch m-0 ml-auto">
		<input
			type="checkbox"
			checked={$carMode}
			onchange={(e) => {
				carMode.set((e.target as HTMLInputElement).checked);
			}} />
		<span class="slider round"></span>
	</label>
</div>
