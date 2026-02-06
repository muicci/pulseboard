document.addEventListener('DOMContentLoaded', () => {
    const API_URL = 'http://localhost:18880/api/dashboard-data';
    const FETCH_INTERVAL = 30000; // 30 seconds

    // Elements to update
    const statSignals = document.getElementById('stat-signals');
    const statActions = document.getElementById('stat-actions');
    const statEvents = document.getElementById('stat-events');
    const statEmails = document.getElementById('stat-emails');
    const signalFeedContent = document.getElementById('signal-feed-content');
    const calendarContent = document.getElementById('calendar-content');
    const emailDigestContent = document.getElementById('email-digest-content');

    const defaultDashboardData = {
        stats: {
            totalSignals: 0,
            pendingActions: 0,
            upcomingEvents: 0,
            emailsProcessed: 0
        },
        signalFeed: [
            { id: 's1', type: 'alert', title: 'Critical System Anomaly', description: 'Unusual activity detected in core network infrastructure.', timestamp: '2 minutes ago', icon: '🚨' },
            { id: 's2', type: 'info', title: 'New AI Model Deployed', description: 'Version 3.1 of sentiment analysis model is now active.', timestamp: '15 minutes ago', icon: '✨' },
            { id: 's3', type: 'warning', title: 'High Traffic Spike', description: 'Web traffic exceeded 200% average. Monitoring for DDoS.', timestamp: '1 hour ago', icon: '📈' }
        ],
        calendarEvents: [
            { id: 'c1', title: 'Project X Review', time: 'Today, 2:00 PM', location: 'Meeting Room 3', icon: '🗓️' },
            { id: 'c2', title: 'Team Sync Call', time: 'Tomorrow, 9:00 AM', location: 'Virtual', icon: '📞' },
            { id: 'c3', title: 'Client Demo Prep', time: 'Feb 10, 11:00 AM', location: 'Office', icon: '💡' }
        ],
        emailDigest: [
            { id: 'e1', subject: 'Weekly AI Performance Report', sender: 'Analytics Bot', preview: 'Overview of last week\'s AI model accuracy and efficiency...', icon: '📊' },
            { id: 'e2', subject: 'Urgent: Security Patch Required', sender: 'Security Team', preview: 'Critical vulnerability detected. Please apply patch immediately...', icon: '🛡️' },
            { id: 'e3', subject: 'New Feature Request: PulseBoard', sender: 'Product Team', preview: 'Summary of user feedback regarding new dashboard features...', icon: '🚀' }
        ]
    };

    async function fetchDashboardData() {
        try {
            const response = await fetch(API_URL);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            updateDashboard(data);
        } catch (error) {
            console.error('Error fetching dashboard data:', error);
            // Fallback to default data or show error message
            updateDashboard(defaultDashboardData);
            signalFeedContent.innerHTML = '<p class="loading-message error-message">Failed to fetch live data. Displaying sample data.</p>';
        }
    }

    function updateDashboard(data) {
        // Update Stats Bar
        statSignals.textContent = data.stats.totalSignals.toLocaleString();
        statActions.textContent = data.stats.pendingActions.toLocaleString();
        statEvents.textContent = data.stats.upcomingEvents.toLocaleString();
        statEmails.textContent = data.stats.emailsProcessed.toLocaleString();

        // Update Signal Feed
        signalFeedContent.innerHTML = ''; // Clear previous content
        if (data.signalFeed && data.signalFeed.length > 0) {
            data.signalFeed.forEach(signal => {
                const signalItem = document.createElement('div');
                signalItem.className = 'signal-feed-item';
                signalItem.innerHTML = `
                    <div class="signal-icon">${signal.icon || '💬'}</div>
                    <div class="signal-content">
                        <h4>${signal.title}</h4>
                        <p>${signal.description}</p>
                        <div class="signal-meta">${signal.timestamp}</div>
                    </div>
                `;
                signalFeedContent.appendChild(signalItem);
            });
        } else {
            signalFeedContent.innerHTML = '<p class="loading-message">No new signals.</p>';
        }


        // Update Calendar Events
        calendarContent.innerHTML = ''; // Clear previous content
        if (data.calendarEvents && data.calendarEvents.length > 0) {
            data.calendarEvents.forEach(event => {
                const eventItem = document.createElement('div');
                eventItem.className = 'signal-feed-item'; // Re-using style for consistency
                eventItem.innerHTML = `
                    <div class="signal-icon">${event.icon || '🗓️'}</div>
                    <div class="signal-content">
                        <h4>${event.title}</h4>
                        <p>${event.time} ${event.location ? ' - ' + event.location : ''}</p>
                    </div>
                `;
                calendarContent.appendChild(eventItem);
            });
        } else {
            calendarContent.innerHTML = '<p class="loading-message">No upcoming events.</p>';
        }


        // Update Email Digest
        emailDigestContent.innerHTML = ''; // Clear previous content
        if (data.emailDigest && data.emailDigest.length > 0) {
            data.emailDigest.forEach(email => {
                const emailItem = document.createElement('div');
                emailItem.className = 'signal-feed-item'; // Re-using style for consistency
                emailItem.innerHTML = `
                    <div class="signal-icon">${email.icon || '📧'}</div>
                    <div class="signal-content">
                        <h4>${email.subject}</h4>
                        <p><strong>From:</strong> ${email.sender}</p>
                        <p>${email.preview}</p>
                    </div>
                `;
                emailDigestContent.appendChild(emailItem);
            });
        } else {
            emailDigestContent.innerHTML = '<p class="loading-message">No new emails in digest.</p>';
        }
    }

    // Initial fetch
    fetchDashboardData();

    // Set up polling
    setInterval(fetchDashboardData, FETCH_INTERVAL);
});
