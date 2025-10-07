
map = null;
marker = null;
dblclicker = null;

function getCurrentPosition() {
  return new Promise( (resolve, reject) => {
    navigator.geolocation.getCurrentPosition(
      position => resolve(position),
      error => reject(error),
      {
        timeout: 5*1000,
        enableHighAccuracy: true
      }
    )
  })
}

function createMapButton(map, label, action, position) {
  if (!position) {
    position = google.maps.ControlPosition.TOP_RIGHT;
  }
  const button = document.createElement("div");
  button.setAttribute('class', 'map-button');
  button.innerHTML = label
  button.onclick = action;
  const wrap = document.createElement("div");
  wrap.setAttribute("class", "map-button-wrap")
  wrap.appendChild(button);
  map.controls[position].push(wrap);
  return button;
}

let meCircle;
let accCircle;

MapFindMeButton = function (map) {
  return createMapButton(map, `<span title="Here" style="font-size:xx-large">\u{2316}</span>`, async () => {
    let position
    try {
      position = await getCurrentPosition();
    } catch (e) {
      alert("Unable to get your location. Please confirm Location Services are enabled and allow this site to access your location.");
      //position = {coords:{latitude:32.5468,longitude:-84.3750, accuracy: 2}}
      return
    }

    let pos = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);

    if (meCircle) {
      meCircle.setMap(null);
    }
    if (accCircle) {
      accCircle.setMap(null);
    }
    
    accCircle = new google.maps.Circle({
      strokeColor: "#3333FF",
      strokeOpacity: 0.8,
      strokeWeight: 2,
      fillColor: "#3333FF",
      fillOpacity: 0.3,
      clickable: false,
      map,
      center: pos,
      radius: Math.min(200, position.coords.accuracy)/2
    });

    meCircle = new google.maps.Circle({
      strokeColor: "#FFFFFF",
      strokeOpacity: 0.8,
      strokeWeight: 2,
      fillColor: "#FFFFFF",
      fillOpacity: 0.3,
      clickable: false,
      map,
      center: pos,
      radius: 5,
    });
    
    map.panTo(pos);
  })
}

async function createMap() {
  const { Map, InfoWindow } = await google.maps.importLibrary("maps");
  map = new Map(document.getElementById("map-canvas"), {
    zoom: 17,
    mapId: '165a88552a1b4169',
    mapTypeId: 'satellite',
    mapTypeControlOptions: {
      style: google.maps.MapTypeControlStyle.DROPDOWN_MENU,
      mapTypeIds: ["satellite", "roadmap", "terrain"],
    },
    streetViewControl: false,
    fullscreenControl: false,
    disableDoubleClickZoom: true
  });

  setMarker();
  MapFindMeButton(map);
}

window.createMap = createMap;


async function setMarker() {
  const { PinElement, AdvancedMarkerElement } = await google.maps.importLibrary("marker");

  let formLat = document.getElementById("SiteLat");
  let formLng = document.getElementById("SiteLon");
  function updateForm(lat, lng) {
    formLat.value = lat;
    formLng.value = lng;
  }
  
  let position;

  if (formLat.value) {
    loc = new google.maps.LatLng(formLat.value, formLng.value);
  } else {
    try {
      position = await getCurrentPosition()
    } catch (e) {
      return
    }
    loc = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
    updateForm(loc.lat(), loc.lng());
  }

  map.panTo(loc)
    
  
  const pin = new PinElement({
    background: "#aaf",
    borderColor: "#333",
    glyphColor: "#333"
  });
  
  if(marker) {
    marker.map = null;
  }
  
  marker = new AdvancedMarkerElement({
    map,
    position: loc,
    content: pin.element,
    gmpDraggable: true
  });
  
  let moved = (event) => {
    updateForm(marker.position.lat, marker.position.lng)
    map.panTo(marker.position);
  }
  marker.addListener("dragend", moved);
  
  dblclicker = map.addListener("dblclick", (ev) => {
    marker.position = ev.latLng;
    moved()
  });
  
}
