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
				console.log('found message with id');
				const { resolve } = this.pendingRequests.get(message.id); // the brackets destructure the object,
				// so we set resolve to the resolve item from the object
				resolve(message.data);
				this.pendingRequests.delete(message.id);
			}
		} else {
			// if normal message
			const messageType = splitMessage[0];

			// do normal stuff here
		}
	}

	async twoWayMessage(type: string, data: any) {
		return new Promise((resolve, reject) => {
			const id = this.send(`two_way_message:${type}`, data);

			this.pendingRequests.set(id, { resolve, reject });

			setTimeout(() => {
				if (this.pendingRequests.has(id)) {
					this.pendingRequests.delete(id);
					reject(new Error('Request timed out'));
				}
			}, 5000);
		});
	}
}

export const ws = new WebSocketHandler();
