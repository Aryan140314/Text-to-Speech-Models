/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#090d16',
        surface: '#0f172a',
        card: '#1e293b',
        primary: '#6366f1',
        accent: '#ec4899',
        border: 'rgba(255,255,255,0.1)',
      },
    },
  },
  plugins: [],
}
