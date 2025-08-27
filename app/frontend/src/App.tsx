import { useEffect, useState } from "react";

function App() {
  const [status, setStatus] = useState<string>("loading");

  useEffect(() => {
    fetch("http://localhost:8000/health")
      .then((res) => res.json())
      .then((data) => setStatus(data.status))
      .catch(() => setStatus("error"));
  }, []);

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Health status: {status}</h1>
    </div>
  );
}

export default App;
