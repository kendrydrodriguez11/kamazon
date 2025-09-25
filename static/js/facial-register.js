window.addEventListener('DOMContentLoaded', (event) => {
    const socket = new WebSocket(`ws://${window.location.host}/ws/facial-register/${userId}/`);
    const canvas = document.getElementById('video');
    const ctx = canvas.getContext('2d');
    const messageElement = document.getElementById('message');

    let video = null;
    let streaming = false;
    let registered = false;

    async function initCamera() {
        try {
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                throw new Error('getUserMedia no soportado');
            }

            const stream = await navigator.mediaDevices.getUserMedia({
                video: true,
                audio: false
            });

            video = document.createElement('video');
            video.srcObject = stream;
            video.autoplay = true;
            video.muted = true;
            video.playsInline = true;

            video.onloadedmetadata = () => {
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                streaming = true;
                messageElement.textContent = 'Cámara iniciada correctamente';
                messageElement.className = 'mt-4 text-center text-sm text-green-500';
                drawVideoFrame();
                startCapturing();
            };

            await video.play();

        } catch (err) {
            console.error('Error cámara:', err);
            messageElement.textContent = `Error: ${err.message}. Verifica permisos y usa HTTPS.`;
            messageElement.className = 'mt-4 text-center text-sm text-red-500';
        }
    }

    function drawVideoFrame() {
        if (streaming && !registered) {
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            requestAnimationFrame(drawVideoFrame);
        }
    }

    function startCapturing() {
        const captureInterval = setInterval(() => {
            if (registered) {
                clearInterval(captureInterval);
                return;
            }
            sendFrameBytes();
        }, 200);
    }

    function sendFrameBytes() {
        if (!streaming || registered) return;

        canvas.toBlob(blob => {
            if (blob && socket.readyState === WebSocket.OPEN) {
                socket.send(blob);
            }
        }, 'image/jpeg', 0.8);
    }

    socket.onopen = () => {
        console.log('WebSocket conectado');
        initCamera();
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        updateStatus(data.message, data.status);

        if (data.status === 'success') {
            registered = true;
            stopCamera();
            setTimeout(() => {
                window.location.href = redirectUrl;
            }, 2000);
        }
    };

    socket.onerror = () => {
        messageElement.textContent = 'Error de conexión WebSocket';
    };

    socket.onclose = () => {
        console.log('WebSocket cerrado');
        stopCamera();
    };

    function updateStatus(message, status) {
        messageElement.textContent = message;
        messageElement.className = `mt-4 text-center text-sm ${
            status === 'success' ? 'text-green-500' :
                status === 'error' ? 'text-red-500' :
                    'text-blue-500'
        }`;
    }

    function stopCamera() {
        streaming = false;
        if (video && video.srcObject) {
            video.srcObject.getTracks().forEach(track => track.stop());
        }
    }
});