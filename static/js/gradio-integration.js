// This script is loaded in the Gradio interface to receive messages from the parent page

// Listen for messages from the parent window (dashboard)
window.addEventListener('message', function(event) {
    // Make sure the message is from our parent window
    if (event.source !== window.parent) return;
    
    console.log('Received message from parent:', event.data);
    
    // Handle parameter updates
    if (event.data.type === 'updateParams') {
        updateGradioComponents(event.data.days, event.data.preferences);
    }
});

// Function to update Gradio components with the received parameters
function updateGradioComponents(days, preferences) {
    console.log('Updating Gradio components with:', days, preferences);
    
    // Wait for Gradio to fully initialize
    setTimeout(() => {
        try {
            // Find the days slider in Gradio interface
            const daysSliders = document.querySelectorAll('input[type="range"]');
            if (daysSliders.length > 0) {
                // Assuming the first slider is for days
                const daysSlider = daysSliders[0];
                daysSlider.value = days;
                
                // Trigger change event to update Gradio's internal state
                const event = new Event('change', { bubbles: true });
                daysSlider.dispatchEvent(event);
                console.log('Updated days slider to:', days);
            } else {
                console.log('Days slider not found');
            }
            
            // Find the preferences checkboxes in Gradio interface
            const checkboxes = document.querySelectorAll('input[type="checkbox"]');
            if (checkboxes.length > 0) {
                console.log('Found checkboxes:', checkboxes.length);
                
                // Reset all checkboxes first
                checkboxes.forEach(checkbox => {
                    checkbox.checked = false;
                });
                
                // Check the ones that match our preferences
                checkboxes.forEach(checkbox => {
                    const label = checkbox.parentElement.textContent.trim();
                    console.log('Checkbox label:', label);
                    if (preferences.includes(label)) {
                        checkbox.checked = true;
                        
                        // Trigger change event
                        const event = new Event('change', { bubbles: true });
                        checkbox.dispatchEvent(event);
                        console.log('Checked checkbox:', label);
                    }
                });
            } else {
                console.log('Checkboxes not found');
            }
        } catch (error) {
            console.error('Error updating Gradio components:', error);
        }
    }, 2000); // Wait 2 seconds for Gradio to initialize
}

// Notify parent when Gradio is fully loaded
window.addEventListener('load', function() {
    console.log('Gradio iframe loaded');
    
    // Wait a bit for Gradio to initialize
    setTimeout(() => {
        console.log('Notifying parent that Gradio is ready');
        window.parent.postMessage({
            type: 'gradioLoaded',
            status: 'ready'
        }, '*');
    }, 2000);
}); 