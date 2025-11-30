<script lang="ts">
	import { onMount, onDestroy } from 'svelte';

	// Props
	let { ip }: { ip: string } = $props();

	// State
	let connectionStatus = $state<'Connecting' | 'Connected' | 'Error' | 'Disconnected'>(
		'Disconnected'
	);
	let videoElement: HTMLVideoElement;
	let peerConnection: RTCPeerConnection | null = null;
	let currentIp = '';

	// Clean up existing connection
	function cleanup() {
		if (peerConnection) {
			peerConnection.close();
			peerConnection = null;
		}
		if (videoElement && videoElement.srcObject) {
			const stream = videoElement.srcObject as MediaStream;
			stream.getTracks().forEach((track) => track.stop());
			videoElement.srcObject = null;
		}
	}

	// Set up WebRTC connection
	async function setupWebRTC() {
		if (!ip) {
			connectionStatus = 'Disconnected';
			return;
		}

		// Clean up any existing connection
		cleanup();
		currentIp = ip;
		connectionStatus = 'Connecting';

		try {
			// Create peer connection
			peerConnection = new RTCPeerConnection({
				iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
			});

			// Handle incoming tracks
			peerConnection.ontrack = (event) => {
				if (videoElement && event.streams[0]) {
					videoElement.srcObject = event.streams[0];
					connectionStatus = 'Connected';
				}
			};

			// Handle connection state changes
			peerConnection.onconnectionstatechange = () => {
				if (peerConnection) {
					switch (peerConnection.connectionState) {
						case 'connected':
							connectionStatus = 'Connected';
							break;
						case 'disconnected':
						case 'closed':
							connectionStatus = 'Disconnected';
							break;
						case 'failed':
							connectionStatus = 'Error';
							break;
					}
				}
			};

			// Handle ICE connection state changes
			peerConnection.oniceconnectionstatechange = () => {
				if (peerConnection) {
					if (peerConnection.iceConnectionState === 'failed') {
						connectionStatus = 'Error';
					}
				}
			};

			// Add transceiver for receiving video
			peerConnection.addTransceiver('video', { direction: 'recvonly' });

			// Create offer
			const offer = await peerConnection.createOffer();
			await peerConnection.setLocalDescription(offer);

			// Wait for ICE gathering to complete
			await new Promise<void>((resolve) => {
				if (peerConnection!.iceGatheringState === 'complete') {
					resolve();
				} else {
					const checkState = () => {
						if (peerConnection!.iceGatheringState === 'complete') {
							peerConnection!.removeEventListener('icegatheringstatechange', checkState);
							resolve();
						}
					};
					peerConnection!.addEventListener('icegatheringstatechange', checkState);
				}
			});

			// Send offer to server and get answer
			const response = await fetch(`http://${ip}:5000/webrtc/offer`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					sdp: peerConnection.localDescription?.sdp,
					type: peerConnection.localDescription?.type
				})
			});

			if (!response.ok) {
				throw new Error(`Server returned ${response.status}`);
			}

			const answer = await response.json();

			// Set remote description
			await peerConnection.setRemoteDescription(new RTCSessionDescription(answer));
		} catch (error) {
			console.error('WebRTC connection failed:', error);
			connectionStatus = 'Error';
			cleanup();
		}
	}

	// Watch for IP changes and reconnect
	$effect(() => {
		if (ip && ip !== currentIp) {
			setupWebRTC();
		} else if (!ip) {
			cleanup();
			connectionStatus = 'Disconnected';
		}
	});

	onMount(() => {
		if (ip) {
			setupWebRTC();
		}
	});

	onDestroy(() => {
		cleanup();
	});
</script>

<div class="webrtc-video-container">
	<video bind:this={videoElement} autoplay playsinline muted width="640" height="480"></video>
	<p
		class="status"
		class:connected={connectionStatus === 'Connected'}
		class:error={connectionStatus === 'Error'}
		class:connecting={connectionStatus === 'Connecting'}>
		{connectionStatus}
	</p>
</div>

<style>
	.webrtc-video-container {
		display: flex;
		flex-direction: column;
		align-items: center;
	}

	video {
		background-color: black;
		border: 1px solid #ccc;
	}

	.status {
		font-weight: bold;
		margin-top: 0.5rem;
	}

	.status.connected {
		color: #00ff00;
	}

	.status.error {
		color: #ff0000;
	}

	.status.connecting {
		color: #ffaa00;
	}
</style>
