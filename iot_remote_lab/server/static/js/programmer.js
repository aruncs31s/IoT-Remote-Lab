// Arduino template code
const arduinoTemplate = `#include <Arduino.h>

void setup() {
  // put your setup code here, to run once:
}

void loop() {
  // put your main code here, to run repeatedly:
}`;

// Initialize CodeMirror
const editor = CodeMirror.fromTextArea(document.getElementById('code-editor'), {
    mode: 'text/x-c++src',
    theme: 'dracula',
    lineNumbers: true,
    matchBrackets: true,
    autoCloseBrackets: true,
    indentUnit: 4,
    tabSize: 4,
    indentWithTabs: false,
    lineWrapping: true,
    foldGutter: true,
    gutters: ["CodeMirror-linenumbers", "CodeMirror-foldgutter"],
    extraKeys: {
        "Ctrl-Space": "autocomplete",
        "Ctrl-S": function (cm) {
            saveProgram();
        }
    },
    value: arduinoTemplate
});

// Elements
const programNameInput = document.getElementById('program-name');
const saveBtn = document.getElementById('save-btn');
const loadBtn = document.getElementById('load-btn');
const uploadBtn = document.getElementById('upload-btn');
const loading = document.getElementById('loading');
const statusMessage = document.getElementById('status-message');
const statusText = document.getElementById('status-text');
const programsGrid = document.getElementById('programs-grid');

// Modal elements
const deviceModal = document.getElementById('device-modal');
const closeModal = document.getElementById('close-modal');
const devicesList = document.getElementById('devices-list');
const confirmUpload = document.getElementById('confirm-upload');
const cancelUpload = document.getElementById('cancel-upload');
const monitorSerial = document.getElementById('monitor-serial');
const saveBeforeUpload = document.getElementById('save-before-upload');

let selectedDevice = null;

// Show status message
function showStatus(message, type = 'success') {
    statusText.textContent = message;
    statusMessage.className = `status-message ${type} show`;
    setTimeout(() => {
        statusMessage.classList.remove('show');
    }, 5000);
}

// Save program
async function saveProgram() {
    const programName = programNameInput.value.trim();
    const code = editor.getValue();

    if (!programName) {
        showStatus('Please enter a program name', 'error');
        programNameInput.focus();
        return;
    }

    if (!code.trim()) {
        showStatus('Please write some code before saving', 'error');
        editor.focus();
        return;
    }

    loading.classList.add('active');
    saveBtn.disabled = true;

    try {
        const response = await fetch('/api/save_program', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                program_name: programName,
                code: code,
                description: `C++ program created on ${new Date().toLocaleDateString()}`
            })
        });

        const data = await response.json();

        if (data.success) {
            showStatus(data.message, 'success');
            loadPrograms(); // Refresh the programs list
        } else {
            showStatus(data.error || 'Failed to save program', 'error');
        }
    } catch (error) {
        console.error('Error saving program:', error);
        showStatus('Network error: Failed to save program', 'error');
    } finally {
        loading.classList.remove('active');
        saveBtn.disabled = false;
    }
}

// Load program
async function loadProgram(programName) {
    try {
        const response = await fetch(`/api/load_program/${encodeURIComponent(programName)}`);
        const data = await response.json();

        if (data.success) {
            programNameInput.value = data.program_name;
            editor.setValue(data.code);
            showStatus(`Loaded program "${data.program_name}"`, 'success');
        } else {
            showStatus(data.error || 'Failed to load program', 'error');
        }
    } catch (error) {
        console.error('Error loading program:', error);
        showStatus('Network error: Failed to load program', 'error');
    }
}

// Load programs list
async function loadPrograms() {
    try {
        const response = await fetch('/api/list_programs');
        const data = await response.json();

        if (data.success) {
            displayPrograms(data.programs);
        } else {
            console.error('Failed to load programs:', data.error);
        }
    } catch (error) {
        console.error('Error loading programs:', error);
    }
}

// Display programs
function displayPrograms(programs) {
    programsGrid.innerHTML = '';

    if (programs.length === 0) {
        programsGrid.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; color: var(--subtext1); padding: 2rem;">
                No saved programs yet. Create your first C++ program!
            </div>
        `;
        return;
    }

    programs.forEach(program => {
        const programCard = document.createElement('div');
        programCard.className = 'program-card';
        programCard.onclick = () => loadProgram(program.name);

        const createdDate = program.created_at ?
            new Date(program.created_at).toLocaleDateString() :
            'Unknown date';

        programCard.innerHTML = `
            <h4>📄 ${program.name}</h4>
            <div class="program-date">Created: ${createdDate}</div>
            ${program.description ? `<div class="program-description">${program.description}</div>` : ''}
        `;

        programsGrid.appendChild(programCard);
    });
}

// Modal functions
function openDeviceModal() {
    deviceModal.classList.add('show');
    loadAvailableDevices();
}

function closeDeviceModal() {
    deviceModal.classList.remove('show');
    selectedDevice = null;
    confirmUpload.disabled = true;
}

async function loadAvailableDevices() {
    try {
        devicesList.innerHTML = `
            <div class="loading-devices">
                <div class="spinner"></div>
                <span>Loading devices...</span>
            </div>
        `;

        const response = await fetch('/api/devices');
        const data = await response.json();
        if (data.success && data.count > 0) {
            displayDevices(data.data);
        } else {
            devicesList.innerHTML = `
                <div style="text-align: center; padding: 2rem; color: var(--ctp-subtext1);">
                    <i class="fa-solid fa-exclamation-triangle" style="font-size: 2rem; margin-bottom: 1rem;"></i>
                    <p>No devices found</p>
                    <p style="font-size: 0.9rem;">Make sure your device is connected and try again.</p>
                    <button class="btn btn-secondary" onclick="loadAvailableDevices()" style="margin-top: 1rem;">
                        <i class="fa-solid fa-refresh"></i> Refresh
                    </button>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading devices:', error);
        devicesList.innerHTML = `
            <div style="text-align: center; padding: 2rem; color: var(--ctp-red);">
                <i class="fa-solid fa-exclamation-circle" style="font-size: 2rem; margin-bottom: 1rem;"></i>
                <p>Failed to load devices</p>
                <p style="font-size: 0.9rem;">Check your connection and try again.</p>
                <button class="btn btn-secondary" onclick="loadAvailableDevices()" style="margin-top: 1rem;">
                    <i class="fa-solid fa-refresh"></i> Retry
                </button>
            </div>
        `;
    }
}

