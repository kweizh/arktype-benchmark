import React from 'react';
import ReactDOM from 'react-dom/client';

const apiUrl = import.meta.env.VITE_API_URL;
console.log("API URL is", apiUrl);

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <div>
      <h1>ArkEnv Vite Plugin Build Gate</h1>
      <p>API URL: {apiUrl}</p>
    </div>
  </React.StrictMode>
);
