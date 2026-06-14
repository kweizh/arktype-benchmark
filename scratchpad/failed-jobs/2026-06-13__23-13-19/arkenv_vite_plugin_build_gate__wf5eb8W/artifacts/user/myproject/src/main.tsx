import React from 'react';
import ReactDOM from 'react-dom/client';

const apiUrl = import.meta.env.VITE_API_URL;

function App() {
  return (
    <div>
      <h1>ArkEnv Vite Plugin Build Gate</h1>
      <p>API URL: <span id="api-url">{apiUrl}</span></p>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
