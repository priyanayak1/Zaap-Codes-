let map = L.map('map').setView([32.1656, -82.9001], 6); // Georgia center

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

let boundaryLayer;

// Attach lookup() to form submit
// document.getElementById('lookupForm').addEventListener('submit', function (e) {
//   e.preventDefault(); // prevent page reload
//   lookup();
// });

function lookup() {
  const address = document.getElementById('address').value;

  fetch('/lookup', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ address })
  })
    .then(res => res.json())
    .then(data => {
      console.log("📦 Response data:", data);
    
      // if (!data || data.jurisdiction === "No county found" || !data.geojson) {
      //   alert("❌ Could not find jurisdiction.");
      //   return;
      // }
    
      // if (boundaryLayer) map.removeLayer(boundaryLayer);

    
      // document.getElementById('result').innerText = `Jurisdiction: ${data.jurisdiction}`;
      // const geojson = JSON.parse(data.geojson);
      // boundaryLayer = L.geoJSON(geojson).addTo(map);
      // map.fitBounds(boundaryLayer.getBounds());
    })
    .catch(err => {
      console.error("❌ Error in fetch:", err);
      alert('❌ Error finding jurisdiction.');
      console.error(err);
    });
}

// CHAT STUFF
document.getElementById('send-btn').addEventListener('click', sendMessage);
document.getElementById('chat-input').addEventListener('keypress', function (e) {
  if (e.key === 'Enter') sendMessage();
});

function toggleChat() {
  let chatBody = document.getElementById('chat-body');
  chatBody.style.display = chatBody.style.display === 'none' ? 'block' : 'none';
}

function sendMessage() {
  let inputField = document.getElementById('chat-input');
  let message = inputField.value.trim();
  if (!message) return;

  appendMessage('user', message);
  inputField.value = '';

  // Send message to backend
  fetch('/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message })
  })
    .then(res => res.json())
    .then(data => {
      console.log("✅ Chatbot Response:", data); // Debugging
      appendMessage('bot', data.response);
    })
    .catch(err => {
      console.error("❌ Fetch Error:", err);
      appendMessage('bot', '❌ Error getting response.');
    });
}

function appendMessage(sender, text) {
  let chatMessages = document.getElementById('chat-messages');
  let messageDiv = document.createElement('div');
  messageDiv.classList.add(sender === 'user' ? 'user-message' : 'bot-message');
  messageDiv.innerText = text;
  chatMessages.appendChild(messageDiv);
  chatMessages.scrollTop = chatMessages.scrollHeight; // Scroll to latest message
}

