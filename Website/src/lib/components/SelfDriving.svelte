<script lang="ts">
	import { status, voltage, ping, gpsData } from '$lib/stores';
	import { ws } from '$lib/components/WebSocketHandler.svelte';

	function startSelfDriving() {
		ws.send('self_driving_mode', 1);
		status.set('Waypoint Mode');
	}

	function stopSelfDriving() {
		ws.send('self_driving_mode', 0);
		status.set('Connected');
	}

	let val: boolean = false;
</script>

<!-- <img src={`https://${ip}:5000/camera`} width="640" height="480" alt="RC Tank Camera Feed"> -->
<!-- Test Image -->
<div class="layout">
	<div class="side left">
		<div class="info_card px-4 py-2">
			<button on:click={startSelfDriving} class="cursor-pointer button px-2 py-1">Start</button>
			<button on:click={stopSelfDriving} class="cursor-pointer button px-2 py-1">Stop</button>
		</div>

		<div class="info_card px-4 py-2">
			<p>Lat: {$gpsData.lat}</p>
			<p>Lon: {$gpsData.lon}</p>
			<p>Alt: {$gpsData.alt}</p>
		</div>
	</div>

	<div class="center">
		<img class="border black_background" src={``} width="640" height="480" alt="Test Cam Feed" />

		<p style="color: #fcad03; font-weight: bold;">
			{$status}
		</p>
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
					<input type="checkbox" bind:checked={val} on:change={() => {}} />
					<span class="slider round"></span>
				</label>
			</div>

			<div class="info_card inline-flex items-center gap-3 px-3 py-2">
				<span class="py-1">FrSky mode:</span>
				<label class="switch m-0 ml-auto">
					<input type="checkbox" bind:checked={val} />
					<span class="slider round"></span>
				</label>
			</div>

			<div class="info_card inline-flex items-center gap-3 px-3 py-2">
				<span class="py-1">Show Video:</span>
				<label class="switch m-0 ml-auto">
					<input type="checkbox" bind:checked={val} on:change={() => {}} />
					<span class="slider round"></span>
				</label>
			</div>

			<div class="info_card inline-flex items-center gap-3 px-3 py-2">
				<span class="py-1">Refresh:</span>
				<div class="inline-flex items-center gap-2 ml-auto">
					<button on:click={() => {}} class="cursor-pointer button px-2 py-1">-</button>
					<p class="m-0">0ms</p>
					<button on:click={() => {}} class="cursor-pointer button px-2 py-1">+</button>
				</div>
			</div>

			<div class="info_card inline-flex items-center gap-3 px-3 py-2">
				<span class="py-1">Car mode:</span>
				<label class="switch m-0 ml-auto">
					<input type="checkbox" bind:checked={val} />
					<span class="slider round"></span>
				</label>
			</div>
		</div>
	</div>
</div>
