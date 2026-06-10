/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts}'],
  theme: {
    extend: {
      colors: {
        orange: {
          50:  '#FFF8F5',
          100: '#FFF0E8',
          200: '#FDCCB0',
          300: '#F9A87A',
          400: '#F6854A',
          500: '#F4652A',
          600: '#D4521A',
          700: '#A83F10',
        },
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui'],
      },
      boxShadow: {
        card:  '0 1px 4px rgba(0,0,0,0.08)',
        panel: '0 2px 12px rgba(0,0,0,0.06)',
      },
    },
  },
  plugins: [],
}