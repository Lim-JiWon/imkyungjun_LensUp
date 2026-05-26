import { useState } from "react";

export default function InfoTooltip({ text }) {
  const [open, setOpen] = useState(false);

  return (
    <div
      style={{
        position: "relative",
        display: "inline-flex",
        alignItems: "center",
        marginLeft: "6px",
      }}
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => setOpen(false)}
    >
      <button
        type="button"
        onClick={() => setOpen(!open)}
        style={{
          width: "20px",
          height: "20px",
          borderRadius: "50%",
          border: "none",
          background: "#dbeafe",
          color: "#2563eb",
          fontSize: "12px",
          fontWeight: "700",
          cursor: "pointer",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: 0,
        }}
        aria-label="설명 보기"
      >
        ?
      </button>

      {open && (
        <div
          style={{
            position: "absolute",
            top: "28px",
            left: "0",
            minWidth: "220px",
            maxWidth: "260px",
            background: "#1e293b",
            color: "#ffffff",
            padding: "10px 12px",
            borderRadius: "10px",
            fontSize: "13px",
            lineHeight: "1.5",
            boxShadow: "0 8px 20px rgba(0,0,0,0.15)",
            zIndex: 1000,
            wordBreak: "keep-all",
          }}
        >
          {text}
        </div>
      )}
    </div>
  );
}