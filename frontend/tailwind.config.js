/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'primary': '#0A2240',      // Deep Sapphire Blue
        'secondary': '#F0F4F8',    // Cloud Gray
        'accent': '#2ECC71',       // Signal Green
        'utility': '#6C757D',      // Steel Gray
      },
      fontFamily: {
        'heading': ['Montserrat', 'sans-serif'],
        'body': ['Lato', 'sans-serif'],
      },
    },
  },
  plugins: [],
}