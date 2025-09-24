let simulatorRunning = false;
let gpioStates = {
    2: false,
    4: false,
    builtin: false
};

function toggleSimulator() {
    const statusDot = document.getElementById('simulatorStatus');
    const statusText = document.getElementById('statusText');
    const toggleBtn = document.getElementById('toggleSimulator');

    simulatorRunning = !simulatorRunning;

    if (simulatorRunning) {
        statusDot.classList.add('running');
        statusText.textContent = 'Simulator Running';
        toggleBtn.innerHTML = '⏸️ Stop Simulator';
        toggleBtn.classList.remove('btn-primary');
        toggleBtn.classList.add('btn-secondary');
        
        addOutput('success', '[INFO] Simulator started');
        addOutput('info', '[DEBUG] ESP32 boot sequence initiated');
        addOutput('info', '[DEBUG] WiFi stack initialized');
    } else {
        statusDot.classList.remove('running');
        statusText.textContent = 'Simulator Stopped';
        toggleBtn.innerHTML = '▶️ Start Simulator';
        toggleBtn.classList.remove('btn-secondary');
        toggleBtn.classList.add('btn-primary');
        
        addOutput('warning', '[INFO] Simulator stopped');
    }
}

function toggleGPIO(pin) {
    if (!simulatorRunning) {
        alert('Please start the simulator first');
        return;
    }

    gpioStates[pin] = !gpioStates[pin];
    const ledElement = document.getElementById(`gpio${pin}LED`);
    
    if (gpioStates[pin]) {
        ledElement.classList.remove('off');
        ledElement.classList.add('on');
        addOutput('success', `[GPIO] GPIO${pin} set to HIGH`);
    } else {
        ledElement.classList.remove('on');
        ledElement.classList.add('off');
        addOutput('info', `[GPIO] GPIO${pin} set to LOW`);
    }
}

function toggleBuiltinLED() {
    if (!simulatorRunning) {
        alert('Please start the simulator first');
        return;
    }

    gpioStates.builtin = !gpioStates.builtin;
    const ledElement = document.getElementById('builtinLED');
    
    if (gpioStates.builtin) {
        ledElement.classList.remove('off');
        ledElement.classList.add('on');
        addOutput('success', '[LED] Built-in LED turned ON');
    } else {
        ledElement.classList.remove('on');
        ledElement.classList.add('off');
        addOutput('info', '[LED] Built-in LED turned OFF');
    }
}

function simulateWiFiConnect() {
    if (!simulatorRunning) {
        alert('Please start the simulator first');
        return;
    }

    const ssid = document.getElementById('wifiSSID').value;
    if (!ssid) {
        addOutput('error', '[WiFi] ERROR: No SSID provided');
        return;
    }

    addOutput('info', `[WiFi] Attempting to connect to "${ssid}"`);
    setTimeout(() => {
        addOutput('success', `[WiFi] Connected to "${ssid}"`);
        addOutput('info', '[WiFi] IP address: 192.168.1.100');
    }, 2000);
}

function updateTemperature(value) {
    document.getElementById('tempValue').textContent = value + '°C';
    
    if (simulatorRunning) {
        addOutput('info', `[SENSOR] Temperature reading: ${value}°C`);
    }
}

function sendCommand() {
    if (!simulatorRunning) {
        alert('Please start the simulator first');
        return;
    }

    const command = document.getElementById('customCommand').value;
    if (!command) return;

    addOutput('info', `[CMD] > ${command}`);
    
    // Simulate command responses
    setTimeout(() => {
        if (command.toLowerCase().includes('help')) {
            addOutput('success', '[CMD] Available commands: reset, status, gpio, wifi');
        } else if (command.toLowerCase().includes('status')) {
            addOutput('success', '[CMD] System status: Running, Free heap: 280KB');
        } else {
            addOutput('warning', `[CMD] Unknown command: ${command}`);
        }
    }, 500);

    document.getElementById('customCommand').value = '';
}

function addOutput(type, message) {
    const output = document.getElementById('serialOutput');
    const line = document.createElement('div');
    line.className = `output-line ${type}`;
    line.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
    
    output.appendChild(line);
    output.scrollTop = output.scrollHeight;
}

function clearOutput() {
    document.getElementById('serialOutput').innerHTML = `
        <div class="output-line info">[INFO] Output cleared</div>
    `;
}

function downloadLog() {
    const output = document.getElementById('serialOutput').innerText;
    const blob = new Blob([output], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'esp32-simulator-log.txt';
    a.click();
    URL.revokeObjectURL(url);
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    addOutput('info', '[SYSTEM] Simulator interface ready');
});