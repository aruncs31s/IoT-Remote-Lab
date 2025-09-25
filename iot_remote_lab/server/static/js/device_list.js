// View switching functionality
function switchView(viewType) {
    const cardView = document.getElementById('cardView');
    const tableView = document.getElementById('tableView');
    const cardViewBtn = document.getElementById('cardViewBtn');
    const tableViewBtn = document.getElementById('tableViewBtn');

    if (viewType === 'card') {
        cardView.style.display = 'grid';
        tableView.style.display = 'none';
        cardViewBtn.classList.add('active');
        tableViewBtn.classList.remove('active');
    } else {
        cardView.style.display = 'none';
        tableView.style.display = 'block';
        cardViewBtn.classList.remove('active');
        tableViewBtn.classList.add('active');
    }
}

// Device management functions
function connectDevice(port) {
    console.log(`Connecting to device on port: ${port}`);
    alert(`Connecting to device on port ${port}...`);

    // TODO: Implement actual connection logic
    // Example: Send POST request to /api/devices/{port}/connect
}

function configureDevice(port) {
    console.log(`Configuring device on port: ${port}`);
    alert(`Opening configuration for device on port ${port}...`);

    // TODO: Implement configuration modal or redirect
    // Example: window.location.href = `/device/${port}/config`;
}

function monitorDevice(port) {
    console.log(`Monitoring device on port: ${port}`);
    alert(`Starting monitoring for device on port ${port}...`);

    // TODO: Implement monitoring functionality
    // Example: window.location.href = `/device/${port}/monitor`;
}

// Auto-refresh device status every 10 seconds
setInterval(() => {
    // TODO: Implement status checking without full page reload
    console.log('Checking device status...');
}, 10000);

// Initialize tooltips or additional functionality
document.addEventListener('DOMContentLoaded', function () {
    console.log('Device list page loaded');

    // Add any initialization code here
});
