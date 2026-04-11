/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        "primary": "#006036",
        "primary-container": "#1b7a4a",
        "on-primary-container": "#abffc6",
        "secondary": "#835500",
        "background": "#f9f9f6",
        "on-background": "#1a1c1b",
        "surface": "#f9f9f6",
        "on-surface": "#1a1c1b",
        "surface-container": "#eeeeeb",
      },
      fontFamily: {
        plus: ["Plus Jakarta Sans", "sans-serif"],
      }
    },
  },
  plugins: [],
}
