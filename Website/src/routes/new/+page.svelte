<script>
	import cam_off_icon from '$lib/assets/cam_off.svg';
	import { ip, status, gpsData, ping, voltage, antiDoxx, STOP_SPEED } from '$lib/stores';
</script>

<main>
	<div class="half horizontal_half_container">
		<div class="half">
			<!-- <p>TOP LEFT</p> -->
			<!-- <video
				bind:this={videoEl}
				autoplay
				playsinline
				class="border black_background"
				width="640"
				height="480"></video> -->
			<img
				class="border black_background"
				src={`${cam_off_icon}`}
				width="640"
				height="480"
				alt="Test Cam Feed" />
			<p style="color: #00FF00; font-weight: bold;">{$status}</p>
		</div>
		<div class="half">
			<p>TOP RIGHT</p>
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
