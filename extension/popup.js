document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('signalForm');
    const statusDiv = document.getElementById('status');

    form.addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent default form submission

        const title = document.getElementById('title').value;
        const description = document.getElementById('description').value;

        // Get current active tab's URL and title
        chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
            const currentTab = tabs[0];
            const url = currentTab.url;
            const tabTitle = currentTab.title;

            const signalData = {
                title: title,
                description: description,
                source: "Chrome Extension Quick Add",
                url: url,
                pageTitle: tabTitle
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
                statusDiv.textContent = 'Signal added successfully!';
                statusDiv.style.color = 'green';
                console.log('Signal added:', data);
                // Optionally clear the form or close the popup
                form.reset();
                setTimeout(() => { window.close(); }, 1500); // Close popup after 1.5 seconds
            })
            .catch(error => {
                statusDiv.textContent = 'Error adding signal: ' + error.message;
                statusDiv.style.color = 'red';
                console.error('Error:', error);
            });
        });
    });
});
