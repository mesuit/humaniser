import React, { useState } from "react";
import axios from "axios";

export default function App() {
  const [input, setInput] = useState("");
  const [output, setOutput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async () => {
    setError("");
    setOutput("");
    if (!input.trim()) {
      setError("Please provide some text.");
      return;
    }
    setLoading(true);
    try {
      // When deployed as single app, same origin; locally adjust to backend URL if needed
      const res = await axios.post("/api/humanise", { text: input }, { timeout: 120000 });
      setOutput(res.data.humanised || res.data.output || "");
    } catch (e) {
      console.error(e);
      setError(e?.response?.data?.error || e.message || "Request failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 900, margin: "40px auto", fontFamily: "Inter, Roboto, sans-serif" }}>
      <h1>Advanced Humaniser</h1>
      <textarea
        rows={12}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Paste text to humanise (any length)..."
        style={{ width: "100%", padding: 12, fontSize: 16 }}
      />
      <div style={{ marginTop: 12 }}>
        <button onClick={handleSubmit} disabled={loading} style={{ padding: "10px 16px", fontSize: 16 }}>
          {loading ? "Humanising..." : "Humanise"}
        </button>
      </div>

      {error && <p style={{ color: "red", marginTop: 12 }}>{error}</p>}

      {output && (
        <div style={{ marginTop: 20 }}>
          <h3>Humanised Text</h3>
          <div style={{ whiteSpace: "pre-wrap", background: "#f7f7f8", padding: 12, borderRadius: 6 }}>
            {output}
          </div>
        </div>
      )}
    </div>
  );
}
