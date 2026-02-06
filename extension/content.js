// content.js
// Listen for a keyboard shortcut (e.g., Alt+Shift+S) to capture the whole page as a signal
document.addEventListener('keydown', function(event) {
  // Check for Alt+Shift+S
  if (event.altKey && event.shiftKey && event.key === 'S') {
    event.preventDefault(); // Prevent default behavior

    // Prepare signal data for the current page
    const signalData = {
      type: 'page_capture_hotkey',
      source: window.location.href,
      data: {
        url: window.location.href,
        title: document.title,
        selected_text: null, // No selection via hotkey
        timestamp: new Date().toISOString(),
        captured_via: 'hotkey'
      }
    };

    // Send the signal data to the background script
    chrome.runtime.sendMessage({action: 'sendSignal', signal: signalData});
  }
});

// Receive confirmation from background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'signalSent') {
    console.log('Signal successfully sent to backend via hotkey.');
    // Optionally show a visual feedback on the page
    alert('PulseBoard Signal Captured via Hotkey!');
  }
});
