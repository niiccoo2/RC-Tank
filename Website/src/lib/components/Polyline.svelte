<script lang="ts">
	import { createEventDispatcher, getContext, setContext, onDestroy } from 'svelte';

	import L from 'leaflet';
	import flush from 'just-flush';
	export let latLngs: L.LatLngExpression[];
	export let color: string | undefined = undefined;
	export let weight: number | undefined = undefined;
	export let opacity: number | undefined = undefined;
	export let pane: string | undefined = undefined;
	export let lineCap: string | undefined = undefined;
	export let lineJoin: string | undefined = undefined;
	export let fill: boolean | undefined = undefined;
	export let fillColor: string | undefined = undefined;
	export let className: string | undefined = undefined;
	export let dashArray: string | undefined = undefined;
	export let dashOffset: string | undefined = undefined;
	export let fillOpacity: number | undefined = undefined;
	export let fillRule: string | undefined = undefined;
	export let interactive = true;
	export let style: string | undefined = undefined;

	const dispatch = createEventDispatcher();

	let layerPane = pane || getContext('pane');
	let layerGroup = (getContext('layerGroup') as () => L.Map | L.LayerGroup)();

	let line: L.Polyline | undefined = new L.Polyline(
		latLngs,
		flush({
			interactive,
			className,
			pane: layerPane
		})
	)
		.on('click', (e) => dispatch('click', e))
		.on('mouseover', (e) => dispatch('mouseover', e))
		.on('mouseout', (e) => dispatch('mouseout', e))
		.addTo(layerGroup);

	setContext('layer', () => line);

	$: lineStyle = flush({
		color,
		className,
		weight,
		opacity,
		dashArray,
		dashOffset,
		lineCap,
		lineJoin,
		fill,
		fillColor,
		fillOpacity,
		fillRule
	});
	onDestroy(() => {
		line?.remove();
		line = undefined;
	});

	$: if (style && line) {
		line.getElement()?.setAttribute('style', style);
	}

	$: if (line) line.setStyle(lineStyle);

	$: if (line) {
		line.setLatLngs(latLngs);
		line.redraw();
	}
</script>

<slot />
