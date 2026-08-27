import { useState } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

const getSeverityColor = (severity) => {
  switch (severity) {
    case 'severe': return '#ef4444'; // Red
    case 'very-poor': return '#f97316'; // Orange
    case 'poor': return '#f59e0b'; // Yellow
    case 'moderate': return '#10b981'; // Green
    default: return '#3b82f6'; // Blue
  }
};

export default function MapPanel({ hotspots = [], label = 'Delhi NCR — hotspot map' }) {
  const [isExpanded, setIsExpanded] = useState(false);

  const wrapperStyle = isExpanded
    ? {
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        zIndex: 9999,
        background: '#16232a',
        display: 'flex',
        flexDirection: 'column',
      }
    : {
        width: 340,
        height: '100%',
        minHeight: 400,
        flexShrink: 0,
        borderRadius: 'var(--radius-xl)',
        overflow: 'hidden',
        background: '#16232a',
        position: 'relative',
        cursor: 'pointer',
      };

  const mapStyle = {
    flex: 1,
    width: '100%',
    height: '100%',
    minHeight: 400,
  };

  const closeButtonStyle = {
    position: 'absolute',
    top: 20,
    right: 20,
    zIndex: 10000,
    padding: '8px 16px',
    background: '#ef4444',
    color: '#fff',
    border: 'none',
    borderRadius: 8,
    cursor: 'pointer',
    fontWeight: 'bold',
  };

  const legendStyle = {
    position: 'absolute',
    bottom: 20,
    left: 20,
    zIndex: 10000,
    background: 'rgba(22, 35, 42, 0.9)',
    padding: '12px',
    borderRadius: '8px',
    color: '#fff',
    fontSize: 12,
    pointerEvents: 'none',
  };

  const expandHintStyle = {
    position: 'absolute',
    top: 10,
    right: 10,
    zIndex: 400,
    background: 'rgba(0,0,0,0.6)',
    color: '#fff',
    padding: '4px 8px',
    borderRadius: 4,
    fontSize: 12,
    pointerEvents: 'none',
  };

  return (
    <div className="map-panel" style={wrapperStyle}>
      {!isExpanded && (
        <div style={expandHintStyle}>Click to Expand Map</div>
      )}
      
      {isExpanded && (
        <button style={closeButtonStyle} onClick={() => setIsExpanded(false)}>
          Close Map
        </button>
      )}

      {/* Wrapping in a div that handles the onClick for expansion if not expanded */}
      <div 
        style={{ width: '100%', height: '100%' }}
        onClick={() => !isExpanded && setIsExpanded(true)}
      >
        <MapContainer 
          key={isExpanded ? 'full' : 'inline'}
          center={[28.6139, 77.2090]}
          zoom={isExpanded ? 11 : 9}
          scrollWheelZoom={isExpanded}
          dragging={isExpanded}
          style={mapStyle}
          zoomControl={isExpanded}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          />
          {hotspots.map((spot, idx) => (
            <CircleMarker
              key={idx}
              center={[spot.lat, spot.lon]}
              pathOptions={{
                fillColor: getSeverityColor(spot.severity),
                color: getSeverityColor(spot.severity),
                fillOpacity: spot.severity === 'severe' ? 0.85 : 0.65,
                weight: spot.severity === 'severe' ? 2 : 1,
              }}
              radius={isExpanded
                ? (spot.severity === 'severe' ? 18 : spot.severity === 'very-poor' ? 14 : 10)
                : (spot.severity === 'severe' ? 11 : spot.severity === 'very-poor' ? 8 : 6)
              }
            >
              <Popup>
                <strong>{spot.name}</strong><br/>
                AQI: <strong>{spot.aqi}</strong><br/>
                Severity: {spot.severity}
              </Popup>
            </CircleMarker>
          ))}
        </MapContainer>
      </div>

      <div style={legendStyle}>
        <h4 style={{ margin: '0 0 8px 0', fontSize: 13 }}>AQI Legend</h4>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4 }}>
          <span style={{ width: 12, height: 12, borderRadius: '50%', background: '#10b981' }}></span> Moderate (≤100)
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4 }}>
          <span style={{ width: 12, height: 12, borderRadius: '50%', background: '#f59e0b' }}></span> Poor (101-200)
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4 }}>
          <span style={{ width: 12, height: 12, borderRadius: '50%', background: '#f97316' }}></span> Very Poor (201-300)
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{ width: 12, height: 12, borderRadius: '50%', background: '#ef4444' }}></span> Severe (>300)
        </div>
      </div>
    </div>
  );
}
