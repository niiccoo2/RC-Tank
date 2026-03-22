<script lang="ts">
	import { createEventDispatcher, setContext } from 'svelte';
	import L from 'leaflet';
	import 'leaflet/dist/leaflet.css';
	export let height = '100%';
	export let width = '100%';

	// Must set either bounds, or view and zoom.
	export let bounds: L.LatLngBoundsExpression | undefined = undefined;
	export let view: L.LatLngExpression | undefined = undefined;
	export let zoom: number | undefined = undefined;
	let mapProp = undefined;
	export { mapProp as map };

	export const invalidateSize = () => map?.invalidateSize();

	const dispatch = createEventDispatcher();

	let map: L.Map | undefined;
	$: mapProp = map;

	export const getMap = () => map;
	setContext('layerGroup', getMap);
	setContext('layer', getMap);
	setContext('map', getMap);

	function createLeaflet(node: HTMLElement) {
		map = L.map(node)
		.on('zoom', (e) => dispatch('zoom', e))
		.on('click', (e) => dispatch('click', e));
		if (bounds) {
			map.fitBounds(bounds);
		} else if (view !== undefined && zoom !== undefined) {
			map.setView(view, zoom);
		}

		L.tileLayer(
    'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    {
        attribution:
            'Tiles © Esri — Source: Esri, Maxar, Earthstar Geographics, and the GIS User Community',
        maxZoom: 19
    }
).addTo(map);

		return {
			destroy() {
				if (map) {
					map.remove();
					map = undefined;
				}
			}
		};
	}

	$: if (map) {
		if (bounds) {
			map.fitBounds(bounds);
		} else if (view !== undefined && zoom !== undefined) {
			map.setView(view, zoom);
		}
	}
</script>

<div style="height:{height};width:{width}" use:createLeaflet>
	{#if map}
		<slot {map} />
	{/if}
</div>

<style>
	:global(.leaflet-control-container) {
		position: static;
	}
</style>
