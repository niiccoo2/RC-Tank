<script lang="ts">
	import L, { latLng } from 'leaflet';
	import Leaflet from './Leaflet.svelte';
	import Control from './Control.svelte';
	import Marker from './Marker.svelte';
	import Popup from './Popup.svelte';
	import Polyline from './Polyline.svelte';
	import MapToolbar from './MapToolbar.svelte';
	let map: L.Map;

	export let ip: string = '';

	let markerLocations: { ID: number, latLng: [number, number] }[] = [];
	let markerIdCount: number = 0;
	let initialView: [number, number] = [0, 0];

	$: lines = markerLocations.slice(1).map((latLng, i) => {
		let prev = markerLocations[i];
		return {
			latLngs: [prev.latLng, latLng.latLng],
			color: "red"
		};
	});

	navigator.geolocation.getCurrentPosition(setInitialView);

	let eye = true;
	let showLines = true;

	export function resizeMap() {
		if (map) {
			map.invalidateSize();
		}
	}

	function setInitialView(geolocationPosition: GeolocationPosition) {
		initialView = [geolocationPosition.coords.latitude, geolocationPosition.coords.longitude];
	}

	function resetMapView() {
		map.setView(initialView, 15);
	}

	function handleMapClick(event: CustomEvent<L.LeafletMouseEvent>) {
		const { lat, lng } = event.detail.latlng;
		console.log(`Map clicked at ${lat}, ${lng}. ID: ${markerIdCount}`);
		markerLocations = [...markerLocations, { ID: markerIdCount, latLng: [lat, lng] }];
		markerIdCount++;
	} 

	function clearMarkers() {
		markerLocations = [];
		markerIdCount = 0;
	}

	function removeLocationFromArray(ID: number) {
		markerLocations = markerLocations.filter((p) => p.ID !== ID);
	}

	async function sendWaypointsToTank() {
		console.log('Sending locations:', markerLocations);
		
		// send all waypoint data to tank here

		try {
				const response = await fetch(`https://${ip}:5000/motor`, {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify(markerLocations)
				});
			} catch (e) {
				console.error(e);
			}
	}
</script>

<svelte:window on:resize={resizeMap} />

<div style="height: 94vh; width: 100%;">
	<Leaflet bind:map on:click={handleMapClick} view={initialView} zoom={15}>
		<Control position="topright">
			<MapToolbar bind:eye bind:lines={showLines} on:click-reset={resetMapView} on:click-send={sendWaypointsToTank} />
		</Control>

		{#if eye}
			{#each markerLocations as location (location.ID)}
				<Marker latLng={location.latLng} width={30} height={30}>
					<svg
						style="width:30px;height:30px"
						fill="none"
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="0"
						viewBox="0 0 24 24"
						stroke="currentColor"
						><circle r="2" cx="12" cy="12" fill="red" /></svg>

					<Popup>
						<button on:click|stopPropagation={() => {removeLocationFromArray(location.ID)}} class="remove_waypoint_button">Remove</button>
					</Popup>
				</Marker>
			{/each}
		{/if}

		{#if showLines}
			{#each lines as { latLngs, color }}
				<Polyline {latLngs} {color} opacity={0.5} />
			{/each}
		{/if}
	</Leaflet>
</div>
