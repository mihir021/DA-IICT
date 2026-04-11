import React from 'react';
import { Link } from 'react-router-dom';
import { ShoppingBasket, User, ArrowRight, Zap, Target, History } from 'lucide-react';

/**
 * Home Page - The main dashboard / welcome screen.
 * Reuses the 'Emerald' theme from the landing page.
 */
const Home = () => {
  const userName = localStorage.getItem("user_name") || "Guest";

  return (
    <div className="min-h-screen bg-background">
      {/* --- NAVBAR --- */}
      <nav className="fixed top-0 w-full z-50 bg-white/80 backdrop-blur-xl border-b border-zinc-100">
        <div className="flex justify-between items-center max-w-7xl mx-auto px-6 h-20">
          <div className="text-xl font-extrabold text-primary flex items-center gap-2">
            <ShoppingBasket className="w-7 h-7" />
            <span>BasketIQ</span>
          </div>
          <div className="flex items-center gap-6">
            <Link to="/profile" className="flex items-center gap-2 font-bold text-zinc-600 hover:text-primary transition-colors">
              <User className="w-5 h-5" />
              <span>{userName}</span>
            </Link>
          </div>
        </div>
      </nav>

      {/* --- HERO SECTION --- */}
      <main className="pt-32 pb-20 px-6 max-w-7xl mx-auto">
        <section className="flex flex-col lg:flex-row gap-16 items-center">
          <div className="lg:w-1/2 flex flex-col gap-8">
            <div className="inline-flex items-center gap-2 bg-primary/10 text-primary px-4 py-1.5 rounded-full text-sm font-bold tracking-wide uppercase">
              <Zap className="w-4 h-4 fill-primary" />
              Smart Dashboard
            </div>
            
            <h1 className="text-5xl lg:text-7xl font-extrabold tracking-tight leading-tight text-on-surface">
              Welcome back, <br/>
              <span className="text-primary italic">{userName}!</span>
            </h1>
            
            <p className="text-zinc-600 text-xl leading-relaxed max-w-md">
              Your smart kitchen is ready. Browse, plan, and save with personalized pricing just for you.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 mt-4">
              <button className="emerald-gradient text-white px-10 py-5 rounded-full font-bold text-lg editorial-shadow transition-transform hover:scale-105 active:scale-95">
                Start Shopping
              </button>
              <Link to="/profile" className="flex items-center justify-center gap-2 text-primary font-bold px-10 py-5 hover:bg-emerald-50 rounded-full transition-colors">
                View Profile
                <ArrowRight className="w-5 h-5" />
              </Link>
            </div>
          </div>

          <div className="lg:w-1/2 grid grid-cols-2 gap-6 w-full">
            <div className="bg-white p-8 rounded-[2.5rem] editorial-shadow border border-zinc-100 flex flex-col items-center text-center gap-4 hover:border-primary/20 transition-all">
              <div className="w-14 h-14 bg-emerald-50 text-primary rounded-2xl flex items-center justify-center">
                <Target className="w-7 h-7" />
              </div>
              <h3 className="font-bold text-lg">Price Watch</h3>
              <p className="text-sm text-zinc-500 font-medium">Monitoring 12 items for price drops.</p>
            </div>
            <div className="bg-white p-8 rounded-[2.5rem] editorial-shadow border border-zinc-100 flex flex-col items-center text-center gap-4 hover:border-primary/20 transition-all">
              <div className="w-14 h-14 bg-emerald-50 text-primary rounded-2xl flex items-center justify-center">
                <History className="w-7 h-7" />
              </div>
              <h3 className="font-bold text-lg">Subscriptions</h3>
              <p className="text-sm text-zinc-500 font-medium">Milk & Eggs scheduled for Monday.</p>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
};

export default Home;
