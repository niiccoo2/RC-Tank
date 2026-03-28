let pc: RTCPeerConnection | null = null;
let statsInterval: number | null = null;

function getApiBase(input: string): string {
	const raw = input.trim().replace(/\/+$/, '');
	if (!raw) return '';

	if (raw.startsWith('http://') || raw.startsWith('https://')) {
		const url = new URL(raw);
		const port = url.port || '5000';
		return `${url.protocol}//${url.hostname}:${port}`;
	}

	return `http://${raw}:5000`;
}

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
			{ urls: 'stun:68.183.59.124:3478' },
			{
				urls: 'turn:68.183.59.124:3478',
				username: 'tank',
				credential: 'tankpass'
			}
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
		if (statsInterval) clearInterval(statsInterval);
		statsInterval = window.setInterval(logWebRTCStats, 2000);
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
		const response = await fetch(`${getApiBase(ip)}/offer`, {
			method: 'POST',
			body: JSON.stringify({
				sdp: pc.localDescription?.sdp,
				type: pc.localDescription?.type
			}),
			headers: {
				'Content-Type': 'application/json'
			}
		});

		const answer = await response.json();
		await pc.setRemoteDescription(answer);
		return remoteStream;
	} catch (e) {
		console.error('WebRTC negotiation failed:', e);
		return null;
	}
}
