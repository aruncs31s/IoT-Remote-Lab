// Serial Monitor JavaScript
class SerialMonitor {
    constructor() {
        this.isConnected = false;
        this.selectedDevice = null;
        this.socket = null;
        this.bytesReceived = 0;
        this.bytesSent = 0;
        this.linesCount = 0;
        this.connectionStartTime = null;
        this.connectionTimer = null;

        this.initializeElements();
        this.attachEventListeners();
        this.loadAvailableDevices();
    }

    initializeElements() {
        // Status elements
        this.statusIndicator = document.getElementById('status-indicator');
        this.statusText = document.getElementById('status-text');
        this.deviceName = document.getElementById('device-name');

        // Control buttons
        this.connectBtn = document.getElementById('connect-btn');
        this.disconnectBtn = document.getElementById('disconnect-btn');
        this.clearBtn = document.getElementById('clear-btn');
        this.refreshDevicesBtn = document.getElementById('refresh-devices');

        // Panels
        this.deviceSelectionPanel = document.getElementById('device-selection-panel');
        this.serialOutputContainer = document.getElementById('serial-output-container');
        this.serialInputContainer = document.getElementById('serial-input-container');

        // Device lists
        this.devicesList = document.getElementById('devices-list');
        this.modalDevicesList = document.getElementById('modal-devices-list');

        // Serial I/O
        this.serialOutput = document.getElementById('serial-output');
        this.serialInput = document.getElementById('serial-input');
        this.sendBtn = document.getElementById('send-btn');

        // Controls
        this.autoScrollCheckbox = document.getElementById('auto-scroll');
        this.timestampCheckbox = document.getElementById('timestamp');
        this.baudRateSelect = document.getElementById('baud-rate');
        this.lineEndingSelect = document.getElementById('line-ending');

        // Modal elements
        this.deviceModal = document.getElementById('device-modal');
        this.closeModal = document.getElementById('close-modal');
        this.confirmConnect = document.getElementById('confirm-connect');
        this.cancelConnect = document.getElementById('cancel-connect');

        // Stats elements
        this.bytesReceivedStat = document.getElementById('bytes-received');
        this.bytesSentStat = document.getElementById('bytes-sent');
        this.linesCountStat = document.getElementById('lines-count');
        this.connectedTimeStat = document.getElementById('connected-time');
    }

