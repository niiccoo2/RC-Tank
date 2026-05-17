<script lang="ts">
	import {
		gpsData,
		ping,
		voltage,
		antiDoxx,
		roundedLeftSpeed,
		roundedRightSpeed
	} from '$lib/stores';
</script>

<div style="width: 100%; max-width: 48vw; height: 48vh; align-items: first;">
	<div class="info_card px-4 py-2">
		<div style="display: grid; grid-template-columns: 95px 1fr; text-align: left;">
			<span>Left Speed:</span> <span>{$roundedLeftSpeed}</span>
			<span>Right Speed:</span> <span>{$roundedRightSpeed}</span>
		</div>
	</div>

	<div class="info_card px-4 py-2">
		{#if $antiDoxx}
			<div style="display: grid; grid-template-columns: 35px 1fr; text-align: left;">
				<span>Lat:</span> <span>0</span>
				<span>Lon:</span> <span>0</span>
				<span>Alt:</span> <span>0m</span>
			</div>
		{:else}
			<div style="display: grid; grid-template-columns: 35px 1fr; text-align: left;">
				<span>Lat:</span> <span>{$gpsData.lat}</span>
				<span>Lon:</span> <span>{$gpsData.lon}</span>
				<span>Alt:</span> <span>{$gpsData.alt}m</span>
			</div>
		{/if}
	</div>

	<div>
		<p class="info_card px-4 py-2">Ping: {$ping}</p>
	</div>

	<div>
		<p class="info_card px-4 py-2">Battery Voltage: {$voltage}v</p>
	</div>
</div>