function displayDevices(devices) {
    devicesList.innerHTML = '';

    devices.forEach(device => {
        const deviceItem = document.createElement('div');
        deviceItem.className = 'device-item';
        deviceItem.onclick = () => selectDevice(device, deviceItem);

        // Use the actual device status from the enum, fallback to 'unknown'
        const statusClass = device.status || 'unknown';
        const deviceIcon = getDeviceIcon(device.type);

        deviceItem.innerHTML = `
            <!-- <i class="fa-solid ${deviceIcon}" style="font-size: 1.5rem; color: var(--ctp-mauve);"></i> -->
            <i class="fa-solid fa-microchip"></i>
            <div class="device-info">
                <div class="device-name">${device.name || device.type || 'Unknown Device'}</div>
                <div class="device-port">${device.port || 'Unknown Port'}</div>
            </div>
            <div class="device-status status-${statusClass}">
                ${getStatusDisplayText(statusClass)}
            </div>
        `;

        devicesList.appendChild(deviceItem);
    });
}

function getDeviceIcon(deviceType) {
    const icons = {
        'arduino': 'fa-microchip',
        'esp32': 'fa-wifi',
        'esp8266': 'fa-wifi',
        'raspberry-pi': 'fa-raspberry-pi',
        'unknown': 'fa-usb'
    };

    // Handle undefined, null, or non-string deviceType
    if (!deviceType || typeof deviceType !== 'string') {
        return icons['unknown'];
    }

    return icons[deviceType.toLowerCase()] || icons['unknown'];
}

function getStatusDisplayText(status) {
    const statusTexts = {
        'connected': '<i class="fa-solid fa-check-circle"></i> Available',
        'disconnected': '<i class="fa-solid fa-times-circle"></i> Offline',
        'unknown': '<i class="fa-solid fa-question-circle"></i> Unknown',
        'busy': '<i class="fa-solid fa-clock"></i> Busy',
        'monitoring': '<i class="fa-solid fa-chart-line"></i> Monitoring'
    };

    return statusTexts[status] || '<i class="fa-solid fa-question-circle"></i> Unknown';
}

function selectDevice(device, deviceElement) {
    // Remove selection from all devices
    document.querySelectorAll('.device-item').forEach(item => {
        item.classList.remove('selected');
    });

    // Select current device
    deviceElement.classList.add('selected');
    selectedDevice = device;
    confirmUpload.disabled = false;
}

async function uploadToDevice() {
    if (!selectedDevice) {
        showStatus('Please select a device first', 'error');
        return;
    }

    const code = editor.getValue();
    const programName = programNameInput.value.trim();

    if (!code.trim()) {
        showStatus('Please write some code before uploading', 'error');
        return;
    }

    // Save program first if option is checked
    if (saveBeforeUpload.checked && programName) {
        await saveProgram();
    }

    // Close modal and show upload progress
    closeDeviceModal();

    // Show upload status
    showStatus('Uploading to device...', 'info');

    try {
        const response = await fetch('/api/upload_firmware', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                code: code,
                device: selectedDevice,
                program_name: programName || 'untitled',
                monitor_serial: monitorSerial.checked
            })
        });

        const data = await response.json();

        if (data.success) {
            // showStatus(`Successfully uploaded to ${selectedDevice.name}`, 'success');

            // Open serial monitor if requested
            if (monitorSerial.checked && data.monitor_url) {
                window.open(data.monitor_url, '_blank');
            }
        } else {
            showStatus(data.error || 'Failed to upload to device', 'error');
        }
    } catch (error) {
        console.error('Error uploading:', error);
        showStatus('Network error: Failed to upload to device', 'error');
    }
}

// Event listeners
uploadBtn.addEventListener('click', openDeviceModal);
closeModal.addEventListener('click', closeDeviceModal);
cancelUpload.addEventListener('click', closeDeviceModal);
confirmUpload.addEventListener('click', uploadToDevice);

// Close modal when clicking outside
deviceModal.addEventListener('click', (e) => {
    if (e.target === deviceModal) {
        closeDeviceModal();
    }
});

saveBtn.addEventListener('click', saveProgram);

// Load programs on page load
document.addEventListener('DOMContentLoaded', () => {
    loadPrograms();
    editor.focus();
});

// Auto-save functionality (optional)
let autoSaveTimeout;
editor.on('change', () => {
    clearTimeout(autoSaveTimeout);
    // Uncomment to enable auto-save after 5 seconds of inactivity
    // autoSaveTimeout = setTimeout(() => {
    //     if (programNameInput.value.trim()) {
    //         saveProgram();
    //     }
    // }, 5000);
});

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 's') {
        e.preventDefault();
        saveProgram();
    }
});
