import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Home from './pages/home/Home';
import Mobile from './pages/portfolio/component/portfolio_mobile.js';
import Portfolio from './pages/portfolio';
import Trading from './pages/trading';
import Status from './pages/status';
import { store } from './redux/store.js';
import { Provider } from 'react-redux';
import { WalletContextProvider } from './context/walletContext.jsx';
import { AddressContextProvider } from './context/addressContext.jsx';
import {Toaster} from 'react-hot-toast'

const App = () => {
  const [theme, setTheme] = useState('dark');
  const [isMobile, setIsMobile] = useState(window.innerWidth < 900); // Check initial screen width

  useEffect(() => {
    localStorage.setItem('theme', theme);
  }, [theme]);

  useEffect(() => {
    // Update isMobile state when the window is resized
    const handleResize = () => {
      setIsMobile(window.innerWidth < 900);
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  return (
    <>
    <Provider store={store}>
      <WalletContextProvider>
        <AddressContextProvider>
          <Router>
            <Routes>
              <Route exact path="/" element={<Home />} />
              <Route exact path="/trading" element={<Trading theme={theme} setTheme={setTheme} curr={'apt'} />} />
              <Route exact path="/trading/apt" element={<Trading theme={theme} setTheme={setTheme} curr={'apt'} />} />
              <Route exact path="/trading/btc" element={<Trading theme={theme} setTheme={setTheme} curr={'btc'} />} />
              <Route exact path="/trading/eth" element={<Trading theme={theme} setTheme={setTheme} curr={'eth'} />} />
              {isMobile ? (
                <Route exact path="/portfolio" element={<Mobile />} /> // Render mobile page
              ) : (
                <Route exact path="/portfolio" element={<Portfolio theme={theme} setTheme={setTheme} />} /> // Render portfolio page
              )}
              <Route exact path="/status" element={<Status />} />
            </Routes>
          </Router>
      <Toaster />
        </AddressContextProvider>
      </WalletContextProvider>
    </Provider>
    </>
  );
};

export default App;
