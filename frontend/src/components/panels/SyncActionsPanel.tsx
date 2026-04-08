import { useState } from "react";

type Props = {
  onRunKiwoomSync: () => void;
  onRunFxSync: () => void;
  onImportUsCsv: (file: File, usdCash: string) => void;
  isRunningKiwoomSync: boolean;
  isRunningFxSync: boolean;
  isImportingUsCsv: boolean;
};

export function SyncActionsPanel({
  onRunKiwoomSync,
  onRunFxSync,
  onImportUsCsv,
  isRunningKiwoomSync,
  isRunningFxSync,
  isImportingUsCsv,
}: Props) {
  const [usdCash, setUsdCash] = useState("");
  const [file, setFile] = useState<File | null>(null);

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(3, minmax(0, 1fr))",
        gap: "16px",
      }}
    >
      <div
        style={{
          border: "1px solid #e5e7eb",
          borderRadius: "12px",
          background: "white",
          padding: "16px",
        }}
      >
        <h3 style={{ marginTop: 0 }}>Kiwoom Sync</h3>
        <p style={{ color: "#6b7280", marginTop: "8px" }}>
          Pull latest KR holdings and KRW cash from Kiwoom.
        </p>

        <button
          onClick={onRunKiwoomSync}
          disabled={isRunningKiwoomSync}
          style={buttonStyle}
        >
          {isRunningKiwoomSync ? "Running Kiwoom Sync..." : "Run Kiwoom Sync"}
        </button>
      </div>

      <div
        style={{
          border: "1px solid #e5e7eb",
          borderRadius: "12px",
          background: "white",
          padding: "16px",
        }}
      >
        <h3 style={{ marginTop: 0 }}>FX Refresh</h3>
        <p style={{ color: "#6b7280", marginTop: "8px" }}>
          Refresh KRW / USD FX snapshots from a live external source.
        </p>

        <button
          onClick={onRunFxSync}
          disabled={isRunningFxSync}
          style={buttonStyle}
        >
          {isRunningFxSync ? "Running FX Sync..." : "Run FX Sync"}
        </button>
      </div>

      <div
        style={{
          border: "1px solid #e5e7eb",
          borderRadius: "12px",
          background: "white",
          padding: "16px",
          display: "grid",
          gap: "12px",
        }}
      >
        <h3 style={{ margin: 0 }}>US Holdings CSV Import</h3>
        <p style={{ color: "#6b7280", margin: 0 }}>
          Upload a CSV for the US sleeve and provide current USD cash.
        </p>

        <a
          href="http://127.0.0.1:8000/api/v1/import/us-holdings/template"
          target="_blank"
          rel="noreferrer"
          style={{ fontSize: "14px" }}
        >
          Download CSV template
        </a>

        <label style={fieldStyle}>
          <span style={labelStyle}>USD Cash</span>
          <input
            value={usdCash}
            onChange={(e) => setUsdCash(e.target.value)}
            placeholder="e.g. 15000"
            style={inputStyle}
          />
        </label>

        <label style={fieldStyle}>
          <span style={labelStyle}>CSV File</span>
          <input
            type="file"
            accept=".csv"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          />
        </label>

        <button
          onClick={() => {
            if (file) onImportUsCsv(file, usdCash);
          }}
          disabled={!file || !usdCash || isImportingUsCsv}
          style={buttonStyle}
        >
          {isImportingUsCsv ? "Importing US CSV..." : "Import US Holdings CSV"}
        </button>
      </div>
    </div>
  );
}

const fieldStyle: React.CSSProperties = {
  display: "grid",
  gap: "6px",
};

const labelStyle: React.CSSProperties = {
  fontSize: "13px",
  color: "#6b7280",
};

const inputStyle: React.CSSProperties = {
  height: "40px",
  borderRadius: "8px",
  border: "1px solid #d1d5db",
  padding: "0 12px",
  fontSize: "14px",
  background: "white",
};

const buttonStyle: React.CSSProperties = {
  height: "40px",
  padding: "0 16px",
  borderRadius: "8px",
  border: "1px solid #d1d5db",
  background: "white",
  cursor: "pointer",
  fontWeight: 600,
};