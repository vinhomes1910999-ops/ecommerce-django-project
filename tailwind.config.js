/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./accounts/templates/**/*.html",
    "./products/templates/**/*.html",
    "./cart/templates/**/*.html",
    "./orders/templates/**/*.html",
    "./pages/templates/**/*.html",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: '#4f46e5',
          dark: '#3730a3',
        },
      },
    },
  },
  plugins: [],
}