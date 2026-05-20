<script lang="ts">
	import L, { latLng } from 'leaflet';
	import Leaflet from './Leaflet.svelte';
	import Control from './Control.svelte';
	import Marker from './Marker.svelte';
	import Popup from './Popup.svelte';
	import Polyline from './Polyline.svelte';
	import MapToolbar from './MapToolbar.svelte';
	import { ws } from './WebSocketHandler.svelte';
	import { gpsData } from '$lib/stores';
	import { onMount } from 'svelte';
	let map: L.Map;

	let markerLocations: { ID: number; latLng: [number, number] }[] = [];
	let markerIdCount: number = 0;
	let initialView: [number, number] = [0, 0];

	$: lines = markerLocations.slice(1).map((latLng, i) => {
		let prev = markerLocations[i];
		return {
			latLngs: [prev.latLng, latLng.latLng],
			color: 'red'
		};
	});

	let eye = true;
	let showLines = true;

	$: liveLocation = { lat: $gpsData.lat, lng: $gpsData.lon };

	export function resizeMap() {
		if (map) {
			map.invalidateSize();
		}
	}

	function resetMapView() {
		map.setView(initialView, 18);
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

		ws.send('waypoint_data', markerLocations);
	}

	onMount(() => {
		const unsubscribe = gpsData.subscribe((data) => {
			if (data.lat !== 0 && data.lon !== 0) {
				initialView = [data.lat, data.lon];
				unsubscribe(); // Unsubscribe immediately
			}
		});
		return unsubscribe;
	});
</script>

<svelte:window on:resize={resizeMap} />

<div class="border" style="height: 48vh; width: 100%;">
	<Leaflet bind:map on:click={handleMapClick} view={initialView} zoom={18}>
		<Control position="topright">
			<MapToolbar
				bind:eye
				bind:lines={showLines}
				on:click-reset={resetMapView}
				on:click-send={sendWaypointsToTank} />
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
						stroke="currentColor"><circle r="2" cx="12" cy="12" fill="red" /></svg>

					<Popup>
						<button
							on:click|stopPropagation={() => {
								removeLocationFromArray(location.ID);
							}}
							class="remove_waypoint_button">Remove</button>
					</Popup>
				</Marker>
			{/each}
		{/if}

		<Marker latLng={liveLocation} width={30} height={30}>
			<svg
				style="width:30px;height:30px"
				fill="none"
				stroke-linecap="round"
				stroke-linejoin="round"
				stroke-width="0"
				viewBox="0 0 12 12"
				stroke="currentColor">
				<circle r="2" cx="6" cy="6" fill="blue" fill-opacity="1" />
			</svg>
			<Popup>
				<p>Tank</p>
			</Popup>
		</Marker>

		{#if showLines}
			{#each lines as { latLngs, color }}
				<Polyline {latLngs} {color} opacity={0.5} />
			{/each}
		{/if}
	</Leaflet>
</div>
