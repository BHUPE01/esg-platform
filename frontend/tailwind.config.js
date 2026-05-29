/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          50: "#f0f9ff",
          500: "#0ea5e9",
          600: "#0284c7",
          700: "#0369a1",
        },
        esg: {
          green: "#16a34a",
          amber: "#d97706",
          red: "#dc2626",
        }
      }
    },
  },
  plugins: [],
};