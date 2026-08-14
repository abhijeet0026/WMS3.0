import React, { useEffect, useState } from 'react';
import { InventoryItem } from '../types/wms';
import { fetchInventory } from '../api/client';
import { Package, Warehouse, AlertTriangle, ShieldCheck, RefreshCw, Layers, TrendingUp } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';

export const DashboardPage: React.FC = () => {
  const { currentUser, permissions } = useAuth();
  const [selectedWarehouse, setSelectedWarehouse] = useState<string>(currentUser?.facility_scope || 'ALL');
  const [inventory, setInventory] = useState<InventoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchInventory(selectedWarehouse);
      setInventory(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load inventory');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [selectedWarehouse]);

  const totalGoodStock = inventory.reduce((acc, item) => acc + item.quantity_good, 0);
  const totalDamagedStock = inventory.reduce((acc, item) => acc + item.quantity_damaged, 0);
  const renoStock = inventory.filter(i => i.warehouse_id === 'RENO').reduce((acc, i) => acc + i.quantity_good, 0);
  const columbusStock = inventory.filter(i => i.warehouse_id === 'COLUMBUS').reduce((acc, i) => acc + i.quantity_good, 0);
  const lowStockItems = inventory.filter(i => i.quantity_good <= 20);

  return (
    <div>
      {/* Page Header */}
      <div className="app-page-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <h1 className="app-page-title">
              Live Inventory
              <span className="app-page-title-accent">Overview</span>
            </h1>
            <p className="app-page-subtitle">
              Real-time transactional stock state. Zero phantom stock. Every write is audited.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
            {permissions.canViewOtherFacility && (
              <select
                data-testid="facility-selector"
                value={selectedWarehouse}
                onChange={(e) => setSelectedWarehouse(e.target.value)}
                className="app-input"
                style={{ width: 'auto', marginTop: 0 }}
              >
                <option value="ALL">All Facilities</option>
                <option value="RENO">Reno, NV</option>
                <option value="COLUMBUS">Columbus, OH</option>
              </select>
            )}
            <button onClick={loadData} className="btn-secondary" style={{ whiteSpace: 'nowrap' }}>
              <RefreshCw size={14} className={loading ? 'spin' : ''} /> Refresh
            </button>
          </div>
        </div>
      </div>

      {/* Metrics Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1.25rem', marginBottom: '2rem' }}>

        <div className="app-metric">
          <p className="app-metric-label">Total Good Stock</p>
          <p className="app-metric-value">
            {totalGoodStock.toLocaleString()}
            <span className="app-metric-unit"> units</span>
          </p>
          <Package size={28} color="#e8e8e5" style={{ position: 'absolute', right: '1.25rem', top: '1.25rem' }} />
        </div>

        {permissions.canViewOtherFacility && (
          <>
            <div className="app-metric">
              <p className="app-metric-label">Reno, NV</p>
              <p className="app-metric-value">
                {renoStock.toLocaleString()}
                <span className="app-metric-unit"> units</span>
              </p>
              <Warehouse size={28} color="#e8e8e5" style={{ position: 'absolute', right: '1.25rem', top: '1.25rem' }} />
            </div>

            <div className="app-metric">
              <p className="app-metric-label">Columbus, OH</p>
              <p className="app-metric-value">
                {columbusStock.toLocaleString()}
                <span className="app-metric-unit"> units</span>
              </p>
              <Warehouse size={28} color="#e8e8e5" style={{ position: 'absolute', right: '1.25rem', top: '1.25rem' }} />
            </div>
          </>
        )}

        <div className="app-metric" style={{ borderColor: lowStockItems.length > 0 ? '#fed7aa' : '#e8e8e5' }}>
          <p className="app-metric-label" style={{ color: lowStockItems.length > 0 ? '#c2410c' : undefined }}>Low Stock Items</p>
          <p className="app-metric-value" style={{ color: lowStockItems.length > 0 ? 'var(--color-orange-primary)' : undefined }}>
            {lowStockItems.length}
            <span className="app-metric-unit"> SKUs</span>
          </p>
          <AlertTriangle size={28} color={lowStockItems.length > 0 ? '#fed7aa' : '#e8e8e5'} style={{ position: 'absolute', right: '1.25rem', top: '1.25rem' }} />
        </div>

        <div className="app-metric">
          <p className="app-metric-label">Damaged Units</p>
          <p className="app-metric-value">
            {totalDamagedStock.toLocaleString()}
            <span className="app-metric-unit"> units</span>
          </p>
          <TrendingUp size={28} color="#e8e8e5" style={{ position: 'absolute', right: '1.25rem', top: '1.25rem' }} />
        </div>
      </div>

      {/* Inventory Table */}
      <div className="app-panel">
        <div className="app-panel-header">
          <Layers size={16} color="var(--color-orange-primary)" />
          Inventory by SKU &amp; Location
          <span style={{ marginLeft: 'auto' }}>
            <span className="badge badge-neutral">
              <ShieldCheck size={11} /> ACID Protected
            </span>
          </span>
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '3rem', color: '#9ca3af' }}>
            <RefreshCw size={24} className="spin" style={{ margin: '0 auto 1rem auto' }} />
            <p style={{ margin: 0 }}>Loading live database stock...</p>
          </div>
        ) : error ? (
          <p style={{ color: '#b91c1c', padding: '1rem' }}>{error}</p>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="app-table">
              <thead>
                <tr>
                  <th>SKU / UPC</th>
                  <th>Product Name</th>
                  {permissions.canViewCostData && (
                    <>
                      <th data-testid="seller-name-column">Seller</th>
                      <th data-testid="cost-column">Cost</th>
                    </>
                  )}
                  <th>Facility</th>
                  <th style={{ textAlign: 'right' }}>Good</th>
                  <th style={{ textAlign: 'right' }}>Damaged</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {inventory.map((item) => (
                  <tr key={item.id}>
                    <td>
                      <div style={{ fontWeight: 700, color: '#1C1C1A', fontFamily: 'IBM Plex Mono', fontSize: '0.85rem' }}>{item.product_sku}</div>
                      <div style={{ fontSize: '0.72rem', color: '#9ca3af', fontFamily: 'IBM Plex Mono' }}>UPC: {item.product_upc}</div>
                    </td>
                    <td style={{ fontWeight: 500 }}>{item.product_name}</td>
                    {permissions.canViewCostData && (
                      <>
                        <td style={{ color: '#6b7280' }}>{item.seller_name || '—'}</td>
                        <td style={{ color: '#6b7280' }}>—</td>
                      </>
                    )}
                    <td>
                      <span className="badge badge-neutral">{item.warehouse_id}</span>
                    </td>
                    <td style={{ textAlign: 'right', fontWeight: 700, color: item.quantity_good > 20 ? '#166534' : '#c2410c', fontFamily: 'IBM Plex Mono' }}>
                      {item.quantity_good}
                    </td>
                    <td style={{ textAlign: 'right', color: item.quantity_damaged > 0 ? '#b91c1c' : '#9ca3af', fontFamily: 'IBM Plex Mono' }}>
                      {item.quantity_damaged}
                    </td>
                    <td>
                      {item.quantity_good <= 20 ? (
                        <span className="badge badge-warning">Low Stock</span>
                      ) : (
                        <span className="badge badge-success">Healthy</span>
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
