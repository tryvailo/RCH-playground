/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        success: '#2ecc71',
        warning: '#f39c12',
        danger: '#e74c3c',
        info: '#3498db',
        primary: '#9b59b6',
      },
    },
  },
  plugins: [],
}

