window.addEventListener('DOMContentLoaded', (event) => {
    const facialEmail = document.getElementById('facial-email');
    const canvas = document.getElementById('facial-video');
    const cameraPlaceholder = document.getElementById('camera-placeholder');
    const messageElement = document.getElementById('facial-message');
    const startBtn = document.getElementById('start-facial-btn');
    const stopBtn = document.getElementById('stop-facial-btn');

    let socket = null;
    let video = null;
    let streaming = false;
    let authenticated = false;
    let ctx = canvas.getContext('2d');

    facialEmail.addEventListener('input', () => {
        const email = facialEmail.value.trim();
        startBtn.disabled = !email || !isValidEmail(email);
    });

    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    async function checkUserExists(email) {
        try {
            const response = await fetch(checkUserFacial, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({email: email})
            });

            const data = await response.json();
            return {
                exists: data.exists && data.has_facial_data,
                token: data.token
            };
        } catch (error) {
            console.error('Error checking user:', error);
            return {exists: false, token: null};
        }
    }

    startBtn.addEventListener('click', async () => {
        const email = facialEmail.value.trim();

        if (!email || !isValidEmail(email)) {
            showMessage('Ingresa un email válido', 'error');
            return;
        }

        showMessage('Verificando usuario...', 'info');
        startBtn.disabled = true;

        const result = await checkUserExists(email);

        if (!result.exists || !result.token) {
            showMessage('Usuario no encontrado o sin datos faciales registrados', 'error');
            startBtn.disabled = false;
            return;
        }

        initFacialRecognition(result.token);
    });

    stopBtn.addEventListener('click', () => {
        stopFacialRecognition();
    });

    async function initFacialRecognition(authToken) {
        try {
            socket = new WebSocket(`ws://${window.location.host}/ws/facial-login/${authToken}/`);

            socket.onopen = async () => {
                console.log('WebSocket conectado');
                await initCamera();
            };

            socket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                handleWebSocketMessage(data);
            };

            socket.onerror = (error) => {
                console.error('WebSocket error:', error);
                showMessage('Error de conexión', 'error');
                resetUI();
            };

            socket.onclose = (event) => {
                console.log('WebSocket cerrado');
                if (event.code === 4000) {
                    showMessage('Usuario no encontrado o sin datos faciales', 'error');
                } else if (event.code === 4001) {
                    showMessage('Token de sesión inválido', 'error');
                }
                resetUI();
            };

        } catch (error) {
            console.error('Error iniciando reconocimiento:', error);
            showMessage('Error iniciando reconocimiento facial', 'error');
            resetUI();
        }
    }

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

                cameraPlaceholder.classList.add('hidden');
                canvas.classList.remove('hidden');

                startBtn.classList.add('hidden');
                stopBtn.classList.remove('hidden');
                facialEmail.disabled = true;

                showMessage('Cámara iniciada. Posiciona tu rostro en el centro.', 'info');

                drawVideoFrame();
                startCapturing();
            };

            await video.play();

        } catch (err) {
            console.error('Error cámara:', err);
            showMessage(`Error: ${err.message}. Verifica permisos y usa HTTPS.`, 'error');
            resetUI();
        }
    }

    function drawVideoFrame() {
        if (streaming && !authenticated) {
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            requestAnimationFrame(drawVideoFrame);
        }
    }

    function startCapturing() {
        const captureInterval = setInterval(() => {
            if (authenticated) {
                clearInterval(captureInterval);
                return;
            }
            if (streaming) {
                sendFrameBytes();
            }
        }, 300);
    }

    function sendFrameBytes() {
        if (!streaming || authenticated || !socket || socket.readyState !== WebSocket.OPEN) return;

        canvas.toBlob(blob => {
            if (blob) {
                socket.send(blob);
            }
        }, 'image/jpeg', 0.8);
    }

    function handleWebSocketMessage(data) {
        showMessage(data.message, data.status);

        if (data.status === 'success' && data.auth_token) {
            authenticated = true;
            stopCamera();
            completeFacialAuth(data.auth_token);
        }
    }

    async function completeFacialAuth(authToken) {
        try {
            const response = await fetch(loginFacial, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({auth_token: authToken})
            });

            const data = await response.json();

            if (data.success) {
                showMessage('¡Login completado!', 'success');
                setTimeout(() => {
                    window.location.href = redirectURL;
                }, 1000);
            } else {
                showMessage('Error completando login: ' + data.message, 'error');
                resetUI();
            }
        } catch (error) {
            console.error('Error completing auth:', error);
            showMessage('Error completando autenticación', 'error');
            resetUI();
        }
    }

    function stopFacialRecognition() {
        stopCamera();

        if (socket) {
            socket.close();
            socket = null;
        }

        resetUI();
    }

    function stopCamera() {
        streaming = false;

        if (video && video.srcObject) {
            video.srcObject.getTracks().forEach(track => track.stop());
            video = null;
        }
    }

    function resetUI() {
        canvas.classList.add('hidden');
        cameraPlaceholder.classList.remove('hidden');
        startBtn.classList.remove('hidden');
        stopBtn.classList.add('hidden');
        startBtn.disabled = !facialEmail.value.trim() || !isValidEmail(facialEmail.value.trim());
        facialEmail.disabled = false;
        authenticated = false;
    }

    function showMessage(message, status) {
        messageElement.textContent = message;
        messageElement.className = `mb-4 text-center text-sm ${
            status === 'success' ? 'text-green-500' :
                status === 'error' || status === 'not_recognized' ? 'text-red-500' :
                    status === 'analyzing' ? 'text-blue-500' :
                        'text-gray-600'
        }`;
    }
});