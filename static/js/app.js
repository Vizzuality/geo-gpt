
// Initialize the map
let map;
function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
      center: { lat: 0, lng: 0 },
      zoom: 2,
      disableDefaultUI: true, // Disable all default UI controls
      zoomControl: true, // Enable only the zoom control
    });
  }

// Add event listener to the input field
const locationInput = document.getElementById("location");
locationInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    geocodeLocation(event.target.value);
  }
});

function addGeeLayer(result) {
    // Add GEE layer to the Google Map
    const geeMapType = new google.maps.ImageMapType({
      getTileUrl: (coord, zoom) => {
        const scale = 1 << zoom;
        const x = ((coord.x % scale) + scale) % scale;
        const y = coord.y;
  
        return (
          result.map_tile_url
            .replace("{x}", x)
            .replace("{y}", y)
            .replace("{z}", zoom)
        );
      },
      tileSize: new google.maps.Size(256, 256),
      opacity: 0.7,
    });
    document.getElementById("user-console").classList.remove("invisible");

    map.overlayMapTypes.clear();
    map.overlayMapTypes.push(geeMapType);
  }

async function geocodeLocation(location) {
    try {
      const response = await fetch("/geocode", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ place: location }),
      });
      const geojson = await response.json();
  
      if (geojson && (geojson.type === "Polygon" || geojson.type === "MultiPolygon")) {
        // Wrap the GeoJSON object into a FeatureCollection
        const geojsonFeatureCollection = {
          type: "FeatureCollection",
          features: [
            {
              type: "Feature",
              properties: {},
              geometry: geojson
            }
          ]
        };
  
        // Create a polygon from the GeoJSON FeatureCollection
        const polygon = new google.maps.Data();
        polygon.addGeoJson(geojsonFeatureCollection);
  
        // Fit the map to the polygon bounds
        const bounds = new google.maps.LatLngBounds();
        polygon.forEach((feature) => {
          feature.getGeometry().forEachLatLng((latLng) => bounds.extend(latLng));
        });
        map.fitBounds(bounds);
  
        // Call analyzeArea with the GeoJSON object
        analyzeArea({ geometry: geojson });
        document.getElementById("user-console").classList.remove("invisible");
      } else {
        console.error("Error: Invalid geocoding result");
      }
    } catch (error) {
      console.error("Error: Geocoding request failed", error);
    }
  }
  
  async function analyzeArea(geojson) {
    try {
      const response = await fetch("/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(geojson),
      });
      const result = await response.json();
  
      if (result) {
        console.log(result);
        addGeeLayer(result);
        describeStats(result); // Call describeStats with the result stats
        localStorage.setItem('analysisResult', JSON.stringify(result)); // Store the result
      } else {
        console.error("Error: Invalid analysis result");
      }
    } catch (error) {
      console.error("Error: Analysis request failed", error);
    }
  }
  

  function streamText(html, element) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message'); // Add a class to style the message element
    messageElement.innerHTML = html;
    element.appendChild(messageElement);
  }
  
  

  async function describeStats(stats, text = null) {
    try {
      const response = await fetch("/describe", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ stats, text }),
      });
      const result = await response.json();
  
      if (result && result.description.markdown) {
        // Remove enclosing double quotes
        const markdownText = result.description.markdown.replace(/^"|"$/g, '');
        const converter = new showdown.Converter();
        const htmlText = converter.makeHtml(markdownText);
        const chatWindow = document.getElementById("chat-window");
        streamText(htmlText, chatWindow);
      } else {
        console.error("Error: Invalid describe result");
      }
    } catch (error) {
      console.error("Error: Describe request failed", error);
    }
  }
  

  document.getElementById('send-a-message').addEventListener('keypress', async function (event) {
    if (event.key === 'Enter') {
      event.preventDefault(); // Prevent the default behavior (line break)
      const text = event.target.value; // Get the text from the textarea
      const storedStats = JSON.parse(localStorage.getItem('analysisResult')); // Retrieve the stored stats
  
      // Call describeStats with the stored stats and the text from the textarea
      await describeStats(storedStats, text);
  
      // Clear the textarea after the function call
      event.target.value = '';
    }
  });
  