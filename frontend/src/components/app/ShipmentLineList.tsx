import React from 'react';
import { Product } from '../../types/wms';
import { Trash2 } from 'lucide-react';

export interface LineItem {
  id: string; // temp id for the list
  product_id: string;
  sku: string;
  name: string;
  quantity: number;
  condition: 'GOOD' | 'DAMAGED';
  damage_reason?: string;
}

interface ShipmentLineListProps {
  items: LineItem[];
  onUpdateQuantity: (id: string, qty: number) => void;
  onUpdateCondition: (id: string, condition: 'GOOD' | 'DAMAGED') => void;
  onUpdateDamageReason: (id: string, reason: string) => void;
  onRemove: (id: string) => void;
}

export const ShipmentLineList: React.FC<ShipmentLineListProps> = ({
  items, onUpdateQuantity, onUpdateCondition, onUpdateDamageReason, onRemove
}) => {
  if (items.length === 0) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center', color: '#9ca3af', border: '1px dashed #e5e7eb', borderRadius: '4px' }}>
        No items scanned yet. Scan a UPC to add to shipment.
      </div>
    );
  }

  return (
    <div style={{ overflowX: 'auto' }}>
      <table className="app-table scanned-items-table">
        <thead>
          <tr>
            <th>SKU</th>
            <th>Name</th>
            <th style={{ width: '100px' }}>Qty</th>
            <th style={{ width: '150px' }}>Condition</th>
            <th>Damage Note</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {items.map(item => (
            <tr key={item.id} className="scanned-item-row">
              <td className="mono-text scanned-sku">{item.sku}</td>
              <td className="scanned-item-name">{item.name}</td>
              <td>
                <div className="qty-editor">
                  <button type="button" className="qty-control" onClick={() => onUpdateQuantity(item.id, Math.max(1, item.quantity - 1))}>−</button>
                  <input
                    type="number"
                    min="1"
                    value={item.quantity}
                    onChange={(e) => onUpdateQuantity(item.id, Number(e.target.value) || 1)}
                    className="app-input mono"
                    style={{ width: '70px', marginTop: 0 }}
                  />
                  <button type="button" className="qty-control" onClick={() => onUpdateQuantity(item.id, item.quantity + 1)}>＋</button>
                </div>
              </td>
              <td>
                <select
                  value={item.condition}
                  onChange={(e) => onUpdateCondition(item.id, e.target.value as 'GOOD'|'DAMAGED')}
                  className="app-input"
                  style={{ marginTop: 0 }}
                >
                  <option value="GOOD">Good</option>
                  <option value="DAMAGED">Damaged</option>
                </select>
              </td>
              <td>
                {item.condition === 'DAMAGED' && (
                  <input
                    type="text"
                    value={item.damage_reason || ''}
                    onChange={(e) => onUpdateDamageReason(item.id, e.target.value)}
                    className="app-input"
                    placeholder="Describe damage..."
                    style={{ marginTop: 0, borderColor: '#ef4444' }}
                  />
                )}
              </td>
              <td style={{ textAlign: 'right' }}>
                <button
                  type="button"
                  onClick={() => onRemove(item.id)}
                  className="remove-item-button"
                  title="Remove item"
                >
                  <Trash2 size={16} />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
