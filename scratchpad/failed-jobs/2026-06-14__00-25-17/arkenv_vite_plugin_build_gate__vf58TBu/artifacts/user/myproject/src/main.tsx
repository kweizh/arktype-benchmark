import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";

const apiUrl: string = import.meta.env.VITE_API_URL;

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App apiUrl={apiUrl} />
  </StrictMode>,
);