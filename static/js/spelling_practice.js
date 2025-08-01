let sessionActive = window.sessionActive;
let elapsedTime = window.elapsedTime;
const wordData = window.wordData;
const synth = window.speechSynthesis;

// Dynamically get CSRF token from the form
const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

function speak(text) {
    console.log('Attempting to speak:', text);  // Debug log
    if (!text) {
        console.warn('No text to speak - wordData may be empty');
        return;
    }
    const utter = new SpeechSynthesisUtterance(text);
    synth.speak(utter);
}

function updateTimer() {
    if (sessionActive) {
        elapsedTime++;
        let minutes = Math.floor(elapsedTime / 60);
        let seconds = elapsedTime % 60;
        document.getElementById('timer').textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
}

if (sessionActive) {
    setInterval(updateTimer, 1000);
    updateTimer();
}

// Function to toggle buttons (disable before session starts)
function toggleButtons(disabled) {
    document.getElementById('hear-word').disabled = disabled;
    document.getElementById('hear-definition').disabled = disabled;
    document.getElementById('hear-sentence').disabled = disabled;
    document.getElementById('user-input').disabled = disabled;
    document.querySelector('#spelling-form button[type="submit"]').disabled = disabled;
}
toggleButtons(!sessionActive);  // Initial state

// Start session button
document.getElementById('start-session').addEventListener('click', () => {
    if (!sessionActive) {
        fetch('/users/start-session/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        }).then(response => response.json())
          .then(data => {
              if (data.status === 'success') {
                  sessionActive = true;
                  elapsedTime = 0;  // Start from 0
                  setInterval(updateTimer, 1000);
                  updateTimer();
                  toggleButtons(false);  // Enable buttons
                  document.getElementById('end-session').style.display = 'block';  // Show end button
                  alert(data.message);
                  location.reload();  // Reload to pick first word
              } else {
                  alert(data.message);
              }
          })
          .catch(error => console.error('Error starting session:', error));
    }
});

// End session button
document.getElementById('end-session').addEventListener('click', () => {
    if (sessionActive) {
        fetch('/users/end-session/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        }).then(response => response.json())
          .then(data => {
              if (data.status === 'success') {
                  sessionActive = false;
                  toggleButtons(true);  // Disable buttons
                  document.getElementById('end-session').style.display = 'none';  // Hide end button
                  alert(data.message);
                  location.reload();  // Reload to reset
              } else {
                  alert(data.message);
              }
          })
          .catch(error => console.error('Error ending session:', error));
    }
});

// Audio buttons
document.getElementById('hear-word').addEventListener('click', () => speak(wordData.word));
document.getElementById('hear-definition').addEventListener('click', () => speak(wordData.definition));
document.getElementById('hear-sentence').addEventListener('click', () => speak(wordData.sentence));
