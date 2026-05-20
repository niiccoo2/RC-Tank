<script lang="ts">
	import {
		gpsData,
		ping,
		voltage,
		antiDoxx,
		roundedLeftSpeed,
		roundedRightSpeed,
		ntripStatus,
		heading
	} from '$lib/stores';
</script>

<div style="width: 48vw; height: 48vh; display: flex; align-items: flex-start; margin-top: 2vh;">
	<div style="display: flex; flex-direction: column;">
		<div class="info_card px-4 py-2">
			<strong>GPS Telemetry:</strong>
			<br />

			<div style="display: grid; grid-template-columns: 75px 1fr">
				{#if $antiDoxx}
					<span>Lat:</span> <span style="text-align: right;">0</span>
					<span>Lon:</span> <span style="text-align: right;">0</span>
					<span>Alt:</span> <span style="text-align: right;">0m</span>
				{:else}
					<span>Lat:</span> <span style="text-align: right;">{$gpsData.lat}</span>
					<span>Lon:</span> <span style="text-align: right;">{$gpsData.lon}</span>
					<span>Alt:</span> <span style="text-align: right;">{$gpsData.alt}m</span>
				{/if}
				<span>Fix Type:</span> <span style="text-align: right;">{$ntripStatus.fixType}D</span>
				<span>RTK:</span> <span style="text-align: right;">{$ntripStatus.rtk}</span>
				<span>Solving:</span> <span style="text-align: right;">{$ntripStatus.diffSoln}</span>
				<span>Age:</span> <span style="text-align: right;">{$ntripStatus.corrAge}s</span>
				<span>Accuracy:</span> <span style="text-align: right;">{$ntripStatus.hAcc}mm</span>
				<span>Sats:</span> <span style="text-align: right;">{$ntripStatus.sats}</span>
			</div>
		</div>
	</div>

	<div style="display: flex; flex-direction: column;">
		<div class="info_card px-4 py-2" style="display: grid; grid-template-columns: 100px 1fr">
			<span>Left Speed:</span> <span style="text-align: right;">{$roundedLeftSpeed}</span>
			<span>Right Speed:</span> <span style="text-align: right;">{$roundedRightSpeed}</span>
		</div>

		<div class="info_card px-4 py-2" style="display: grid; grid-template-columns: 100px 1fr">
			<span>Ping: </span> <span style="text-align: right;">{$ping}</span>
		</div>

		<div class="info_card px-4 py-2" style="display: grid; grid-template-columns: 150px 1fr">
			<span>Battery Voltage: </span> <span style="text-align: right;">{$voltage}v</span>
		</div>

		<div class="info_card px-4 py-2" style="display: grid; grid-template-columns: 150px 1fr">
			<span>Heading: </span> <span style="text-align: right;">{Math.round($heading)}°</span>
		</div>
	</div>
</div>
