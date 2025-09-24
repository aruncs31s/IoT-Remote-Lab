let selectedDevice = null;

function selectDevice(port, description, hwid) {
    // Remove previous selection
    document.querySelectorAll('.device-card').forEach(card => {
        card.classList.remove('selected');
    });

    // Add selection to clicked card
    event.currentTarget.classList.add('selected');

    // Store selected device data
    selectedDevice = {
        port: port,
        description: description,
        hwid: hwid
    };

    // Update selected device info
    const infoDiv = document.getElementById('selectedDeviceInfo');
    const detailsDiv = document.getElementById('selectedDeviceDetails');
    
    detailsDiv.innerHTML = `
        <div style="margin-top: 10px;">
            <strong>Port:</strong> ${port}<br>
            <strong>Description:</strong> ${description}<br>
            <strong>Hardware ID:</strong> ${hwid}
        </div>
    `;
    
    infoDiv.classList.add('show');

    // Enable action buttons
    document.getElementById('connectBtn').disabled = false;
    document.getElementById('monitorBtn').disabled = false;
}

function connectToDevice() {
    if (!selectedDevice) {
        alert('Please select a device first');
        return;
    }

    // You can implement the connection logic here
    alert(`Connecting to device on port ${selectedDevice.port}...`);
    
    // Example: redirect to a device control page
    // window.location.href = `/device/${selectedDevice.port}`;
}

function monitorDevice() {
    if (!selectedDevice) {
        alert('Please select a device first');
        return;
    }

    // You can implement the monitoring logic here
    alert(`Starting monitoring for device on port ${selectedDevice.port}...`);
    
    // Example: redirect to a monitoring page
    // window.location.href = `/monitor/${selectedDevice.port}`;
}

// Auto-refresh every 30 seconds
setInterval(() => {
    if (!selectedDevice) {
        location.reload();
    }
}, 30000);