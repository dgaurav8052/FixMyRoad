const reportIdInput = document.getElementById('report-id');
const trackButton = document.getElementById('track-status-btn');

// Read real sequential ID from query param `rid` and show as #<id>
window.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    const rid = params.get('rid');
    if (rid) {
        reportIdInput.value = `#${rid}`;
    } else {
        reportIdInput.value = '#?';
    }
});

// Add functionality to the "Track Your Status" button
trackButton.addEventListener('click', () => {
    const reportID = reportIdInput.value;
    alert(`Navigating to status page for Report ID: ${reportID}.`);
    // Example redirect:
    // window.location.href = `/status?id=${encodeURIComponent(reportID.replace('#',''))}`;
});