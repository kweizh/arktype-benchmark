interface AppProps {
  apiUrl: string;
}

function App({ apiUrl }: AppProps) {
  return (
    <div>
      <h1>ArkEnv Build Gate</h1>
      <p>API URL: {apiUrl}</p>
    </div>
  );
}

export default App;