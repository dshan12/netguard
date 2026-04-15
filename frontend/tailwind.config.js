/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0a0a0b',
        card: '#141416',
        border: '#1f1f22',
        accent: {
          cyan: '#06b6d4',
          red: '#ef4444',
          green: '#22c55e',
          yellow: '#eab308',
        }
      }
    },
  },
  plugins: [],
}
