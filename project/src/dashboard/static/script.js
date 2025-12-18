// Connect to WebSocket
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const ws = new WebSocket(`${protocol}//${window.location.host}/ws`);

// Chart Configuration
const ctx = document.getElementById('errorChart').getContext('2d');
const errorChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Error Rate',
            data: [],
            borderColor: '#00d1b2',
            backgroundColor: 'rgba(0, 209, 178, 0.1)',
            borderWidth: 2,
            tension: 0.4,
            fill: true,
            pointRadius: 0
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                beginAtZero: true,
                max: 1,
                grid: { color: '#2d3748' },
                ticks: { color: '#8b9bb4' }
            },
            x: {
                grid: { display: false },
                ticks: { display: false }
            }
        },
        plugins: {
            legend: { display: false }
        },
        animation: { duration: 0 } // Disable animation for performance
    }
});

// State
let requestCount = 0;
const MAX_DATA_POINTS = 50;

ws.onmessage = (event) => {
    const message = JSON.parse(event.data);

    if (message.type === 'metric') {
        updateMetrics(message.data);
    } else if (message.type === 'alert') {
        addAlert(message.data);
    }
};

function updateMetrics(data) {
    // Update Counters
    requestCount++;
    document.getElementById('total-requests').textContent = requestCount;

    const errorRate = data.error_rate;
    document.getElementById('error-rate').textContent = (errorRate * 100).toFixed(2) + '%';

    // Update Chart
    const now = new Date().toLocaleTimeString();
    errorChart.data.labels.push(now);
    errorChart.data.datasets[0].data.push(errorRate);

    // Keep chart window fixed size
    if (errorChart.data.labels.length > MAX_DATA_POINTS) {
        errorChart.data.labels.shift();
        errorChart.data.datasets[0].data.shift();
    }

    errorChart.update();
}

function addAlert(data) {
    const feed = document.getElementById('alert-feed');
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert-item warning';
    alertDiv.textContent = `[${new Date().toLocaleTimeString()}] ${data.message}`;

    // Add to top
    feed.insertBefore(alertDiv, feed.firstChild);

    // Update Status Indicator
    const statusEl = document.getElementById('drift-status');
    statusEl.textContent = "DRIFT DETECTED";
    statusEl.className = "value status-alert";

    // Reset status after 5 seconds
    setTimeout(() => {
        statusEl.textContent = "STABLE";
        statusEl.className = "value status-ok";
    }, 5000);
}

// Update Clock
setInterval(() => {
    document.getElementById('timestamp').textContent = new Date().toLocaleTimeString();
}, 1000);

// Manual Phishing Check
async function checkPhishing() {
    const input = document.getElementById('manual-input');
    const resultBox = document.getElementById('manual-result');
    const resultText = document.getElementById('result-text');
    const confidenceFill = document.getElementById('confidence-fill');

    if (!input.value.trim()) return;

    // Reset UI
    resultBox.className = 'result-box hidden';

    try {
        const response = await fetch('/api/check', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: input.value })
        });

        const data = await response.json();

        // Show Result
        resultBox.className = `result-box result-${data.result.toLowerCase()}`;
        resultText.textContent = `${data.result} (${(data.confidence * 100).toFixed(0)}%)`;

        // Animate Bar
        confidenceFill.style.width = '0%';
        setTimeout(() => {
            confidenceFill.style.width = `${data.confidence * 100}%`;
        }, 100);

    } catch (error) {
        console.error('Error checking phishing:', error);
        alert('Failed to check. Ensure backend is running.');
    }
}
