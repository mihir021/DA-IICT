import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { User, Mail, LogOut, ShoppingBasket, ShieldCheck } from 'lucide-react';

/**
 * Profile Page - Shows private user information.
 * FLOW: Check Token -> FastAPI (/profile) with Header -> Display Data
 */
const Profile = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    // --- FLOW: Data Fetching with Token ---
    const fetchProfile = async () => {
      const token = localStorage.getItem("token");

      if (!token) {
        // No token means not logged in! Send back to login.
        navigate('/login');
        return;
      }

      try {
        const response = await fetch('http://localhost:8000/api/profile', {
          headers: {
            'Authorization': `Bearer ${token}` // Include token in the header
          }
        });

        if (response.ok) {
          const data = await response.json();
          setUser(data);
        } else {
          // Token might be expired or invalid
          localStorage.clear();
          navigate('/login');
        }
      } catch (err) {
        console.error("Fetch error:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, [navigate]);

  const handleLogout = () => {
    localStorage.clear();
    navigate('/login');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto py-20">
        <div className="flex items-center gap-4 mb-12">
          <div className="p-3 bg-primary/10 rounded-2xl">
             <ShoppingBasket className="w-8 h-8 text-primary" />
          </div>
          <h1 className="text-4xl font-extrabold text-on-surface">Your Profile</h1>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
          {/* USER CARD */}
          <div className="lg:col-span-1 bg-white p-10 rounded-[3rem] editorial-shadow border border-zinc-100 flex flex-col items-center text-center">
            <div className="w-32 h-32 bg-emerald-50 text-primary rounded-full flex items-center justify-center mb-6">
              <User className="w-16 h-16" />
            </div>
            
            <h2 className="text-2xl font-extrabold mb-1">{user?.name}</h2>
            <p className="text-zinc-500 font-medium mb-8 flex items-center gap-2 justify-center">
              <Mail className="w-4 h-4" />
              {user?.email}
            </p>

            <button
              onClick={handleLogout}
              className="flex items-center gap-2 bg-red-50 text-red-600 px-8 py-3 rounded-full font-bold hover:bg-red-100 transition-colors"
            >
              <LogOut className="w-5 h-5" />
              Sign Out
            </button>
          </div>

          {/* DETAILS SECTION */}
          <div className="lg:col-span-2 flex flex-col gap-6">
            <div className="bg-white p-8 rounded-[2.5rem] editorial-shadow border border-zinc-100">
               <div className="flex items-center gap-4 mb-6">
                  <div className="w-10 h-10 bg-primary/10 rounded-xl flex items-center justify-center">
                    <ShieldCheck className="w-6 h-6 text-primary" />
                  </div>
                  <h3 className="text-xl font-bold">Account Security</h3>
               </div>
               <div className="flex flex-col gap-4">
                  <div className="flex justify-between items-center py-4 border-b border-zinc-100">
                    <span className="font-bold text-zinc-600">Verification Status</span>
                    <span className="px-3 py-1 bg-green-100 text-green-700 text-xs font-bold rounded-full">VERIFIED</span>
                  </div>
                  <div className="flex justify-between items-center py-4 border-b border-zinc-100">
                    <span className="font-bold text-zinc-600">Session ID</span>
                    <span className="text-zinc-400 font-mono text-xs">...{localStorage.getItem("token")?.slice(-8)}</span>
                  </div>
               </div>
            </div>

            <div className="bg-primary p-12 rounded-[2.5rem] text-white flex flex-col gap-4">
               <h3 className="text-2xl font-bold italic">"Your digital twin is learning..."</h3>
               <p className="opacity-80 leading-relaxed max-w-lg font-medium">
                  BasketIQ is analyzing 24 behavior markers to optimize your next autonomous grocery basket. Check back tomorrow for personalized price drops.
               </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
