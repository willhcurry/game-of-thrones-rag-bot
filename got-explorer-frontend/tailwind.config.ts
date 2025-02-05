import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'got-primary': '#B21F1F',    // Lannister red
        'got-secondary': '#785A28',   // Golden accent
        'got-dark': '#1a1a1a',       // Dark background
        'got-light': '#D4B483',      // Light accent
        'got-text': '#E5E5E5',       // Light text
      },
    },
  },
  plugins: [],
}

export default config