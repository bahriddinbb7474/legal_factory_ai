export default function HomePage() {
  return (
    <main
      style={{
        alignItems: "center",
        display: "flex",
        flexDirection: "column",
        fontFamily:
          "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
        gap: "12px",
        justifyContent: "center",
        minHeight: "100vh",
        padding: "32px",
        textAlign: "center",
      }}
    >
      <h1 style={{ fontSize: "40px", margin: 0 }}>Legal Factory AI</h1>
      <p style={{ color: "#475569", fontSize: "18px", margin: 0 }}>
        AI legal workspace for cable factory
      </p>
    </main>
  );
}
