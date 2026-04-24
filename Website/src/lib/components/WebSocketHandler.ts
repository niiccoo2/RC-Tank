class WebSocketHandler {
	ws: WebSocket | null = null;

	connect(ip: string) {
		this.ws = new WebSocket(`wss://${ip}:5000/ws`);
		this.ws.onmessage = (e) => this.handleMessage(JSON.parse(e.data));
	}

	send(type: string, data: any) {
		if (this.ws?.readyState === WebSocket.OPEN) {
			type = type.toLowerCase();
			this.ws.send(JSON.stringify({ type, data }));
			return 0; // success
		} else return 1; // error
	}

	handleMessage(message: any) {
		const msg = JSON.parse(message.data);

		if (msg.type === 'pong') {
			const rtt = Math.round(performance.now() - msg.data.timeStamp);
			ping = `${rtt}ms`;
		}
		// do some stuff here
		// we will have to sort the messages and decide what to do here
	}
}

export const ws = new WebSocketHandler();
export let ping: string = `N/A`;
