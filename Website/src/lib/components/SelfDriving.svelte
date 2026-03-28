<script lang='ts'>
    
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

			<div class="info_card inline-flex items-center gap-3 px-3 py-2">
					<span class="py-1">Show Video:</span>
					<label class="switch m-0 ml-auto">
						<input type="checkbox" bind:checked={videoSetting} on:change={toggleVideo} />
						<span class="slider round"></span>
					</label>
			</div>

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
