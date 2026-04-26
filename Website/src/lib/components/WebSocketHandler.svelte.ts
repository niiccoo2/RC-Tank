import { gpsData, voltage } from '$lib/stores';

class WebSocketHandler {
	ws: WebSocket | null = null;

	ping = $state('N/A');
	pendingRequests = new Map();

	connect(ip: string) {
		this.ws = new WebSocket(`wss://${ip}:5000/ws`);
		this.ws.onmessage = (e) => this.handleMessage(JSON.parse(e.data));
	}

	send(type: string, data: any) {
		if (this.ws?.readyState === WebSocket.OPEN) {
			const id = crypto.randomUUID();
			type = type.toLowerCase();
			this.ws.send(JSON.stringify({ id, type, data }));
			return id; // success
		} else return false; // error
	}

	handleMessage(message: any) {
		const splitMessage = message.type.split(':');

		if (splitMessage.length > 1) {
			// then has a prefix. in this case that means two way message
			if (this.pendingRequests.has(message.id)) {
				const { resolve } = this.pendingRequests.get(message.id); // the brackets destructure the object,
				// so we set resolve to the resolve item from the object
				resolve(message.data);
				this.pendingRequests.delete(message.id);
			}
		} else {
			// if normal message
			const messageType = splitMessage[0];

			if (messageType === 'telemetry') {
				voltage.set(message.data.voltage);

				gpsData.set({
					lat: message.data.gps.lat,
					lon: message.data.gps.lon,
					alt: message.data.gps.alt
				});
			}
		}
	}

	waitForOpen(timeout = 3000) {
		return new Promise<void>((resolve, reject) => {
			if (this.ws?.readyState === WebSocket.OPEN) return resolve();
			const onOpen = () => {
				cleanup();
				resolve();
			};
			const onError = () => {
				cleanup();
				reject(new Error('WebSocket failed to open'));
			};
			const cleanup = () => {
				this.ws?.removeEventListener('open', onOpen);
				this.ws?.removeEventListener('error', onError);
			};
			this.ws?.addEventListener('open', onOpen);
			this.ws?.addEventListener('error', onError);
			setTimeout(() => {
				cleanup();
				reject(new Error('WebSocket open timeout'));
			}, timeout);
		});
	}

	async twoWayMessage(type: string, data: any, timeout: number = 5000) {
		await this.waitForOpen();
		return new Promise((resolve, reject) => {
			const id = this.send(`two_way_message:${type}`, data);

			if (!id) reject(new Error('WebSocket connection not open'));

			this.pendingRequests.set(id, { resolve, reject });

			setTimeout(() => {
				if (this.pendingRequests.has(id)) {
					this.pendingRequests.delete(id);
					reject(new Error('Request timed out'));
				}
			}, timeout);
		});
	}
}

export const ws = new WebSocketHandler();
