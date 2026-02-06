chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.create({
        id: "saveToPulseBoard",
        title: "Save to PulseBoard",
        contexts: ["page"]
    });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === "saveToPulseBoard") {
        const url = tab.url;
        const title = tab.title;

        const signalData = {
            title: "Context Menu Save: " + title,
            description: "Saved from context menu.",
            source: "Chrome Extension Context Menu",
            url: url,
            pageTitle: title
        };

        fetch('http://localhost:18880/api/signals', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(signalData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log('Signal added via context menu:', data);
            // Optionally notify the user via a subtle notification
            chrome.notifications.create({
                type: 'basic',
                iconUrl: 'icons/icon48.png',
                title: 'PulseBoard',
                message: 'Page saved to PulseBoard successfully!'
            });
        })
        .catch(error => {
            console.error('Error adding signal via context menu:', error);
            chrome.notifications.create({
                type: 'basic',
                iconUrl: 'icons/icon48.png',
                title: 'PulseBoard',
                message: 'Failed to save page to PulseBoard: ' + error.message
            });
        });
    }
});
