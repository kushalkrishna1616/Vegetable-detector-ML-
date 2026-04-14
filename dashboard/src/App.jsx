import React, { useState, useEffect } from 'react';
import './index.css';

const GOOGLE_CLIENT_ID = "676042233490-bseaec4b9q7gtbloocbjm5ct9qnnmp0j.apps.googleusercontent.com"; // Integrated actual Client ID

function App() {
  const [view, setView] = useState('login'); 
  const [mode, setMode] = useState('checkout'); 
  const [user, setUser] = useState(null);
  
  const [items, setItems] = useState([]);
  const [revenue, setRevenue] = useState(0);
  const [currentDetection, setCurrentDetection] = useState(null);
  const [dynamicInsight, setDynamicInsight] = useState("Ready to explore!");
  const [itemDetails, setItemDetails] = useState({});
  const [isSuccess, setIsSuccess] = useState(false);
  const [receipt, setReceipt] = useState(null); // To store successful bill data

  // Helper to decode JWT without a library
  const parseJwt = (token) => {
    try {
      return JSON.parse(atob(token.split('.')[1]));
    } catch (e) {
      return null;
    }
  };

  // Initialize Google Login
  useEffect(() => {
    if (view === 'login') {
      /* global google */
      if (typeof google !== 'undefined') {
        google.accounts.id.initialize({
          client_id: GOOGLE_CLIENT_ID,
          callback: handleGoogleResponse
        });
        google.accounts.id.renderButton(
          document.getElementById("googleBtnContainer"),
          { theme: "outline", size: "large", width: "300" }
        );
      }
    }
  }, [view]);

  const handleGoogleResponse = (response) => {
    const userData = parseJwt(response.credential);
    if (userData) {
      setUser({
        name: userData.name,
        email: userData.email,
        photo: userData.picture || "👤"
      });
      setView('mode-select');
    }
  };

  const handleLogout = () => {
    setUser(null);
    setView('login');
  };

  const handleModeSelect = (selectedMode) => {
    setMode(selectedMode);
    setView('dashboard');
  };

  const handlePayment = () => {
    if (revenue <= 0) {
      alert("Your cart is empty!");
      return;
    }

    const options = {
      key: "rzp_test_RtAEhhoLIQ49vG", 
      amount: revenue * 100, 
      name: "VegDetector AI",
      description: "Bill Payment",
      image: "https://cdn-icons-png.flaticon.com/512/2153/2153788.png",
      handler: function (response) {
        setReceipt({
          id: response.razorpay_payment_id,
          date: new Date().toLocaleString(),
          items: [...items],
          total: revenue,
          user: user
        });
        setItems([]);
        setRevenue(0);
        setView('receipt');
      },
      prefill: {
        name: user?.name,
        email: user?.email,
      },
      theme: { color: "#D2B48C" },
    };

    const rzp1 = new window.Razorpay(options);
    rzp1.open();
  }  // Handle Weight/Quantity change
  const handleWeightChange = (index, newWeight) => {
    const updatedItems = [...items];
    updatedItems[index].weight = parseFloat(newWeight) || 0;
    setItems(updatedItems);

    // Recalculate Total Revenue
    const newTotal = updatedItems.reduce((acc, item) => {
      const unitPrice = parseInt(item.unitPrice.replace('₹', '').split('/')[0]);
      return acc + (unitPrice * item.weight);
    }, 0);
    setRevenue(newTotal);
  };

  // Modified Auto-log for checkout mode
  useEffect(() => {
    if (view !== 'dashboard' || mode !== 'checkout') return;

    const interval = setInterval(async () => {
      try {
        const response = await fetch('http://localhost:5000/status');
        const data = await response.json();
        
        if (data.last_item && data.last_item !== "None") {
          setCurrentDetection(data.last_item);
          setDynamicInsight(data.last_insight);
          setItemDetails(data);

          // Only add if it's not already the most recent item (prevents duplicates)
          if (data.last_item !== items[0]?.name) {
            const unitPriceVal = parseInt(data.price.replace('₹', '').split('/')[0]);
            const newItem = {
              name: data.last_item,
              unitPrice: data.price,
              weight: 1, // Default to 1kg or 1pc
              time: new Date().toLocaleTimeString()
            };
            setItems(prev => [newItem, ...prev].slice(0, 5));
            setRevenue(prev => prev + unitPriceVal);
            setIsSuccess(true);
            setTimeout(() => setIsSuccess(false), 500);
          }
        } else {
          setCurrentDetection(null);
        }
      } catch (err) { }
    }, 1200);
    return () => clearInterval(interval);
  }, [view, mode, items]);

  if (view === 'login') {
    return (
      <div className="login-container">
        <div className="login-card">
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🥗</div>
          <h1 style={{ color: 'var(--color-gold)', marginBottom: '0.5rem' }}>VegDetector AI</h1>
          <p style={{ opacity: 0.7, fontSize: '0.9rem', marginBottom: '2rem' }}>Secure Intelligent Vision Gateway</p>
          
          <div id="googleBtnContainer" style={{ display: 'flex', justifyContent: 'center' }}></div>
          
          <p style={{ marginTop: '1.5rem', fontSize: '0.7rem', opacity: 0.4 }}>
            Powered by Google Identity Services
          </p>
        </div>
      </div>
    );
  }

  if (view === 'receipt' && receipt) {
    return (
      <div className="receipt-container" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', background: '#f5f5f5', padding: '20px' }}>
        <div className="receipt-paper" style={{ background: '#FFF', width: '100%', maxWidth: '400px', padding: '40px', boxShadow: '0 15px 35px rgba(0,0,0,0.1)', borderRadius: '2px', color: '#333', fontFamily: 'monospace' }}>
          <div style={{ textAlign: 'center', borderBottom: '2px dashed #EEE', paddingBottom: '20px', marginBottom: '20px' }}>
            <h2 style={{ margin: 0 }}>VEGDETECTOR AI</h2>
            <p style={{ fontSize: '0.8rem', opacity: 0.6 }}>SMART RETAIL STATION #001</p>
          </div>
          
          <div style={{ fontSize: '0.8rem', marginBottom: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>DATE:</span> <span>{receipt.date}</span></div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>TXN ID:</span> <span>{receipt.id}</span></div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}><span>CUSTOMER:</span> <span>{receipt.user.name}</span></div>
          </div>

          <div style={{ borderBottom: '1px solid #EEE', paddingBottom: '10px', marginBottom: '10px', fontWeight: 'bold' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>ITEM</span>
              <span>QTY</span>
              <span>TOTAL</span>
            </div>
          </div>

          <div style={{ marginBottom: '20px' }}>
            {receipt.items.map((item, i) => (
              <div key={i} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem', marginBottom: '5px' }}>
                <span>{item.name}</span>
                <span>{item.weight}</span>
                <span>₹{(parseInt(item.unitPrice.replace('₹', '').split('/')[0]) * item.weight).toFixed(2)}</span>
              </div>
            ))}
          </div>

          <div style={{ borderTop: '2px dashed #EEE', paddingTop: '20px', textAlign: 'right' }}>
            <div style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>TOTAL: ₹{receipt.total.toFixed(2)}</div>
            <p style={{ fontSize: '0.7rem', opacity: 0.5, marginTop: '20px', textAlign: 'center' }}>THANK YOU FOR SHOPPING WITH US!</p>
          </div>

          <div style={{ display: 'flex', gap: '10px', marginTop: '30px' }}>
            <button onClick={() => window.print()} style={{ flex: 1, padding: '12px', background: '#333', color: '#FFF', border: 'none', borderRadius: '5px', cursor: 'pointer' }}>PRINT BILL</button>
            <button onClick={() => setView('dashboard')} style={{ flex: 1, padding: '12px', background: 'var(--color-gold)', color: '#000', border: 'none', borderRadius: '5px', fontWeight: 'bold', cursor: 'pointer' }}>NEW SCAN</button>
          </div>
        </div>
      </div>
    );
  }

  if (view === 'mode-select') {
    return (
      <div className="mode-container">
        <h1 style={{ color: 'var(--color-gold)' }}>Welcome, {user.name}</h1>
        <p style={{ opacity: 0.6 }}>Choose your experience</p>
        <div className="mode-grid">
          <div className="mode-card kids" onClick={() => handleModeSelect('kids')}>
            <div style={{ fontSize: '4rem' }}>🎒</div>
            <h2>Kids Explorer</h2>
            <p>Fun facts, colors, and nutritional magic for kids!</p>
          </div>
          <div className="mode-card checkout" onClick={() => handleModeSelect('checkout')}>
            <div style={{ fontSize: '4rem' }}>🛒</div>
            <h2>Quick Checkout</h2>
            <p>High-speed automated billing for smarter shopping.</p>
          </div>
        </div>
        <button onClick={handleLogout} style={{ marginTop: '20px', background: 'none', border: '1px solid #444', color: '#888', padding: '10px 20px', borderRadius: '20px', cursor: 'pointer' }}>Logout</button>
      </div>
    );
  }

  return (
    <div className={`app-container ${mode === 'kids' ? 'kids-mode' : ''}`}>
      <header>
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <span className="logo">{mode === 'kids' ? "🌈 Veggie Magic" : "Kushalzz AI Vision"}</span>
          <button onClick={() => setView('mode-select')} style={{ background: 'rgba(255,255,255,0.1)', border: 'none', color: '#FFF', padding: '5px 10px', borderRadius: '5px', cursor: 'pointer', fontSize: '0.7rem' }}>SWITCH MODE</button>
        </div>
        
        <div className="status-badge">
          <div className="pulse"></div>
          {mode === 'kids' ? "Learning Mode: On" : "Checkout Mode: Active"}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '0.8rem', fontWeight: 'bold' }}>{user.name}</div>
            <div style={{ fontSize: '0.6rem', opacity: 0.5 }}>{user.email}</div>
          </div>
          <img src={user.photo} alt="User" style={{ height: '35px', width: '35px', borderRadius: '50%', border: '2px solid var(--color-gold)' }} />
        </div>
      </header>

      {/* LEFT PANEL */}
      <aside className="stats-panel">
        {mode === 'kids' ? (
          <div className="discovery-card">
            <h3>Explorer Stats</h3>
            <div className="stat-card">
              <div className="stat-label">Items Found Today</div>
              <div className="stat-value">12</div>
            </div>
            <div className="stat-card" style={{ background: '#FFF3E0' }}>
              <div className="stat-label">Discovery Level</div>
              <div className="stat-value" style={{ color: '#E65100' }}>Expert 🌟</div>
            </div>
          </div>
        ) : (
          <>
            <h3>Billing Summary</h3>
            <div className={`stat-card ${isSuccess ? 'success-pulse' : ''}`}>
              <div className="stat-label">Total Amount</div>
              <div className="stat-value" style={{ color: 'var(--color-gold-bright)' }}>₹{revenue}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Items Scanned</div>
              <div className="stat-value">{items.length}</div>
            </div>
          </>
        )}
      </aside>

      {/* VIDEO PANEL */}
      <main className="feed-container">
        <img 
          src="http://127.0.0.1:5000/video_feed" 
          alt="AI Stream" 
          style={{ width: '100%', height: '100%', objectFit: 'cover' }} 
        />
        
        {/* KIDS OVERLAY */}
        {mode === 'kids' && currentDetection && (
          <div style={{ position: 'absolute', bottom: '20px', left: '20px', right: '20px' }}>
            <div className="discovery-card" style={{ border: '4px solid #FFD54F' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h2 style={{ fontSize: '2.5rem', textTransform: 'uppercase' }}>{currentDetection}!</h2>
                <div style={{ fontSize: '3rem' }}>✨</div>
              </div>
              <p style={{ fontSize: '1.2rem', fontWeight: '500' }}>{dynamicInsight}</p>
              <div style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
                <span className="fact-tag" style={{ background: '#E3F2FD', color: '#1565C0' }}>{itemDetails.calories}</span>
                <span className="fact-tag" style={{ background: '#F3E5F5', color: '#7B1FA2' }}>Color: {itemDetails.color}</span>
                <span className="fact-tag" style={{ background: '#FFF8E1', color: '#FBC02D' }}>{itemDetails.type}</span>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* RIGHT PANEL (ONLY FOR CHECKOUT) */}
      {mode === 'checkout' && (
        <aside className="inventory-panel">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h3>Shopping Cart</h3>
            <button onClick={() => {setItems([]); setRevenue(0);}} style={{ background: 'none', border: 'none', color: 'var(--color-gold)', cursor: 'pointer', fontSize: '0.7rem' }}>CLEAR</button>
          </div>
          <div className="history-list">
            {items.map((item, idx) => (
              <div className="item-row" key={idx} style={{ flexDirection: 'column', gap: '8px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%' }}>
                  <div className="item-name">{item.name}</div>
                  <div className="item-price">₹{(parseInt(item.unitPrice.replace('₹', '').split('/')[0]) * item.weight).toFixed(2)}</div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', width: '100%' }}>
                  <input 
                    type="number" 
                    value={item.weight} 
                    onChange={(e) => handleWeightChange(idx, e.target.value)}
                    style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid #444', color: '#FFF', padding: '2px 5px', width: '60px', borderRadius: '4px', fontSize: '0.8rem' }}
                    step="0.1"
                  />
                  <span style={{ fontSize: '0.7rem', opacity: 0.5 }}>Weight (Kg/Pc) @ {item.unitPrice}</span>
                </div>
              </div>
            ))}
          </div>
          <button 
            onClick={handlePayment}
            className="checkout-btn"
          >
            Pay Now (Razorpay)
          </button>
        </aside>
      )}
    </div>
  );
}

export default App;
