<script lang="ts">
	import DrivingScreen from '$lib/components/DrivingScreen.svelte';
	import RoutePlanner from '$lib/components/RoutePlanner.svelte';
	import SelfDriving from '$lib/components/SelfDriving.svelte';
	import { startWebRTC, stopWebRTC } from '$lib/components/WebRTC';
	import { onDestroy, tick } from 'svelte';
	import { ws } from '$lib/components/WebSocketHandler.svelte';
	import { ip, STOP_SPEED } from '$lib/stores';

	let ip_textbox: string = localStorage.getItem('ip') ?? ''; // ?? means if null
	let activeIndex: number = 0;
	let videoStream: MediaStream | null = null;
	let routePlanner: RoutePlanner;

	type NavItem = { name: string; component: any };
	let headerItems: NavItem[] = [
		{ name: 'Human Driving', component: DrivingScreen },
		{ name: 'Route Planner', component: RoutePlanner },
		{ name: 'Self Driving', component: SelfDriving }
	];

	async function confirmIp() {
		localStorage.setItem('ip', ip_textbox);
		ip.set(ip_textbox);
		ws.connect($ip);
		await ws.waitForOpen();
		videoStream = await startWebRTC($ip);
	}

	async function switchTab(i: number) {
		activeIndex = i;
		if (headerItems[i].component === RoutePlanner) {
			await tick();
			routePlanner?.resizeMap();
		}

		stopMotors();
	}

	function stopMotors() {
    ws.send('motor', { left: STOP_SPEED, right: STOP_SPEED });
	}

	onDestroy(() => {
		stopWebRTC();
	});

	function onVisibilityChange() {
		if (document.hidden && activeIndex != 2) {
			stopMotors();
		}
	}

	document.addEventListener("visibilitychange", onVisibilityChange, false);
</script>

<svelte:head>
	<title>RC Tank Controller</title>
</svelte:head>

{#if $ip}
	<header>
		{#each headerItems as item, i}
			<button class="tab" class:active={activeIndex === i} on:click={() => switchTab(i)}>
				{item.name}
			</button>
		{/each}
	</header>
	<main>
		{#each headerItems as item, i}
			<div style="display: {activeIndex === i ? 'block' : 'none'}; width: 100%">
				{#if item.component === DrivingScreen}
					<DrivingScreen
						bind:stream={videoStream}
						{startWebRTC}
						{stopWebRTC}
						active={activeIndex === 0} />
				{:else if item.component === RoutePlanner}
					<RoutePlanner bind:this={routePlanner} />
				{:else}
					<svelte:component this={item.component} />
				{/if}
			</div>
		{/each}
	</main>
{:else}
	<main style="min-height: 100vh;">
		<div class="center">
			<div class="border black_background ip_picker">
				<input
					id={'ip_textbox'}
					bind:value={ip_textbox}
					placeholder="Tank IP"
					class="border focus:outline-none px-2 py-1 mt-4" />
				<button on:click={() => confirmIp()} class="px-4 py-2 cursor-pointer button px-2 py-1 mt-4">
					Confirm
				</button>
			</div>
		</div>
	</main>
{/if}
