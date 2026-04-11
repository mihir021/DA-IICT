import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Mail, Lock, ShoppingBasket } from 'lucide-react';

/**
 * Login Page - Authenticates users and stores their token.
 * FLOW: Form Input -> FastAPI (/login) -> JWT Token -> LocalStorage -> Redirect
 */
const Login = () => {
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');

    try {
      // --- FLOW: Request Token ---
      const response = await fetch('http://localhost:8000/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      if (response.ok && data.token) {
        // --- LOGIC: Store Token ---
        // We save the token so the browser 'remembers' we are logged in
        localStorage.setItem("token", data.token);
        localStorage.setItem("user_name", data.name);
        
        // Redirect to Home page
        navigate('/');
      } else {
        setError(data.detail || "Login failed. Please check your email/password.");
      }
    } catch (err) {
      setError("Could not connect to server.");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-6">
      <div className="w-full max-w-md bg-white p-8 rounded-[2rem] editorial-shadow border border-zinc-100">
        <div className="flex flex-col items-center gap-2 mb-8">
          <div className="flex items-center gap-2 text-primary font-bold text-2xl">
            <ShoppingBasket className="w-8 h-8" />
            <span>BasketIQ</span>
          </div>
          <p className="text-zinc-500 font-medium">Welcome back, smart shopper!</p>
        </div>

        <h2 className="text-3xl font-extrabold text-on-surface mb-6 text-center">Login</h2>

        {error && <div className="bg-red-50 text-red-600 p-3 rounded-xl mb-4 text-sm font-medium">{error}</div>}

        <form onSubmit={handleLogin} className="flex flex-col gap-5">
          <div className="relative">
            <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-400" />
            <input
              type="email"
              placeholder="Email Address"
              className="w-full pl-12 pr-4 py-4 bg-zinc-50 border-none rounded-2xl focus:ring-2 focus:ring-primary/20 outline-none transition-all"
              required
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            />
          </div>

          <div className="relative">
            <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-400" />
            <input
              type="password"
              placeholder="Password"
              className="w-full pl-12 pr-4 py-4 bg-zinc-50 border-none rounded-2xl focus:ring-2 focus:ring-primary/20 outline-none transition-all"
              required
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
            />
          </div>

          <button
            type="submit"
            className="w-full emerald-gradient text-white py-4 rounded-full font-bold text-lg mt-2 transition-transform hover:scale-[1.02] active:scale-95 shadow-lg shadow-primary/20"
          >
            Sign In
          </button>
        </form>

        <p className="text-center mt-6 text-zinc-600 font-medium">
          Don't have an account? <Link to="/signup" className="text-primary font-bold">Sign Up</Link>
        </p>
      </div>
    </div>
  );
};

export default Login;
