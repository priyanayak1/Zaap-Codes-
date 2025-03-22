let map = L.map('map').setView([32.1656, -82.9001], 6); // Georgia center

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

let boundaryLayer;

// Attach lookup() to form submit
document.getElementById('lookupForm').addEventListener('submit', function (e) {
  e.preventDefault(); // prevent page reload
  lookup();
});

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
    
      if (!data || data.jurisdiction === "No county found" || !data.geojson) {
        alert("❌ Could not find jurisdiction.");
        return;
      }
    
      if (boundaryLayer) map.removeLayer(boundaryLayer);
    
      document.getElementById('result').innerText = `Jurisdiction: ${data.jurisdiction}`;
    
      // const codeList = document.getElementById('codes');
      // codeList.innerHTML = '';
      
      // if (data.codes && Array.isArray(data.codes)) {
      //   data.codes.forEach(code => {
      //     const li = document.createElement('li');
      //     li.innerText = code;
      //     codeList.appendChild(li);
      //   });
      // }
    
      const geojson = JSON.parse(data.geojson);
      boundaryLayer = L.geoJSON(geojson).addTo(map);
      map.fitBounds(boundaryLayer.getBounds());
    })
    .catch(err => {
      console.error("❌ Error in fetch:", err);
      alert('❌ Error finding jurisdiction.');
      console.error(err);
    });
}

