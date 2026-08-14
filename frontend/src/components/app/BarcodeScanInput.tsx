import React, { useState } from 'react';
import { QrCode, Search, Plus } from 'lucide-react';

interface BarcodeScanInputProps {
  onScan: (upc: string) => void;
  disabled?: boolean;
}

export const BarcodeScanInput: React.FC<BarcodeScanInputProps> = ({ onScan, disabled }) => {
  const [inputValue, setInputValue] = useState('');
  const [lastScanned, setLastScanned] = useState<string | null>(null);

  const submitScan = () => {
    const value = inputValue.trim();
    if (!value) return;
    onScan(value);
    setLastScanned(value);
    setInputValue('');
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      submitScan();
    }
  };

  return (
    <div className="app-panel scan-panel">
      <div className="scan-panel-header">
        <h3>
          <QrCode size={18} color="var(--color-orange-primary)" />
          Scan UPC / Barcode
        </h3>
        {lastScanned && <span className="app-chip app-chip-neutral">Last: {lastScanned}</span>}
      </div>

      <div className="scan-input-wrap">
        <Search size={18} className="scan-search-icon" />
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          placeholder="Awaiting scanner input... or type and press Enter"
          className="app-input mono scan-input"
          autoFocus
        />
        <button
          type="button"
          className="btn-primary scan-add-button"
          onClick={submitScan}
          disabled={disabled || !inputValue.trim()}
        >
          <Plus size={14} /> Add
        </button>
      </div>

      <p className="scan-help-text">
        Hardware scanners act like keyboard input and finish with Enter.
      </p>
    </div>
  );
};
