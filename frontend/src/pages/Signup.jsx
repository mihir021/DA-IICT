import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { User, Mail, Lock, ShoppingBasket } from 'lucide-react';

/**
 * Signup Page - Allows new users to create an account.
 * FLOW: Form Input -> Validation -> FastAPI (/signup) -> Success Response
 */
const Signup = () => {
  const [formData, setFormData] = useState({ name: '', email: '', password: '' });
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSignup = async (e) => {
    e.preventDefault();
    setError('');

    // --- SIMPLE VALIDATION ---
    if (formData.password.length < 6) {
      setError("Password must be at least 6 characters.");
      return;
    }

    try {
      // --- FLOW: React to FastAPI ---
      const response = await fetch('http://localhost:8000/api/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      if (response.ok) {
        // Redirect to login after successful signup
        navigate('/login');
      } else {
        setError(data.detail || "Signup failed");
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
          <p className="text-zinc-500 font-medium">Join the smart shopping community</p>
        </div>

        <h2 className="text-3xl font-extrabold text-on-surface mb-6 text-center">Create Account</h2>

        {error && <div className="bg-red-50 text-red-600 p-3 rounded-xl mb-4 text-sm font-medium">{error}</div>}

        <form onSubmit={handleSignup} className="flex flex-col gap-5">
          <div className="relative">
            <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-400" />
            <input
              type="text"
              placeholder="Full Name"
              className="w-full pl-12 pr-4 py-4 bg-zinc-50 border-none rounded-2xl focus:ring-2 focus:ring-primary/20 outline-none transition-all"
              required
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            />
          </div>

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
              placeholder="Password (min 6 characters)"
              className="w-full pl-12 pr-4 py-4 bg-zinc-50 border-none rounded-2xl focus:ring-2 focus:ring-primary/20 outline-none transition-all"
              required
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
            />
          </div>

          <button
            type="submit"
            className="w-full emerald-gradient text-white py-4 rounded-full font-bold text-lg mt-2 transition-transform hover:scale-[1.02] active:scale-95 shadow-lg shadow-primary/20"
          >
            Sign Up
          </button>
        </form>

        <p className="text-center mt-6 text-zinc-600 font-medium">
          Already have an account? <Link to="/login" className="text-primary font-bold">Login</Link>
        </p>
      </div>
    </div>
  );
};

export default Signup;
