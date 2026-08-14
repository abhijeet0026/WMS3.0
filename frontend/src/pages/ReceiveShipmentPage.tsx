import React, { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { receiveShipment, fetchProducts } from '../api/client';
import { Product } from '../types/wms';
import { PackagePlus, Truck } from 'lucide-react';
import { Toast, ToastType } from '../components/shared/Toast';
import { BarcodeScanInput } from '../components/app/BarcodeScanInput';
import { ShipmentLineList, LineItem } from '../components/app/ShipmentLineList';

export const ReceiveShipmentPage: React.FC = () => {
  const { currentUser, permissions } = useAuth();
  const [products, setProducts] = useState<Product[]>([]);
  
  const [trackingNumber, setTrackingNumber] = useState('');
  const [warehouseId, setWarehouseId] = useState(currentUser?.facility_scope || 'RENO');
  const [sellerId, setSellerId] = useState('SEL-001'); // static for demo

  const [lineItems, setLineItems] = useState<LineItem[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [toast, setToast] = useState<{ type: ToastType; title: string; message: string } | null>(null);

  useEffect(() => {
    fetchProducts().then(setProducts);
  }, []);

  const handleScan = (upc: string) => {
    setToast(null);
    const product = products.find(p => p.upc === upc);
    
    if (product) {
      const existing = lineItems.find(i => i.product_id === product.id);
      if (existing) {
        setLineItems(lineItems.map(i => i.id === existing.id ? { ...i, quantity: i.quantity + 1 } : i));
      } else {
        setLineItems([...lineItems, {
          id: Math.random().toString(),
          product_id: product.id,
          sku: product.sku,
          name: product.name,
          quantity: 1,
          condition: 'GOOD'
        }]);
      }
    } else {
      setToast({
        type: 'error',
        title: 'Unknown UPC',
        message: `No product found matching UPC: ${upc}.`
      });
    }
  };

  const handleUpdateLine = (id: string, updates: Partial<LineItem>) => {
    setLineItems(lineItems.map(item => item.id === id ? { ...item, ...updates } : item));
  };

  const totalUnits = lineItems.reduce((sum, item) => sum + item.quantity, 0);
  const facilityLabel = warehouseId === 'RENO' ? 'Reno, NV' : 'Columbus, OH';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setToast(null);

    if (!trackingNumber.trim()) {
      setToast({ type: 'error', title: 'Missing Info', message: 'Tracking number is required.' });
      return;
    }

    if (currentUser?.role === 'NEW_HIRE') {
      const confirmMsg = `Confirm quantity: ${totalUnits}`;
      if (!window.confirm(confirmMsg)) {
        return;
      }
    }

    if (lineItems.length === 0) {
      setToast({ type: 'error', title: 'Empty Shipment', message: 'Scan at least one item before submitting.' });
      return;
    }

    try {
      setSubmitting(true);
      const res = await receiveShipment({
        tracking_number: trackingNumber,
        warehouse_id: warehouseId,
        seller_id: sellerId,
        items: lineItems.map(item => ({
          product_id: item.product_id,
          quantity: item.quantity,
          condition: item.condition,
          damage_reason: item.damage_reason
        })),
      });

      if (res.is_duplicate_attempt) {
        setToast({
          type: 'duplicate',
          title: 'Already Received (Idempotent)',
          message: `Tracking #${res.tracking_number} was already logged at ${new Date(res.received_at!).toLocaleString()}. Displaying existing record to prevent phantom stock.`
        });
        setTimeout(() => {
            const toastEl = document.querySelector('.toast-container');
            if (toastEl) toastEl.setAttribute('data-testid', 'already-received-banner');
        }, 10);
      } else {
        setToast({
          type: 'success',
          title: 'Shipment Received',
          message: `Successfully received ${totalUnits} units into ${res.warehouse_id}.`
        });
        setTimeout(() => {
            const toastEl = document.querySelector('.toast-container');
            if (toastEl) toastEl.setAttribute('data-testid', 'receive-success-banner');
        }, 10);
        setTrackingNumber('');
        setLineItems([]);
      }
    } catch (err: any) {
      setToast({ type: 'error', title: 'Submission Failed', message: err.message });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="receive-page">
      <div className="app-page-header">
        <div className="app-page-heading-row">
          <h1 className="app-page-title">
            <PackagePlus size={22} color="var(--color-orange-primary)" />
            Inbound <span className="app-page-title-accent">Receiving</span>
          </h1>
          <span className="app-chip app-chip-neutral">{facilityLabel}</span>
        </div>
        <p className="app-page-subtitle">
          Scan tracking tickets and UPCs. System enforces idempotency — no phantom stock on retries.
        </p>
      </div>

      {toast && <Toast {...toast} onDismiss={() => setToast(null)} />}

      <div className="receive-summary-grid">
        <div className="app-panel app-panel-accent receive-summary-card">
          <span className="receive-summary-label">Items in Manifest</span>
          <strong>{lineItems.length}</strong>
        </div>
        <div className="app-panel receive-summary-card">
          <span className="receive-summary-label">Total Units</span>
          <strong>{totalUnits}</strong>
        </div>
        <div className="app-panel receive-summary-card">
          <span className="receive-summary-label">Destination</span>
          <strong>{facilityLabel}</strong>
        </div>
      </div>

      <div className="receive-layout">
        <form onSubmit={handleSubmit} className="app-panel receive-form">
          <h3 className="receive-form-title">Manifest Details</h3>

          <div className="field-block">
            <label className="field-label">
              <Truck size={14} /> Tracking / Ticket Number
            </label>
            <input
              data-testid="tracking-number-input"
              type="text"
              value={trackingNumber}
              onChange={e => setTrackingNumber(e.target.value)}
              className="app-input mono"
              placeholder="Scan or type tracking..."
              required
            />
          </div>

          <div className="field-block">
            <label className="field-label">Destination Facility</label>
            <select
              value={warehouseId}
              onChange={e => setWarehouseId(e.target.value)}
              className="app-input"
              disabled={!permissions.canViewOtherFacility && currentUser?.facility_scope !== null}
            >
              {(permissions.canViewOtherFacility || currentUser?.facility_scope === 'RENO') && <option value="RENO">Reno, NV</option>}
              {(permissions.canViewOtherFacility || currentUser?.facility_scope === 'COLUMBUS') && <option value="COLUMBUS">Columbus, OH</option>}
            </select>
          </div>

          <button data-testid="mark-received-button" type="submit" className="btn-primary receive-submit" disabled={submitting || lineItems.length === 0}>
            {submitting ? 'Committing...' : 'Mark Shipment Received'}
          </button>
        </form>

        <div className="receive-content-stack">
          <BarcodeScanInput onScan={handleScan} />

          <div className="app-panel">
            <div className="receive-list-header">
              <h3>Scanned Line Items</h3>
              <span className="app-chip app-chip-orange">{totalUnits} units</span>
            </div>
            <ShipmentLineList
              items={lineItems}
              onUpdateQuantity={(id, q) => handleUpdateLine(id, { quantity: q })}
              onUpdateCondition={(id, c) => handleUpdateLine(id, { condition: c })}
              onUpdateDamageReason={(id, r) => handleUpdateLine(id, { damage_reason: r })}
              onRemove={(id) => setLineItems(lineItems.filter(i => i.id !== id))}
            />
          </div>
        </div>
      </div>
    </div>
  );
};
