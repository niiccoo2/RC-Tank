<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import '../app.css';

let animationFrame: number;
let lastSendTime: number = 0;
let leftSpeed: number = 0;
let rightSpeed: number = 0;
let status: string = 'Disconnected';
let ip: string = '192.168.1.161';
let videoSetting = true;
let ping: string = 'N/A';

async function pingAddress(ip: string) {
    let latency: number | null = null;
    let error: string | null = null;
    try {
      const start = performance.now();
      // We request a small resource (can be a 1x1 image or anything small)
      await fetch(ip, { method: 'HEAD', mode: 'no-cors' });
      const end = performance.now();
      latency = Math.round(end - start);
      error = null;
      return String(latency+' ms');
    } catch (e) {
      latency = null;
      error = 'Failed to reach server';
      return error;
    }
  }

async function updatePing() {
    ping = await pingAddress(`http://${ip}:5000/stats`);
}

function pollGamepad() {
  const gamepads = navigator.getGamepads();
  const gamepad = gamepads[0];

  if (gamepad) {
    // Log to find your trigger axes
    console.log('Axes:', gamepad.axes);
    
    // Adjust these indices based on your controller
    leftSpeed = -gamepad.axes[1];   // Left trigger
    rightSpeed = -gamepad.axes[3];  // Right trigger
    
    // Only send if x ms has passed
    const now = Date.now();
    if (now - lastSendTime > 10) {
      sendCommand(leftSpeed, rightSpeed);
      lastSendTime = now;
    }
  }

  animationFrame = requestAnimationFrame(pollGamepad);
}

async function sendCommand(left: number, right: number) {
console.log(`Sending command - Left: ${left}, Right: ${right}`);
try {
    const response = await fetch(`http://${ip}:5000/motor`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ left, right })
    });
    const data = await response.json();
    status = 'Connected';
    return data;
} catch (e) {
    status = 'Error';
    console.error(e);
}
}

onMount(() => {
    pollGamepad();
    sendCommand(0, 0); // Ensure motors are stopped on load and check connection

    updatePing();

    setInterval(() => {
        updatePing();
    }, 5000);
});

onDestroy(() => {
if (animationFrame) {
    cancelAnimationFrame(animationFrame);
}
});
</script>

<svelte:head>
	<title>RC Tank Controller</title>
</svelte:head>

<main>
    <!-- <img src={`http://${ip}:5000/camera`} width="640" height="480" alt="RC Tank Camera Feed"> -->
    <!-- Test Image -->
    <div class="layout">
        <div class="side left">
            <p>Left Speed: {leftSpeed}</p>
            <p>Right Speed: {rightSpeed}</p>
        </div>

        <div class="center">
            {#if videoSetting}
                {#if status !== 'Connected'}
                    <img class="border"src={`https://images.wallpapersden.com/image/wl-yellow-forest-landscape-4k-mountains_87481.jpg`} width="640" height="480" alt="Test Cam Feed">
                    <p style="color: #FF0000; font-weight: bold;">{status}</p>
                {:else}
                    <img class="border" src={`http://${ip}:5000/camera`} width="640" height="480" alt="RC Tank Camera Feed">
                    <p style="color: #00FF00;">{status}</p>
                {/if}
            {:else}
                <img class="border"src={`https://images.wallpapersden.com/image/wl-yellow-forest-landscape-4k-mountains_87481.jpg`} width="640" height="480" alt="Test Cam Feed">
                {#if status === 'Connected'}
                    <p style="color: #00FF00;">Camera Off | {status}</p>
                {:else if status === 'Error'}
                    <p style="color: #FF0000;">Camera Off | {status}</p>
                {:else}
                    <p style="color: #FF0000;">Camera Off | {status}</p>
                {/if}
            {/if}
        </div>

        <div class="side right">
            <div>
                <p class="border px-4 py-2">Ping: {ping}</p>
            </div>
            <div>
                <p class="border px-4 py-2">More</p>
            </div>
        </div>
    </div>
</main>