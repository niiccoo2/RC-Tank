<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { ssrModuleExportsKey } from 'vite/module-runner';

let animationFrame: number;
let lastSendTime: number = 0;

function pollGamepad() {
  const gamepads = navigator.getGamepads();
  const gamepad = gamepads[0];

  if (gamepad) {
    // Log to find your trigger axes
    console.log('Axes:', gamepad.axes);
    
    // Adjust these indices based on your controller
    leftSpeed = -gamepad.axes[1];   // Left trigger
    rightSpeed = -gamepad.axes[3];  // Right trigger
    
    // Only send if 50ms has passed
    const now = Date.now();
    if (now - lastSendTime > 50) {
      sendCommand(leftSpeed, rightSpeed);
      lastSendTime = now;
    }
  }
  

  animationFrame = requestAnimationFrame(pollGamepad);
}

onMount(() => {
  pollGamepad();
});

onDestroy(() => {
  if (animationFrame) {
    cancelAnimationFrame(animationFrame);
  }
});

  let leftSpeed: number = 0;
  let rightSpeed: number = 0;
  let status: string = 'disconnected';
  let ip: string = '192.168.1.161';

  async function sendCommand(left: number, right: number) {
    console.log(`Sending command - Left: ${left}, Right: ${right}`);
    try {
      const response = await fetch(`http://${ip}:5000/motor`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ left, right })
      });
      const data = await response.json();
      status = 'connected';
      return data;
    } catch (e) {
      status = 'error';
      console.error(e);
    }
  }

  function handleForward() {
    leftSpeed = 0.5;
    rightSpeed = 0.5;
    sendCommand(leftSpeed, rightSpeed);
  }

  function handleReverse() {
    leftSpeed = -0.5;
    rightSpeed = -0.5;
    sendCommand(leftSpeed, rightSpeed);
  }

  function handleLeft() {
    leftSpeed = -0.3;
    rightSpeed = 0.3;
    sendCommand(leftSpeed, rightSpeed);
  }

  function handleRight() {
    leftSpeed = 0.3;
    rightSpeed = -0.3;
    sendCommand(leftSpeed, rightSpeed);
  }

  function handleStop() {
    leftSpeed = 0;
    rightSpeed = 0;
    sendCommand(0, 0);
  }
</script>

<svelte:head>
	<title>RC Tank Controller</title>
</svelte:head>

<main>
    <p>Left Speed: {leftSpeed}, Right Speed: {rightSpeed}</p>
</main>

<style>
  :global(body) {
    margin: 0;
    padding: 0;
    font-family: 'Arial Black', sans-serif;
    font-weight: bold;
  }

  main {
    display: flex;
    background: #000000;
    min-height: 100vh;
    width: 100vw;
    color: #ffffff;
  }
</style>