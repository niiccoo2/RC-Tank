import { ws } from '$lib/components/WebSocketHandler.svelte';
import { status } from '$lib/stores';

let pc: RTCPeerConnection | null = null;
let statsInterval: number | null = null;

function logWebRTCStats() {
	if (!pc) return;

	pc.getStats().then((stats) => {
		stats.forEach((report) => {
			if (report.type === 'inbound-rtp' && report.kind === 'video') {
				console.log('📊 WebRTC Stats:', {
					fps: report.framesPerSecond || 0,
					packetsLost: report.packetsLost || 0,
					jitter: (report.jitter * 1000).toFixed(2) + 'ms',
					framesDropped: report.framesDropped || 0,
					framesReceived: report.framesReceived || 0
				});
			}
		});
	});
}

export function stopWebRTC() {
	if (statsInterval) {
		clearInterval(statsInterval);
		statsInterval = null;
	}

	if (pc) {
		pc.close();
		pc = null;
	}
}

export async function startWebRTC(ip: string): Promise<MediaStream | null> {
	if (pc) {
		pc.close();
	}

	const configuration = {
		iceServers: [
			{ urls: 'stun:134.209.220.119:3478' }, // do droplet
			{
				urls: 'turn:134.209.220.119:3478',
				username: 'tank',
				credential: 'tankpass'
			}
			// { urls: 'stun:173.48.62.89:3478' }, // home-server
			// {
			// 	urls: 'turn:173.48.62.89:3478',
			// 	username: 'tank',
			// 	credential: 'tankpass'
			// }
		]
	};

	pc = new RTCPeerConnection(configuration);
	let remoteStream: MediaStream | null = null;

	pc.oniceconnectionstatechange = () => {
		console.log('ICE Connection State:', pc?.iceConnectionState);
	};

	pc.addTransceiver('video', { direction: 'recvonly' });

	pc.ontrack = (event) => {
		if (!event.streams[0]) return;

		remoteStream = event.streams[0];

		// Start logging stats every 2 seconds when video starts
		// if (statsInterval) clearInterval(statsInterval);
		// statsInterval = window.setInterval(logWebRTCStats, 2000);
	};

	const offer = await pc.createOffer();
	await pc.setLocalDescription(offer);

	// Wait for ICE gathering to complete or timeout after 1.5s
	await Promise.race([
		new Promise((resolve) => {
			if (pc && pc.iceGatheringState === 'complete') {
				resolve(null);
			} else {
				const checkState = () => {
					if (pc && pc.iceGatheringState === 'complete') {
						pc.removeEventListener('icegatheringstatechange', checkState);
						resolve(null);
					}
				};
				pc?.addEventListener('icegatheringstatechange', checkState);
			}
		}),
		new Promise((resolve) => setTimeout(resolve, 1500))
	]);

	try {
		// const response = await fetch(`https://${ip}:5000/offer`, {
		// 	method: 'POST',
		// 	body: JSON.stringify({
		// 		sdp: pc.localDescription?.sdp,
		// 		type: pc.localDescription?.type
		// 	}),
		// 	headers: {
		// 		'Content-Type': 'application/json'
		// 	}
		// });

		const response: any = await ws.twoWayMessage(
			'webrtc_offer_request',
			{
				sdp: pc.localDescription?.sdp,
				type: pc.localDescription?.type
			},
			20000
		);

		await pc.setRemoteDescription(response);
		status.set('Connected');
		return remoteStream;
	} catch (e) {
		console.error('WebRTC negotiation failed:', e);
		return null;
	}
}
