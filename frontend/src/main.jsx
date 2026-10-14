import React from "react";
import { createRoot } from "react-dom/client";

import "antd/dist/reset.css";
import "leaflet/dist/leaflet.css";
import "./styles/global.css";

import { AnalyzerPage } from "./pages/AnalyzerPage";

const rootElement = document.getElementById("root");

createRoot(rootElement).render(
    <React.StrictMode>
        <AnalyzerPage />
    </React.StrictMode>,
);
