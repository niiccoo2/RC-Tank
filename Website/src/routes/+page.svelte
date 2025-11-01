<script lang="ts">
import { onMount, onDestroy } from 'svelte';
import cam_off_icon from '$lib/assets/cam_off.svg';

let animationFrame: number;
let lastSendTime: number = 0;
let status: string = 'Disconnected';
// let ip: string = '192.168.1.161';
let ip: string = '';
let ip_textbox: string = '';
let videoSetting = true;
let ping: string = 'N/A';
let roundedLeftSpeed: number = 0;
let roundedRightSpeed: number = 0;
let refreshTimeMs: number = 100;
let leftSpeed: number = 0;
let rightSpeed: number = 0;
let trottle: number = 0;
let stick: number = 0;
let carMode: boolean = true;

function changeRefresh(amount: number) {
    refreshTimeMs = refreshTimeMs + amount;
}

function carToTracks(trottle: number, stick: number) {
    let left: number;
    let right: number;
    const multiplier: number = .6

    if (stick != 0.00) { // Only cap the trottle if turning
        left = .6*trottle+(multiplier*stick)
        right = .6*trottle-(multiplier*stick)
    } else {
        left = trottle
        right = trottle
    }

    if (left > 1.00) {
        left = 1.00
    } else if (left < -1.00) {
        left = -1.00
    }
        
    if (right > 1.00) {
        right = 1.00
    } else if (right < -1.00) {
        right = -1.00
    }
    
    return [left, right]
}

async function pingAddress(ip: string) {
    let latency: number | null = null;
    let error: string | null = null;

    if (!ip) {
        console.log("IP is not set. pingAddress is returning.")
        return "IP is not set."
    }

    try {
      const start = performance.now();
      // request a small resource
      await fetch(ip, { method: 'HEAD', mode: 'no-cors' });
      const end = performance.now();
      latency = Math.round(end - start);
      error = null;
      return String(latency+'ms');
    } catch (e) {
      latency = null;
      error = 'Error';
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
    console.log('Axes:', gamepad.axes);
    
    if (carMode) {
        // Using sticks for now but will change to triggers soon
        trottle = -gamepad.axes[3];  // Right stick
        stick = gamepad.axes[0];   // Left stick

        [leftSpeed, rightSpeed] = carToTracks(trottle, stick) 
    } else { // Stick-to-track
        leftSpeed = -gamepad.axes[1];   // Left stick
        rightSpeed = -gamepad.axes[3];  // Right stick
    }

    roundedLeftSpeed = Number(leftSpeed.toFixed(2));
    roundedRightSpeed = Number(rightSpeed.toFixed(2));
    
    // Only send if x ms has passed
    const now = Date.now();
    if (now - lastSendTime > refreshTimeMs) {
      sendCommand(leftSpeed, rightSpeed);
      lastSendTime = now;
    }
  }

  animationFrame = requestAnimationFrame(pollGamepad);
}

async function sendCommand(left: number, right: number) {
    if(!ip) {
        console.log("IP is not set. sendCommand returning.")
        return
    } else {
        console.log(`Sending command to ${ip} - Left: ${left}, Right: ${right}`);
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
}

function confirmIp() {
    ip = ip_textbox
}

onMount(() => {
    pollGamepad();
    sendCommand(0, 0); // Ensure motors are stopped on load and check connection

    updatePing();

    setInterval(() => {
        updatePing();

        if (status === "Disconnected") {
            sendCommand(0, 0);
        }
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
    {#if ip}
        <!-- <img src={`http://${ip}:5000/camera`} width="640" height="480" alt="RC Tank Camera Feed"> -->
        <!-- Test Image -->
        <div class="layout">
            <div class="side left">
                <div class="info_card px-4 py-2">
                    <p>Left Speed: {roundedLeftSpeed}</p>
                    <p>Right Speed: {roundedRightSpeed}</p>
                </div>
            </div>

            <div class="center">
                {#if videoSetting}
                    {#if status !== 'Connected'}
                        <img class="border black_background" src={`${cam_off_icon}`} width="640" height="480" alt="Test Cam Feed">
                        <p style="color: #FF0000; font-weight: bold;">{status}</p>
                    {:else}
                        <img class="border black_background" src={`http://${ip}:5000/camera`} width="640" height="480" alt="RC Tank Camera Feed">
                        <p style="color: #00FF00; font-weight: bold;">{status}</p>
                    {/if}
                {:else}
                    <img class="border black_background" src={`${cam_off_icon}`} width="640" height="480" alt="Test Cam Feed">
                    {#if status === 'Connected'}
                        <p style="color: #00FF00; font-weight: bold;">Camera Off | {status}</p>
                    {:else if status === 'Error'}
                        <p style="color: #FF0000; font-weight: bold;">Camera Off | {status}</p>
                    {:else}
                        <p style="color: #FF0000; font-weight: bold;">Camera Off | {status}</p>
                    {/if}
                {/if}
            </div>

            <div class="side right">
                <div>
                    <p class="info_card px-4 py-2">Ping: {ping}</p>
                </div>

                <div class="mt-2 space-y-2">
                    <div class="info_card inline-flex items-center gap-3 px-3 py-2">
                        <span class="py-1">Show Video:</span>
                        <label class="switch m-0 ml-auto">
                            <input type="checkbox" bind:checked={videoSetting}>
                            <span class="slider round"></span>
                        </label>
                    </div>

                    <div class="info_card inline-flex items-center gap-3 px-3 py-2">
                        <span class="py-1">Refresh:</span>
                        <div class="inline-flex items-center gap-2 ml-auto">
                            <button on:click={() => changeRefresh(-10)} class="cursor-pointer button px-2 py-1">-</button>
                            <p class="m-0">{refreshTimeMs}ms</p>
                            <button on:click={() => changeRefresh(10)} class="cursor-pointer button px-2 py-1">+</button>
                        </div>
                    </div>

                    <div class="info_card inline-flex items-center gap-3 px-3 py-2">
                        <span class="py-1">Car mode:</span>
                        <label class="switch m-0 ml-auto">
                            <input type="checkbox" bind:checked={carMode}>
                            <span class="slider round"></span>
                        </label>
                    </div>
                </div>
            </div>
        </div>
    {:else}
        <div class="center">
            <div class="border black_background ip_picker">
                <input
                    id={'ip_textbox'}
                    bind:value={ip_textbox}
                    placeholder="Tank IP"
                    class="border focus:outline-none px-2 py-1 mt-4"
                />
                <button 
                    on:click={() => confirmIp()}
                    class="px-4 py-2 cursor-pointer button px-2 py-1 mt-4">
                    Confirm
                </button>
            </div>
        </div>
    {/if}
</main>