    attachEventListeners() {
        // Button events
        this.connectBtn.addEventListener('click', () => this.openDeviceModal());
        this.disconnectBtn.addEventListener('click', () => this.disconnect());
        this.clearBtn.addEventListener('click', () => this.clearOutput());
        this.refreshDevicesBtn.addEventListener('click', () => this.loadAvailableDevices());
        this.sendBtn.addEventListener('click', () => this.sendData());

        // Serial input events
        this.serialInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendData();
            }
        });

        // Baud rate change
        this.baudRateSelect.addEventListener('change', () => {
            if (this.isConnected) {
                this.updateBaudRate();
            }
        });

        // Modal events
        this.closeModal.addEventListener('click', () => this.closeDeviceModal());
        this.cancelConnect.addEventListener('click', () => this.closeDeviceModal());
        this.confirmConnect.addEventListener('click', () => this.connectToSelectedDevice());

        // Close modal when clicking outside
        this.deviceModal.addEventListener('click', (e) => {
            if (e.target === this.deviceModal) {
                this.closeDeviceModal();
            }
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                e.preventDefault();
                this.sendData();
            }
            if (e.ctrlKey && e.key === 'l') {
                e.preventDefault();
                this.clearOutput();
            }
        });
    }

    async loadAvailableDevices() {
        try {
            this.devicesList.innerHTML = `
                <div class="loading-devices">
                    <div class="spinner"></div>
                    <span>Loading devices...</span>
                </div>
            `;

            const response = await fetch('/api/devices');
            const data = await response.json();

            if (data.success && data.count > 0) {
                this.displayDevices(data.data, this.devicesList);
            } else {
                this.devicesList.innerHTML = `
                    <div style="text-align: center; padding: 2rem; color: var(--ctp-subtext1);">
                        <i class="fa-solid fa-exclamation-triangle" style="font-size: 2rem; margin-bottom: 1rem;"></i>
                        <p>No devices found</p>
                        <p style="font-size: 0.9rem;">Make sure your device is connected and try again.</p>
                    </div>
                `;
            }
        } catch (error) {
            console.error('Error loading devices:', error);
            this.devicesList.innerHTML = `
                <div style="text-align: center; padding: 2rem; color: var(--ctp-red);">
                    <i class="fa-solid fa-exclamation-circle" style="font-size: 2rem; margin-bottom: 1rem;"></i>
                    <p>Failed to load devices</p>
                    <p style="font-size: 0.9rem;">Check your connection and try again.</p>
                </div>
            `;
        }
    }

    displayDevices(devices, container) {
        container.innerHTML = '';

        devices.forEach(device => {
            const deviceCard = document.createElement('div');
            deviceCard.className = 'device-card';
            deviceCard.onclick = () => this.selectDevice(device, deviceCard);

            const statusClass = `status-${device.status || 'unknown'}`;
            const deviceIcon = this.getDeviceIcon(device.type);
            const statusText = this.getStatusDisplayText(device.status);

            deviceCard.innerHTML = `
                <div class="device-icon">
                    <!-- <i class="fa-solid ${deviceIcon}"></i> -->
                    <i class="fa-solid fa-microchip"></i>
                </div>
                <div class="device-details">
                    <div class="device-name">${device.name || device.type || 'Unknown Device'}</div>
                    <div class="device-port">${device.port || 'Unknown Port'}</div>
                </div>
                <div class="device-status ${statusClass}">
                    ${statusText}
                </div>
            `;

            container.appendChild(deviceCard);
        });
    }

    getDeviceIcon(deviceType) {
        const icons = {
            'arduino': 'fa-microchip',
            'esp32': 'fa-wifi',
            'esp8266': 'fa-wifi',
            'raspberry-pi': 'fa-raspberry-pi',
            'unknown': 'fa-usb'
        };

        if (!deviceType || typeof deviceType !== 'string') {
            return icons['unknown'];
        }

        return icons[deviceType.toLowerCase()] || icons['unknown'];
    }

    getStatusDisplayText(status) {
        const statusTexts = {
            'connected': 'Available',
            'disconnected': 'Offline',
            'unknown': 'Unknown',
            'busy': 'Busy',
            'monitoring': 'Monitoring'
        };

        return statusTexts[status] || 'Unknown';
    }

    selectDevice(device, deviceElement) {
        // Remove selection from all devices
        document.querySelectorAll('.device-card').forEach(card => {
            card.classList.remove('selected');
        });

        // Select current device
        deviceElement.classList.add('selected');
        this.selectedDevice = device;

        if (this.confirmConnect) {
            this.confirmConnect.disabled = false;
        }
    }

    openDeviceModal() {
        this.deviceModal.classList.add('show');
        this.loadModalDevices();
    }

    closeDeviceModal() {
        this.deviceModal.classList.remove('show');
        this.selectedDevice = null;
        if (this.confirmConnect) {
            this.confirmConnect.disabled = true;
        }
    }

    async loadModalDevices() {
        try {
            this.modalDevicesList.innerHTML = `
                <div class="loading-devices">
                    <div class="spinner"></div>
                    <span>Loading devices...</span>
                </div>
            `;

            const response = await fetch('/api/devices');
            const data = await response.json();

            if (data.success && data.count > 0) {
                this.displayDevices(data.data, this.modalDevicesList);
            } else {
                this.modalDevicesList.innerHTML = `
                    <div style="text-align: center; padding: 2rem; color: var(--ctp-subtext1);">
                        <p>No devices found</p>
                    </div>
                `;
            }
        } catch (error) {
            console.error('Error loading modal devices:', error);
            this.modalDevicesList.innerHTML = `
                <div style="text-align: center; padding: 2rem; color: var(--ctp-red);">
                    <p>Failed to load devices</p>
                </div>
            `;
        }
    }

    async connectToSelectedDevice() {
        if (!this.selectedDevice) {
            this.showMessage('Please select a device first', 'error');
            return;
        }

        this.closeDeviceModal();
        await this.connect(this.selectedDevice);
    }

    async connect(device) {
        try {
            this.updateStatus('connecting', 'Connecting...');

            const response = await fetch('/api/serial/connect', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    device: device,
                    baud_rate: parseInt(this.baudRateSelect.value)
                })
            });

            const data = await response.json();

            if (data.success) {
                this.isConnected = true;
                this.selectedDevice = device;
                this.updateStatus('connected', 'Connected');
                this.deviceName.textContent = device.name || device.port;

                // Update UI
                this.connectBtn.disabled = true;
                this.disconnectBtn.disabled = false;
                this.serialInput.disabled = false;
                this.sendBtn.disabled = false;

                // Hide device selection panel
                this.deviceSelectionPanel.classList.add('hidden');

                // Clear welcome message
                this.clearOutput();

                // Start connection timer
                this.startConnectionTimer();

                // Initialize WebSocket for real-time data
                this.initializeWebSocket(data.session_id);

                this.showMessage(`Connected to ${device.name || device.port}`, 'success');
            } else {
                this.updateStatus('disconnected', 'Connection failed');
                this.showMessage(data.error || 'Failed to connect to device', 'error');
            }
        } catch (error) {
            console.error('Connection error:', error);
            this.updateStatus('disconnected', 'Connection failed');
            this.showMessage('Network error: Failed to connect to device', 'error');
        }
    }

    async disconnect() {
        try {
            if (this.socket) {
                this.socket.close();
                this.socket = null;
            }

            const response = await fetch('/api/serial/disconnect', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    device: this.selectedDevice
                })
            });

            this.isConnected = false;
            this.selectedDevice = null;

            this.updateStatus('disconnected', 'Disconnected');
            this.deviceName.textContent = 'No device selected';

            // Update UI
            this.connectBtn.disabled = false;
            this.disconnectBtn.disabled = true;
            this.serialInput.disabled = true;
            this.sendBtn.disabled = true;

            // Show device selection panel
            this.deviceSelectionPanel.classList.remove('hidden');

            // Stop connection timer
            this.stopConnectionTimer();

            // Reset stats
            this.resetStats();

            this.showMessage('Disconnected from device', 'info');
            this.loadAvailableDevices();
        } catch (error) {
            console.error('Disconnect error:', error);
            this.showMessage('Error disconnecting from device', 'error');
        }
    }

    initializeWebSocket(sessionId) {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/serial/${sessionId}`;

        this.socket = new WebSocket(wsUrl);

        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'serial_data') {
                this.appendOutput(data.data);
                this.bytesReceived += data.data.length;
                this.updateStats();
            }
        };

        this.socket.onclose = () => {
            if (this.isConnected) {
                this.showMessage('Connection lost', 'warning');
                this.disconnect();
            }
        };

        this.socket.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.showMessage('Communication error', 'error');
        };
    }

    async sendData() {
        const data = this.serialInput.value;
        if (!data.trim() || !this.isConnected) return;

        try {
            const lineEnding = this.getLineEnding();
            const dataToSend = data + lineEnding;

            const response = await fetch('/api/serial/send', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    device: this.selectedDevice,
                    data: dataToSend
                })
            });

            const result = await response.json();

            if (result.success) {
                // Show sent data in output
                this.appendOutput(`> ${data}`, 'sent');
                this.serialInput.value = '';
                this.bytesSent += dataToSend.length;
                this.updateStats();
            } else {
                this.showMessage(result.error || 'Failed to send data', 'error');
            }
        } catch (error) {
            console.error('Send error:', error);
            this.showMessage('Failed to send data', 'error');
        }
    }

    getLineEnding() {
        const endings = {
            'none': '',
            'cr': '\r',
            'lf': '\n',
            'crlf': '\r\n'
        };
        return endings[this.lineEndingSelect.value] || '';
    }

    appendOutput(data, type = 'received') {
        const lines = data.split('\n');

        lines.forEach((line, index) => {
            if (line.trim() || index < lines.length - 1) {
                const lineElement = document.createElement('div');
                lineElement.className = 'serial-line';

                if (this.timestampCheckbox.checked) {
                    const timestamp = document.createElement('span');
                    timestamp.className = 'timestamp';
                    timestamp.textContent = new Date().toLocaleTimeString();
                    lineElement.appendChild(timestamp);
                }

                const content = document.createElement('span');
                content.className = `line-content ${type}-line`;
                content.textContent = line;
                lineElement.appendChild(content);

                this.serialOutput.appendChild(lineElement);
                this.linesCount++;
            }
        });

        // Remove welcome message if it exists
        const welcomeMessage = this.serialOutput.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }

        // Auto-scroll if enabled
        if (this.autoScrollCheckbox.checked) {
            this.serialOutput.scrollTop = this.serialOutput.scrollHeight;
        }

        this.updateStats();
    }

    clearOutput() {
        this.serialOutput.innerHTML = '';
        this.linesCount = 0;
        this.updateStats();
    }

    async updateBaudRate() {
        if (!this.isConnected) return;

        try {
            const response = await fetch('/api/serial/baud_rate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    device: this.selectedDevice,
                    baud_rate: parseInt(this.baudRateSelect.value)
                })
            });

            const data = await response.json();
            if (!data.success) {
                this.showMessage(data.error || 'Failed to update baud rate', 'error');
            }
        } catch (error) {
            console.error('Baud rate update error:', error);
            this.showMessage('Failed to update baud rate', 'error');
        }
    }

    updateStatus(status, text) {
        this.statusIndicator.className = `status-indicator ${status}`;
        this.statusText.textContent = text;
    }

    startConnectionTimer() {
        this.connectionStartTime = Date.now();
        this.connectionTimer = setInterval(() => {
            const elapsed = Date.now() - this.connectionStartTime;
            const hours = Math.floor(elapsed / 3600000);
            const minutes = Math.floor((elapsed % 3600000) / 60000);
            const seconds = Math.floor((elapsed % 60000) / 1000);

            this.connectedTimeStat.textContent =
                `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }, 1000);
    }

    stopConnectionTimer() {
        if (this.connectionTimer) {
            clearInterval(this.connectionTimer);
            this.connectionTimer = null;
        }
        this.connectedTimeStat.textContent = '00:00:00';
    }

    updateStats() {
        this.bytesReceivedStat.textContent = this.bytesReceived.toLocaleString();
        this.bytesSentStat.textContent = this.bytesSent.toLocaleString();
        this.linesCountStat.textContent = this.linesCount.toLocaleString();
    }

    resetStats() {
        this.bytesReceived = 0;
        this.bytesSent = 0;
        this.linesCount = 0;
        this.updateStats();
    }

    showMessage(message, type = 'info') {
        // Create a temporary message element
        const messageElement = document.createElement('div');
        messageElement.className = `message ${type}`;
        messageElement.textContent = message;
        messageElement.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            color: white;
            font-weight: 600;
            z-index: 10000;
            animation: slideIn 0.3s ease-out;
        `;

        const colors = {
            'success': 'var(--ctp-green)',
            'error': 'var(--ctp-red)',
            'warning': 'var(--ctp-yellow)',
            'info': 'var(--ctp-sky)'
        };

        messageElement.style.backgroundColor = colors[type] || colors['info'];

        document.body.appendChild(messageElement);

        setTimeout(() => {
            messageElement.remove();
        }, 5000);
    }
}

// Initialize Serial Monitor when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new SerialMonitor();
});
