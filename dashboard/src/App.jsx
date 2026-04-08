import React, { useState, useEffect } from 'react';
import './index.css';

function App() {
  const [items, setItems] = useState([
    { name: 'Red Onion', price: '₹35', time: '12:45:01' },
    { name: 'Fresh Basil', price: '₹20', time: '12:44:12' },
    { name: 'Bell Pepper', price: '₹60', time: '12:43:55' },
  ]);

  const [revenue, setRevenue] = useState(1280.50);
  const [itemsCount, setItemsCount] = useState(12);
  const [currentDetection, setCurrentDetection] = useState("Scanning...");
  const [dynamicInsight, setDynamicInsight] = useState("Place a fruit or vegetable in front of the camera.");

  // Fetch real-time status from Flask
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const response = await fetch('http://localhost:5000/status');
        const data = await response.json();
        if (data.last_item && data.last_item !== "None") {
          setCurrentDetection(data.last_item);
          setDynamicInsight(data.last_insight);
        }
      } catch (err) {
        console.error("Vision Engine Offline");
      }
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="app-container">
      <header>
        <span className="logo">Kushalzz AI Vision Assistant</span>
        <div className="status-badge">
          <div className="pulse"></div>
          AI System Online
        </div>
      </header>

      {/* Left Sidebar: Real-time Stats */}
      <aside className="stats-panel">
        <h3>Vision Analytics</h3>
        
        <div className="stat-card">
          <div className="stat-label">Daily Revenue</div>
          <div className="stat-value" style={{ color: 'var(--color-gold-bright)' }}>₹{revenue.toFixed(2)}</div>
          <div className="stat-label" style={{ color: 'var(--color-accent)' }}>+12% vs Yesterday</div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Active Detection</div>
          <div className="stat-value">{currentDetection}</div>
          <div className="stat-label">Tracking...</div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Neural Engine</div>
          <div className="stat-value" style={{ fontSize: '1.2rem' }}>Hybrid v3.0</div>
          <div className="stat-label">COCO + OIV7 Active</div>
        </div>

        <div className="stat-card">
          <div className="stat-label">AI Nutrition Insight</div>
          <div style={{ fontSize: '0.85rem', color: 'var(--color-gold)', marginTop: '0.5rem', fontStyle: 'italic' }}>
            "{dynamicInsight}"
          </div>
        </div>
      </aside>

      {/* Middle: Live Video Feed */}
      <main className="feed-container">
        <div className="feed-overlay">
          <div style={{ position: 'absolute', top: '20px', left: '20px', fontSize: '0.8rem', color: 'rgba(255,255,255,0.4)' }}>
            CAM_01 / REALTIME_ANALYSIS / 480P_OPTIMIZED
          </div>
          <div style={{ position: 'absolute', bottom: '20px', right: '20px', color: 'var(--color-gold)' }}>
            [ FRUIT & VEG ONLY ]
          </div>
        </div>
        
        {/* Real MJPEG Stream from Flask */}
        <img 
          src="http://localhost:5000/video_feed" 
          alt="AI Stream" 
          style={{ width: '100%', height: '100%', objectFit: 'cover' }} 
          onError={(e) => {
            e.target.style.display = 'none';
            e.target.nextSibling.style.display = 'flex';
          }}
        />
        
        {/* Placeholder if stream is offline */}
        <div style={{ width: '100%', height: '100%', display: 'none', alignItems: 'center', justifyContent: 'center', background: '#080808' }}>
          <div style={{ textAlign: 'center', color: 'rgba(210, 180, 140, 0.4)' }}>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>👁️</div>
            <div>CONNECT TO VISION ENGINE</div>
            <div style={{ fontSize: '0.7rem', marginTop: '10px' }}>RUN `py streaming_server.py`</div>
          </div>
        </div>
      </main>

      {/* Right Sidebar: History / Inventory */}
      <aside className="inventory-panel">
        <h3>Recent Detections</h3>
        <div className="history-list">
          {items.map((item, idx) => (
            <div className="item-row" key={idx}>
              <div>
                <div className="item-name">{item.name}</div>
                <div style={{ fontSize: '0.7rem', opacity: 0.5 }}>{item.time}</div>
              </div>
              <div className="item-price">{item.price}</div>
            </div>
          ))}
        </div>
        
        <button style={{ 
          width: '100%', 
          marginTop: '2rem', 
          padding: '1rem', 
          background: 'linear-gradient(135deg, var(--color-gold), #8B733E)',
          color: '#000',
          border: 'none',
          borderRadius: '8px',
          fontWeight: '700',
          cursor: 'pointer',
          textTransform: 'uppercase',
          letterSpacing: '1px'
        }}>
          Process Bill (INR)
        </button>
      </aside>
    </div>
  );
}

export default App;
