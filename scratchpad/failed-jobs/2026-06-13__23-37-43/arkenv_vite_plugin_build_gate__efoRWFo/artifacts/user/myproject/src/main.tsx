import React from "react";
import { createRoot } from "react-dom/client";

const apiUrl = import.meta.env.VITE_API_URL;
const featureFlags = import.meta.env.VITE_FEATURE_FLAGS;
const maxUploadMb = import.meta.env.VITE_MAX_UPLOAD_MB;

function App() {
  return (
    <div>
      <h1>ArkEnv Build Gate</h1>
      <p>
        API URL: <code>{apiUrl}</code>
      </p>
      <p>
        Feature flags enabled: <code>{String(featureFlags)}</code>
      </p>
      <p>
        Max upload: <code>{maxUploadMb} MB</code>
      </p>
    </div>
  );
}

const root = document.getElementById("root");
if (!root) throw new Error("Missing #root element");
createRoot(root).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
