const html5QrCode = new Html5Qrcode('video');

function start() {
    html5QrCode.start(
        {facingMode: "environment"},
        {
            fps: 10,
            qrbox: 250
        },
        qrCodeMessage => {
            html5QrCode.stop();
            sendAuthorization(qrCodeMessage);
        },
        errorMessage => {
            console.error(errorMessage);
        }
    ).catch(err => {
        console.error(err);
    });
}

start();

function sendAuthorization(token) {
    const webSocket = new WebSocket(`ws://${window.location.host}/ws/qr/${token}/`);
    webSocket.onopen = () => {
        webSocket.send(JSON.stringify({
            'type': 'user_id',
            'user_id': user_id
        }));
    }
    webSocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'authenticated') {
            window.location.href = redirectUrl;
        }
    };
}
