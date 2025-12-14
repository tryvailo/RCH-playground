import { useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { MapPin } from 'lucide-react';

// Fix for default marker icons in React-Leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

interface MapViewProps {
  latitude: number;
  longitude: number;
  address?: string;
  postcode?: string;
  zoom?: number;
  height?: string;
  showMultipleMarkers?: Array<{
    lat: number;
    lon: number;
    label: string;
  }>;
  apiKey?: string; // OS Maps API key (uses OS Places key if not provided)
}

// Component to handle map view updates
function MapViewUpdater({ lat, lon, zoom }: { lat: number; lon: number; zoom: number }) {
  const map = useMap();
  
  useEffect(() => {
    map.setView([lat, lon], zoom);
  }, [lat, lon, zoom, map]);
  
  return null;
}

export default function MapView({
  latitude,
  longitude,
  address,
  postcode,
  zoom = 15,
  height = '400px',
  showMultipleMarkers,
  apiKey
}: MapViewProps) {
  const mapRef = useRef<L.Map | null>(null);
  
  // OS Maps API key - use provided key or default (same as OS Places)
  const osMapsApiKey = apiKey || '4rt8r3Hnr6W4PreGYYtClGmmxix1ICTz';
  
  // OS Maps Road layer URL (Web Mercator EPSG:3857)
  // Road layer is best for care homes as it shows:
  // - Detailed roads and transport infrastructure
  // - Buildings and addresses clearly
  // - Urban infrastructure (shops, healthcare, amenities)
  // - Better suited for walkability and accessibility analysis
  const osMapsTileUrl = `https://api.os.uk/maps/raster/v1/zxy/Road_3857/{z}/{x}/{y}.png?key=${osMapsApiKey}`;

  // Create custom icon
  const customIcon = L.icon({
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    tooltipAnchor: [16, -28],
    shadowSize: [41, 41]
  });

  if (!latitude || !longitude) {
    return (
      <div className="w-full bg-gray-100 rounded-lg flex items-center justify-center" style={{ height }}>
        <div className="text-center text-gray-500">
          <MapPin className="w-12 h-12 mx-auto mb-2 opacity-50" />
          <p>No coordinates available</p>
        </div>
      </div>
    );
  }

  const markers = showMultipleMarkers && showMultipleMarkers.length > 0
    ? showMultipleMarkers
    : [{ lat: latitude, lon: longitude, label: address || postcode || 'Location' }];

  return (
    <div className="w-full rounded-lg overflow-hidden border border-gray-300 shadow-sm" style={{ height }}>
      <MapContainer
        center={[latitude, longitude]}
        zoom={zoom}
        style={{ height: '100%', width: '100%' }}
        scrollWheelZoom={true}
        ref={mapRef}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.ordnancesurvey.co.uk/">Ordnance Survey</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url={osMapsTileUrl}
          maxZoom={19}
        />
        <MapViewUpdater lat={latitude} lon={longitude} zoom={zoom} />
        
        {markers.map((marker, index) => (
          <Marker
            key={index}
            position={[marker.lat, marker.lon]}
            icon={customIcon}
          >
            <Popup>
              <div className="p-2">
                <div className="font-semibold text-sm">{marker.label}</div>
                {postcode && (
                  <div className="text-xs text-gray-600 mt-1">Postcode: {postcode}</div>
                )}
                <div className="text-xs text-gray-500 mt-1">
                  {marker.lat.toFixed(6)}, {marker.lon.toFixed(6)}
                </div>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}

