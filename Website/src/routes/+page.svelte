<script lang="ts">
	import DrivingScreen from '$lib/components/DrivingScreen.svelte';
	import Something from '$lib/components/Something.svelte';
	import { type Component } from 'svelte';

	let ip: string = 'test';
	let ip_textbox: string = '';
	let activeIndex: number = 0;

	type NavItem = { name: string; component: Component };
	let headerItems: NavItem[] = [
		{ name: 'Human Driving', component: DrivingScreen },
		{ name: 'Something Else', component: Something }
	];

	function confirmIp() {
		// NEED TO START WRBRTC OR THINGS WONT WORK
		ip = ip_textbox;
	}
</script>

<svelte:head>
	<title>RC Tank Controller</title>
</svelte:head>

{#if ip}
	<header>
		{#each headerItems as item, i}
			<button class="tab" class:active={activeIndex === i} on:click={() => (activeIndex = i)}>
				{item.name}
			</button>
		{/each}
	</header>
	<main>
		<!-- <DrivingScreen {ip} bind:this={drivingScreen}></DrivingScreen> -->
		{#each headerItems as item, i}
			<div style="display: {activeIndex === i ? 'block' : 'none'}">
				<svelte:component this={item.component} {ip} />
			</div>
		{/each}
	</main>
{:else}
	<main>
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
