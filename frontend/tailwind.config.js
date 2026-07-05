/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#F97316",
          hover: "#EA580C",
        },
        tier: {
          allow: "#16A34A",
          review: "#D97706",
          block: "#DC2626",
        },
        surface: {
          DEFAULT: "#FFFFFF",
          muted: "#F9FAFB",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
