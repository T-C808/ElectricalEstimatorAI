import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#1f2933",
        panel: "#f7f3ea",
        copper: "#b45309",
        conduit: "#256f7c",
        alert: "#b42318"
      }
    }
  },
  plugins: []
} satisfies Config;
