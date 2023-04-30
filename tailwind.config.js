/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/src/**/*.js"
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter var']
      },
      textColor: {
        'vizzuality': '#2ba4a0',
      },
      backgroundColor: {
        'vizzuality': '#2ba4a0',
      },
    },
  },
  variants: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography')
  ]
}
    