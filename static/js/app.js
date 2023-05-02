
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

const chatWindow = document.getElementById("chat-window");


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
    message = `-----I must add the data layer to the map`;
      streamText(message, chatWindow, "system");

    if (!result || !result.map_tile_url) {
        console.error("Result object or map_tile_url is undefined:", result);
        return;
      }
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
    changeStateTextField("disabled", "location");
    changeStateTextField("disabled", "send-a-message");
    try {
      const response = await fetch("/geocode", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ place: location }),
      });

      message = `<b>New location: ${location}</b>`;
      streamText(message, chatWindow, "user");
      const geojson = await response.json();
      message = `-----I must set the map viewport over: ${location}`;
      streamText(message, chatWindow, "loader");
      message = `--Done`;
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
        
       message = `-----I must analyze the area`;
       streamText(message, chatWindow, "loader");
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
        console.error("I apologize, but I was unable to find the location you mentioned. Please, kindly double-check the information or provide me with more specific details.");
        streamText("I apologize, but I was unable to find the location you mentioned. Please, kindly double-check the information or provide me with more specific details.", chatWindow, "error");
        changeStateTextField("enabled", "location");    
      }
    } catch (error) {
      console.error("Error: analysis request failed", error);
      streamText("I apologize, but I was unable to find the location you mentioned. Please, kindly double-check the information or provide me with more specific details.", chatWindow, "error");
      changeStateTextField("enabled", "location");
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
      streamText("I apologize, but I couldn't analyze that area. Probably there is no relevant data at this moment or the data can be incorrect. We'll address these issues soon.", chatWindow, "error");
      console.error("I apologize, but I couldn't analyze that area. Probably there is no relevant data at this moment or the data can be incorrect. We'll address these issues soon.");
      changeStateTextField("enabled", "location");
      }
    } catch (error) {
      streamText("I apologize, but I couldn't analyze that area. Probably there is no relevant data at this moment or the data can be incorrect. We'll address these issues soon.", chatWindow, "error");
      console.error("Error: Analysis request failed", error);
      changeStateTextField("enabled", "location");
    }
  }
    
  async function describeStats(stats, text = null) {
    message = `-----I must explain the data`;
    streamText(message, chatWindow, "loader");
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
        streamText(htmlText, chatWindow, "system");
        changeStateTextField("enabled", "location");
        changeStateTextField("enabled", "send-a-message");
      } else {
        console.error("Error: Invalid describe result");
        changeStateTextField("enabled", "location");
        changeStateTextField("enabled", "send-a-message");
        streamText("Error: Invalid describe result", chatWindow, "error");
      }
    } catch (error) {
      console.error("Error: Describe request failed", error);
      changeStateTextField("enabled", "location");
      changeStateTextField("enabled", "send-a-message");
      streamText("Error: Invalid describe result", chatWindow, "error");
    }
  }
  

  document.getElementById('send-a-message').addEventListener('keypress', async function (event) {
    if (event.key === 'Enter') {
      changeStateTextField("disabled", "send-a-message");
      
      event.preventDefault(); // Prevent the default behavior (line break)
      const text = event.target.value; // Get the text from the textarea
      const storedStats = JSON.parse(localStorage.getItem('analysisResult')); // Retrieve the stored stats
  
      // Call describeStats with the stored stats and the text from the textarea
      await describeStats(storedStats, text);
      console.log(JSON.stringify({ storedStats, text }))

  
      // Clear the textarea after the function call
      event.target.value = '';
    }
  });
  
  function changeStateTextField(state, fieldId) {
    const textField = document.getElementById(fieldId);
  
    if (state === "enabled") {
      // Enable the text field
      textField.disabled = false;
      textField.classList.remove('bg-gray-100','border','border-gray-300','text-gray-900','rounded-lg','focus:ring-blue-500','focus:border-blue-500','cursor-not-allowed','dark:bg-gray-700','dark:border-gray-600','dark:placeholder-gray-400','dark:text-gray-400','dark:focus:ring-blue-500','dark:focus:border-blue-500');
    } else {
      // Disable the text field
      textField.disabled = true;
      textField.classList.add('bg-gray-100','border','border-gray-300','text-gray-900','rounded-lg','focus:ring-blue-500','focus:border-blue-500','cursor-not-allowed','dark:bg-gray-700','dark:border-gray-600','dark:placeholder-gray-400','dark:text-gray-400','dark:focus:ring-blue-500','dark:focus:border-blue-500');
    }
  }

  let messageQueue = [];
  let isProcessingMessage = false;
  
  function streamText(html, element, origin) {
    // Add the message to the queue
    messageQueue.push({ html, element, origin });
  
    // If not currently processing a message, start processing the queue
    if (!isProcessingMessage) {
      processMessageQueue();
    }
  }
  
  function processMessageQueue() {
    if (messageQueue.length === 0 && !isProcessingMessage) {
      return;
    }
  
    if (isProcessingMessage) {
      return;
    }
  
    isProcessingMessage = true;
    const { html, element, origin } = messageQueue.shift();
    const messageElement = document.createElement('div');
    let textPosition = 0;
    const blinkerId = `blinker-${Date.now()}`;
  
    // Remove the previous blinker
    const previousBlinker = document.querySelector(`[data-blinker]`);
    if (previousBlinker) {
      previousBlinker.remove();
    }
  
    // Add a class to style the message element
    if (origin === "user") {
      messageElement.classList.add('bg-gray-800', 'mt-4', 'md:mt-8', 'px-4', 'py-2');
    } else if (origin === "error"){
        messageElement.classList.add('gray-700', 'py-0', 'text-red-400');
    } else {
        messageElement.classList.add('gray-700', 'py-0');
    }
    element.appendChild(messageElement);
  
    function typeWriter() {
      if (textPosition < html.length) {
        messageElement.innerHTML = html.substring(0, textPosition + 1) + `<span data-blinker="${blinkerId}" class="blinking">\u25ae</span>`;
        textPosition++;
        element.scrollTop = element.scrollHeight;
        setTimeout(typeWriter, 3); // Adjust the typing speed here
      } else {
        isProcessingMessage = false;
  
        // Remove the last blinker only if the origin is not "loader" and there are no more messages in the queue
        if (origin !== "loader" && messageQueue.length === 0) {
          const lastBlinker = document.querySelector(`[data-blinker]`);
          if (lastBlinker) {
            lastBlinker.remove();
          }
        }
        processMessageQueue();
      }
    }
  
    // Start the typewriter effect
    typeWriter();
  }
  