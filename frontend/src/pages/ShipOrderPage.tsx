import React, { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { fetchOrders, shipOrder } from '../api/client';
import { Order } from '../types/wms';
import { Truck, Printer, Scale, Search } from 'lucide-react';
import { Toast, ToastType } from '../components/shared/Toast';

export const ShipOrderPage: React.FC = () => {
  const { currentUser, permissions } = useAuth();
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [shippingOrderId, setShippingOrderId] = useState<string | null>(null);
  const [toast, setToast] = useState<{ type: ToastType; title: string; message: string } | null>(null);

  // Facility filter
  const [warehouseId, setWarehouseId] = useState(currentUser?.facility_scope || 'ALL');

  useEffect(() => {
    loadOrders();
  }, [warehouseId]);

  const loadOrders = async () => {
    try {
      setLoading(true);
      const data = await fetchOrders(warehouseId === 'ALL' ? undefined : warehouseId);
      setOrders(data);
    } catch (err: any) {
      setToast({ type: 'error', title: 'Fetch Error', message: err.message });
    } finally {
      setLoading(false);
    }
  };

  const handleShipOrder = async (orderId: string) => {
    setToast(null);
    try {
      setShippingOrderId(orderId);
      const shippedOrder = await shipOrder(orderId, '1.5 lbs'); // default weight for demo
      
      setToast({
        type: 'success',
        title: 'Order Shipped',
        message: `Order #${shippedOrder.order_number} has been packed, shipped, and stock deducted atomically.`
      });
      loadOrders(); // refresh list
    } catch (err: any) {
      // The backend returns 409 Conflict if stock is insufficient due to row-locking race conditions.
      // This is expected business logic during a race, not a crash.
      if (err.message.includes('Insufficient stock')) {
        setToast({
          type: 'warning',
          title: 'Stock Unavailable',
          message: 'Pick failed. Another worker has already claimed the remaining stock for this item. Please physically verify inventory.'
        });
      } else {
        setToast({ type: 'error', title: 'Shipping Error', message: err.message });
      }
    } finally {
      setShippingOrderId(null);
    }
  };

  const handleScanShip = (e: React.FormEvent) => {
    e.preventDefault();
    const pendingOrder = orders.find(o => o.status === 'PENDING');
    if (pendingOrder) {
      handleShipOrder(pendingOrder.id);
    } else {
      setToast({ type: 'error', title: 'No Orders', message: 'No pending orders available to ship.' });
    }
  };

  return (
    <div>
      <div className="app-page-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <h1 className="app-page-title">
              <Truck size={22} color="var(--color-orange-primary)" />
              Outbound <span className="app-page-title-accent">Shipping</span>
            </h1>
            <p className="app-page-subtitle">
              Fulfill pending orders. Stock deducted with row-level locking — no overselling.
            </p>
          </div>
          {permissions.canViewOtherFacility && (
            <select
              value={warehouseId}
              onChange={(e) => setWarehouseId(e.target.value)}
              className="app-input"
              style={{ width: 'auto', marginTop: 0 }}
            >
              <option value="ALL">All Facilities</option>
              <option value="RENO">Reno, NV</option>
              <option value="COLUMBUS">Columbus, OH</option>
            </select>
          )}
        </div>
      </div>

      {toast && (
        <div data-testid="ship-result">
          <Toast {...toast} onDismiss={() => setToast(null)} />
        </div>
      )}

      <div className="app-panel">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
          <h3 style={{ fontSize: '1.1rem', margin: 0 }}>Pending Orders</h3>
          
          <form onSubmit={handleScanShip} style={{ display: 'flex', gap: '0.5rem' }}>
            <div style={{ position: 'relative' }}>
              <Search size={16} color="#9ca3af" style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)' }} />
              <input data-testid="barcode-scan-input" type="text" placeholder="Scan barcode to ship next..." className="app-input" style={{ paddingLeft: '2rem', width: '250px', marginTop: 0 }} />
            </div>
            <button data-testid="ship-confirm-button" type="submit" className="btn-primary" style={{ padding: '0.5rem 1rem', marginTop: 0 }}>
              Scan & Ship
            </button>
          </form>
        </div>



        {loading ? (
          <p style={{ color: '#6b7280', textAlign: 'center', padding: '2rem' }}>Loading orders...</p>
        ) : orders.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '3rem', color: '#9ca3af', border: '1px dashed #e5e7eb', borderRadius: '4px' }}>
            No pending orders to fulfill at this facility.
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="app-table">
              <thead>
                <tr>
                  <th>Order #</th>
                  <th>Customer</th>
                  <th>Facility</th>
                  <th>Status</th>
                  <th style={{ textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {orders.map(order => (
                  <tr key={order.id}>
                    <td className="mono-text" style={{ fontWeight: 600 }}>{order.order_number}</td>
                    <td>{order.customer_name}</td>
                    <td><span className="badge badge-neutral">{order.warehouse_id}</span></td>
                    <td>
                      <span className={`badge ${order.status === 'SHIPPED' ? 'badge-success' : 'badge-warning'}`}>
                        {order.status}
                      </span>
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      {order.status === 'PENDING' ? (
                        <button
                          onClick={() => handleShipOrder(order.id)}
                          disabled={shippingOrderId === order.id}
                          className="btn-primary"
                          style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.85rem' }}
                        >
                          <Scale size={14} /> Pack & Ship
                        </button>
                      ) : (
                        <button className="btn-secondary" disabled style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.85rem' }}>
                          <Printer size={14} /> Reprint Label
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

    </div>
  );
};
