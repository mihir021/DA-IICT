import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Signup from './pages/Signup';
import Login from './pages/Login';
import Home from './pages/Home';
import Profile from './pages/Profile';

/**
 * App.jsx - Main Routing file.
 * We use 'react-router-dom' to switch between different pages.
 */
function App() {
  return (
    <Router>
      <Routes>
        {/* PUBLIC ROUTES */}
        <Route path="/signup" element={<Signup />} />
        <Route path="/login" element={<Login />} />
        
        {/* PRIVATE ROUTES (Home & Profile) */}
        <Route path="/" element={<Home />} />
        <Route path="/profile" element={<Profile />} />
        
        {/* FALLBACK: If someone typed a wrong URL, send to Home */}
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </Router>
  );
}

export default App;
