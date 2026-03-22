<script lang="ts">
	import L from 'leaflet';
	import { getContext, setContext } from 'svelte';

	let classNames: string | undefined = undefined;
	export { classNames as class };

	export let marker: L.Marker<any> | undefined = undefined;

	export let width = 30;
	export let height = 30;
	export let latLng: L.LatLngExpression;

	const layerGroup = (getContext('layerGroup') as () => L.Map | L.LayerGroup)();
	setContext('layer', () => marker);

	function createMarker(markerElement: HTMLElement) {
		let icon = L.divIcon({
			html: markerElement,
			className: 'map-marker',
			iconSize: L.point(width, height)
		});
		marker = L.marker(latLng, { icon }).addTo(layerGroup);

		return {
			destroy() {
				if (marker) {
					marker.remove();
					marker = undefined;
				}
			}
		};
	}
</script>

<div class="hidden">
	<div use:createMarker class={classNames}>
		{#if marker}
			<slot />
		{/if}
	</div>
</div>
