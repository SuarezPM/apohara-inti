/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    container: {
      center: true,
      padding: "1rem",
      screens: {
        "2xl": "1280px",
      },
    },
    extend: {
      colors: {
        // shadcn-style HSL CSS variables (re-mapped to Apohara brand palette in index.css)
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        // Apohara brand palette (raw hex; use Tailwind opacity modifiers e.g. apohara-lime/27)
        apohara: {
          lime:      "#25B13F",
          dark:      "#2A2D3A",
          bone:      "#EDEFF0",
          ink:       "#0E1010",
          red:       "#B8262A",
          "bg-void":   "#0D0F18",
          "bg-mid":    "#1E2130",
          "bg-raised": "#222640",
        },
        // Legacy plane palette — kept for transition; new code prefers apohara-* tokens
        plane: {
          memory: "hsl(140 70% 45%)",
          defense: "hsl(35 95% 55%)",
          danger: "hsl(0 85% 60%)",
        },
      },
      fontFamily: {
        "pixel-sans": ['"Press Start 2P"', "ui-monospace", "monospace"],
        mono: ['"JetBrains Mono"', "ui-monospace", "SFMono-Regular", "Menlo", "monospace"],
        body: ["Inter", "ui-sans-serif", "system-ui", "-apple-system", '"Segoe UI"', "Roboto", "sans-serif"],
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        // Lime perimeter pulse for status="running" attacker cards
        "pulse-lime": {
          "0%, 100%": {
            boxShadow: "0 0 0 0 hsl(131 65% 42% / 0.5)",
            opacity: "1",
          },
          "50%": {
            boxShadow: "0 0 0 10px hsl(131 65% 42% / 0)",
            opacity: "0.92",
          },
        },
        // Terminal cursor blink
        blink: {
          "0%, 49%": { opacity: "1" },
          "50%, 100%": { opacity: "0" },
        },
        // Hero terminal typing cadence (caller controls duration via animation-duration)
        "terminal-typing": {
          from: { width: "0" },
          to: { width: "100%" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
        // Legacy aliases
        "pulse-green": {
          "0%, 100%": { boxShadow: "0 0 0 0 hsl(140 70% 45% / 0.5)", opacity: "1" },
          "50%":       { boxShadow: "0 0 0 12px hsl(140 70% 45% / 0)",  opacity: "0.95" },
        },
      },
      animation: {
        "pulse-lime":      "pulse-lime 2s ease-in-out infinite",
        blink:             "blink 1s step-end infinite",
        "terminal-typing": "terminal-typing 2.4s steps(40, end) forwards",
        shimmer:           "shimmer 2s linear infinite",
        "pulse-green":     "pulse-green 2s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
