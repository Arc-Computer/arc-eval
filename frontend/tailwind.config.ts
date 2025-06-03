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
        'arc-blue': {
          light: '#60a5fa', // example blue-400
          DEFAULT: '#2563eb', // example blue-600
          dark: '#1d4ed8',  // example blue-700
        },
        'arc-gray': {
          extralight: '#f3f4f6', // example gray-100
          light: '#d1d5db',    // example gray-300
          DEFAULT: '#6b7280',    // example gray-500
          dark: '#374151',     // example gray-700
        },
        // Add other brand colors as needed (e.g., for risk levels)
        'arc-red': '#ef4444',    // example red-500
        'arc-amber': '#f59e0b',  // example amber-500
        'arc-green': '#22c55e',  // example green-500
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic':
          'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [],
}
export default config
