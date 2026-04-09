import { useEffect, useMemo, useState } from "react";

import type {
  ManualStrategyOverlayUpsertRequest,
  StrategyOptionsPayload,
  StrategyOverlayItem,
} from "../../types/strategy";
import { formatCurrency } from "../../utils/format";

type Props = {
  selectedRow: StrategyOverlayItem | null;
  options: StrategyOptionsPayload | null;
  isSaving: boolean;
  onSave: (payload: ManualStrategyOverlayUpsertRequest) => void;
};

export function StrategyOverlayEditor({
  selectedRow,
  options,
  isSaving,
  onSave,
}: Props) {
  const [strategyState, setStrategyState] = useState("");
  const [targetState, setTargetState] = useState("");
  const [targetWeight, setTargetWeight] = useState("");
  const [targetDollars, setTargetDollars] = useState("");
  const [eligibilityStatus, setEligibilityStatus] = useState("");
  const [buyListStatus, setBuyListStatus] = useState("");
  const [reasonCode, setReasonCode] = useState("");
  const [notes, setNotes] = useState("");
  const [appendDecisionLog, setAppendDecisionLog] = useState(true);

  useEffect(() => {
    if (!selectedRow) {
      return;
    }

    setStrategyState(selectedRow.strategy_state ?? "");
    setTargetState(selectedRow.target_state ?? "");
    setTargetWeight(
      selectedRow.target_weight == null ? "" : String(selectedRow.target_weight)
    );
    setTargetDollars(
      selectedRow.target_dollars == null ? "" : String(selectedRow.target_dollars)
    );
    setEligibilityStatus(selectedRow.eligibility_status ?? "");
    setBuyListStatus(selectedRow.buy_list_status ?? "");
    setReasonCode(selectedRow.reason_code ?? "MANUAL_HOLD");
    setNotes("");
    setAppendDecisionLog(true);
  }, [selectedRow]);

  useEffect(() => {
    if (!reasonCode && options && options.reason_codes.length > 0) {
      setReasonCode(options.reason_codes[0].code);
    }
  }, [options, reasonCode]);

  const currentMarketValue = selectedRow?.current_market_value_base ?? 0;

  const previewDelta = useMemo(() => {
    if (!targetDollars) return null;
    const parsed = Number(targetDollars);
    if (Number.isNaN(parsed)) return null;
    return currentMarketValue - parsed;
  }, [currentMarketValue, targetDollars]);

  if (!selectedRow) {
    return (
      <div style={panelStyle}>
        <h3 style={{ marginTop: 0 }}>Manual Strategy Input</h3>
        <div style={{ color: "#6b7280" }}>Select a row from the overlay table first.</div>
      </div>
    );
  }

  return (
    <div style={panelStyle}>
      <h3 style={{ marginTop: 0 }}>Manual Strategy Input</h3>
      <div style={{ color: "#6b7280", marginBottom: "16px" }}>
        Save a manual overlay row and optionally append a daily decision-log entry.
      </div>

      <div style={{ display: "grid", gap: "12px" }}>
        <ReadOnlyField label="Symbol" value={selectedRow.symbol} />
        <ReadOnlyField label="Sleeve" value={selectedRow.sleeve} />
        <ReadOnlyField
          label="Current Position $"
          value={formatCurrency(currentMarketValue, "USD", 0)}
        />

        <Field label="Strategy State">
          <select value={strategyState} onChange={(e) => setStrategyState(e.target.value)} style={inputStyle}>
            <option value="">—</option>
            {(options?.strategy_state_options ?? []).map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>
        </Field>

        <Field label="Target State">
          <select value={targetState} onChange={(e) => setTargetState(e.target.value)} style={inputStyle}>
            <option value="">—</option>
            {(options?.target_state_options ?? []).map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>
        </Field>

        <Field label="Target Weight">
          <input
            value={targetWeight}
            onChange={(e) => setTargetWeight(e.target.value)}
            placeholder="e.g. 0.05"
            style={inputStyle}
          />
        </Field>

        <Field label="Target Dollars">
          <input
            value={targetDollars}
            onChange={(e) => setTargetDollars(e.target.value)}
            placeholder="e.g. 5000"
            style={inputStyle}
          />
        </Field>

        <Field label="Eligibility Status">
          <select
            value={eligibilityStatus}
            onChange={(e) => setEligibilityStatus(e.target.value)}
            style={inputStyle}
          >
            <option value="">—</option>
            {(options?.eligibility_status_options ?? []).map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>
        </Field>

        <Field label="Buy List Status">
          <select
            value={buyListStatus}
            onChange={(e) => setBuyListStatus(e.target.value)}
            style={inputStyle}
          >
            <option value="">—</option>
            {(options?.buy_list_status_options ?? []).map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>
        </Field>

        <Field label="Reason Code">
          <select value={reasonCode} onChange={(e) => setReasonCode(e.target.value)} style={inputStyle}>
            {(options?.reason_codes ?? []).map((item) => (
              <option key={item.code} value={item.code}>
                {item.code} — {item.label}
              </option>
            ))}
          </select>
        </Field>

        <div
          style={{
            border: "1px solid #e5e7eb",
            borderRadius: "8px",
            padding: "10px 12px",
            background: "#f9fafb",
            fontSize: "13px",
            color: "#4b5563",
          }}
        >
          {
            options?.reason_codes.find((item) => item.code === reasonCode)?.description ??
            "Select a reason code."
          }
        </div>

        <Field label="Notes">
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            rows={4}
            style={{ ...inputStyle, height: "auto", paddingTop: "10px" }}
          />
        </Field>

        <label
          style={{
            display: "flex",
            alignItems: "center",
            gap: "8px",
            fontSize: "14px",
          }}
        >
          <input
            type="checkbox"
            checked={appendDecisionLog}
            onChange={(e) => setAppendDecisionLog(e.target.checked)}
          />
          Append daily decision-log row on save
        </label>

        <ReadOnlyField
          label="Preview Delta"
          value={previewDelta == null ? "—" : formatCurrency(previewDelta, "USD", 0)}
        />

        <button
          disabled={isSaving || !reasonCode}
          onClick={() =>
            onSave({
              symbol: selectedRow.symbol,
              sleeve: selectedRow.sleeve,
              strategy_state: strategyState || null,
              target_state: targetState || null,
              target_weight: targetWeight ? Number(targetWeight) : null,
              target_dollars: targetDollars ? Number(targetDollars) : null,
              eligibility_status: eligibilityStatus || null,
              buy_list_status: buyListStatus || null,
              reason_code: reasonCode,
              notes: notes || null,
              append_decision_log: appendDecisionLog,
            })
          }
          style={buttonStyle}
        >
          {isSaving ? "Saving Manual Overlay..." : "Save Manual Overlay"}
        </button>
      </div>
    </div>
  );
}

function Field({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <label style={{ display: "grid", gap: "6px" }}>
      <span style={{ fontSize: "13px", color: "#6b7280" }}>{label}</span>
      {children}
    </label>
  );
}

function ReadOnlyField({ label, value }: { label: string; value: string }) {
  return (
    <div style={{ display: "grid", gap: "6px" }}>
      <span style={{ fontSize: "13px", color: "#6b7280" }}>{label}</span>
      <div
        style={{
          minHeight: "40px",
          border: "1px solid #e5e7eb",
          borderRadius: "8px",
          padding: "10px 12px",
          background: "#f9fafb",
          display: "flex",
          alignItems: "center",
        }}
      >
        {value}
      </div>
    </div>
  );
}

const panelStyle: React.CSSProperties = {
  border: "1px solid #e5e7eb",
  borderRadius: "12px",
  background: "white",
  padding: "16px",
};

const inputStyle: React.CSSProperties = {
  height: "40px",
  borderRadius: "8px",
  border: "1px solid #d1d5db",
  padding: "0 12px",
  fontSize: "14px",
  background: "white",
  width: "100%",
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