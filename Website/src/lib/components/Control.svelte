<script lang="ts" context="module">
	import L from 'leaflet';

	// Define the custom control class
	class SvelteControl extends L.Control {
		private el: HTMLElement;

		constructor(el: HTMLElement, position: L.ControlPosition) {
			super({ position });
			this.el = el;
		}

		onAdd() {
			return this.el;
		}

		// Leaflet expects onRemove, even if empty
		onRemove() {}
	}
</script>

<script lang="ts">
	import { getContext } from 'svelte';

	let classNames: string | undefined = undefined;
	export { classNames as class };

	// Use Leaflet's built-in position type
	export let position: L.ControlPosition;

	// Export the control instance so parents can bind to it
	export let control: SvelteControl | undefined = undefined;

	// Get the map instance from context
	const mapGetter = getContext('map') as () => L.Map;
	const map = mapGetter();

	function createControl(container: HTMLElement) {
		control = new SvelteControl(container, position).addTo(map);

		return {
			destroy() {
				if (control) {
					control.remove();
					control = undefined;
				}
			}
		};
	}
</script>

<!-- The outer div is hidden so it doesn't affect layout; 
     the inner div is moved into the Leaflet control container -->
<div style="display:none">
	<div use:createControl class={classNames}>
		{#if control}
			<slot {control} />
		{/if}
	</div>
</div>
