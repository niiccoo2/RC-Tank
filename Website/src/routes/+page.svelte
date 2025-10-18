<script lang="ts">
  let leftSpeed: number = 0;
  let rightSpeed: number = 0;
  let status: string = 'disconnected';

  async function sendCommand(left: number, right: number) {
    console.log(`Sending command - Left: ${left}, Right: ${right}`);
    try {
      const response = await fetch('http://192.168.1.161:5000/motor', {
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

<main>
  <div class="terminal">
    <header>
      <h1>RC-TANK CONTROL</h1>
      <div class="status" class:connected={status === 'connected'} class:error={status === 'error'}>
        ● {status.toUpperCase()}
      </div>
    </header>

    <div class="controls">
      <button on:click={handleForward} class="btn">▲ FORWARD</button>
      <div class="row">
        <button on:click={handleLeft} class="btn">◄ LEFT</button>
        <button on:click={handleStop} class="btn stop">■ STOP</button>
        <button on:click={handleRight} class="btn">RIGHT ►</button>
      </div>
      <button on:click={handleReverse} class="btn">▼ REVERSE</button>
    </div>

    <div class="telemetry">
      <div class="bar">
        <span>LEFT:</span>
        <div class="meter">
          <div class="fill" style="width: {Math.abs(leftSpeed) * 100}%; background: {leftSpeed < 0 ? '#ff0000' : '#00ff00'}"></div>
        </div>
        <span>{(leftSpeed * 100).toFixed(0)}%</span>
      </div>
      <div class="bar">
        <span>RIGHT:</span>
        <div class="meter">
          <div class="fill" style="width: {Math.abs(rightSpeed) * 100}%; background: {rightSpeed < 0 ? '#ff0000' : '#00ff00'}"></div>
        </div>
        <span>{(rightSpeed * 100).toFixed(0)}%</span>
      </div>
    </div>
  </div>
</main>

<style>
  :global(body) {
    margin: 0;
    padding: 0;
    background: #000;
    font-family: 'Courier New', monospace;
    color: #0f0;
    overflow: hidden;
  }

  main {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    padding: 1rem;
  }

  .terminal {
    border: 2px solid #0f0;
    padding: 2rem;
    max-width: 600px;
    width: 100%;
    background: #000;
    box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
  }

  header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #0f0;
  }

  h1 {
    margin: 0;
    font-size: 1.5rem;
    letter-spacing: 2px;
  }

  .status {
    color: #666;
    font-size: 0.9rem;
  }

  .status.connected {
    color: #0f0;
  }

  .status.error {
    color: #f00;
  }

  .controls {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-bottom: 2rem;
  }

  .row {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 0.5rem;
  }

  .btn {
    background: #000;
    border: 1px solid #0f0;
    color: #0f0;
    padding: 1rem;
    font-family: 'Courier New', monospace;
    font-size: 1rem;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn:hover {
    background: #0f0;
    color: #000;
    box-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
  }

  .btn:active {
    transform: scale(0.95);
  }

  .btn.stop {
    border-color: #f00;
    color: #f00;
  }

  .btn.stop:hover {
    background: #f00;
    color: #000;
    box-shadow: 0 0 10px rgba(255, 0, 0, 0.5);
  }

  .telemetry {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .bar {
    display: grid;
    grid-template-columns: 60px 1fr 60px;
    gap: 0.5rem;
    align-items: center;
  }

  .meter {
    height: 20px;
    border: 1px solid #0f0;
    position: relative;
    overflow: hidden;
  }

  .fill {
    height: 100%;
    transition: width 0.3s;
  }

  span {
    font-size: 0.9rem;
    text-align: center;
  }

  @media (max-width: 640px) {
    .terminal {
      padding: 1rem;
    }

    h1 {
      font-size: 1.2rem;
    }

    .btn {
      padding: 0.75rem;
      font-size: 0.9rem;
    }
  }
</style>