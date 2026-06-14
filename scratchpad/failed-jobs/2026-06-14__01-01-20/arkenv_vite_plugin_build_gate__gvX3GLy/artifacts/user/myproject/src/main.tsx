import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

const apiUrl = import.meta.env.VITE_API_URL;

function App() {
  return (
    <div>
      <h1>ArkEnv Build Gate</h1>
      <p>API URL: {apiUrl}</p>
    </div>
  );
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
