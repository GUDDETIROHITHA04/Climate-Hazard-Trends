import path from "node:path";
import { fileURLToPath } from "node:url";
const __dirname = path.dirname(fileURLToPath(import.meta.url));
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";
export default defineConfig({
    plugins: [react()],
    resolve: { alias: { "@": path.resolve(__dirname, "src") } },
    build: {
        rollupOptions: {
            output: {
                manualChunks: {
                    antd: ["antd", "@ant-design/icons"],
                    charts: ["chart.js", "react-chartjs-2"],
                    map: ["leaflet", "react-leaflet"],
                },
            },
        },
        chunkSizeWarningLimit: 1200,
    },
});
