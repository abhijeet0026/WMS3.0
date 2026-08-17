import {
  InventoryItem, Product, Shipment, Order, AuditLog, LegacyIssue, VoiceAssistantResponse, User
} from '../types/wms';

export const API_BASE = (() => {
  const configuredUrl = import.meta.env.VITE_API_URL;
  if (configuredUrl) return `${configuredUrl}/v1`;

  if (typeof window !== 'undefined' && ['localhost', '127.0.0.1'].includes(window.location.hostname)) {
    return 'http://localhost:8000/v1';
  }

  return '/v1';
})();

export async function fetchInventory(warehouse_id?: string): Promise<InventoryItem[]> {
  const url = warehouse_id && warehouse_id !== 'ALL' 
    ? `${API_BASE}/inventory?warehouse_id=${warehouse_id}`
    : `${API_BASE}/inventory`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to fetch inventory');
  return res.json();
}

export async function fetchProducts(): Promise<Product[]> {
  const res = await fetch(`${API_BASE}/products`);
  if (!res.ok) throw new Error('Failed to fetch products');
  return res.json();
}

export async function fetchUsers(): Promise<User[]> {
  const res = await fetch(`${API_BASE}/auth/users`);
  if (!res.ok) throw new Error('Failed to fetch users');
  return res.json();
}

export async function createUser(data: Partial<User>): Promise<User> {
  const res = await fetch(`${API_BASE}/auth/users`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Failed to create user');
  }
  return res.json();
}

export async function receiveShipment(data: {
  tracking_number: string;
  warehouse_id: string;
  seller_id: string;
  items: { product_id: string; quantity: number; condition: string; damage_reason?: string }[];
}): Promise<Shipment> {
  const res = await fetch(`${API_BASE}/receiving/shipments`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Failed to receive shipment');
  }
  return res.json();
}

export async function fetchShipments(warehouse_id?: string): Promise<Shipment[]> {
  const url = warehouse_id && warehouse_id !== 'ALL'
    ? `${API_BASE}/receiving/shipments?warehouse_id=${warehouse_id}`
    : `${API_BASE}/receiving/shipments`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to fetch shipments');
  return res.json();
}

export async function createOrder(data: {
  order_number: string;
  warehouse_id: string;
  seller_id: string;
  customer_name: string;
  items: { product_id: string; quantity: number }[];
}): Promise<Order> {
  const res = await fetch(`${API_BASE}/shipping/orders`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Failed to create order');
  }
  return res.json();
}

export async function shipOrder(order_id: string, weight_lbs: string = '1.5 lbs'): Promise<Order> {
  const res = await fetch(`${API_BASE}/shipping/ship`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ order_id, weight_lbs }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Failed to ship order');
  }
  return res.json();
}

export async function fetchOrders(warehouse_id?: string): Promise<Order[]> {
  const url = warehouse_id && warehouse_id !== 'ALL'
    ? `${API_BASE}/shipping/orders?warehouse_id=${warehouse_id}`
    : `${API_BASE}/shipping/orders`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to fetch orders');
  return res.json();
}

export async function fetchAuditLogs(warehouse_id?: string, search?: string): Promise<AuditLog[]> {
  let url = `${API_BASE}/audit/logs?`;
  if (warehouse_id && warehouse_id !== 'ALL') url += `warehouse_id=${warehouse_id}&`;
  if (search) url += `search=${encodeURIComponent(search)}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to fetch audit logs');
  return res.json();
}

export async function fetchLegacyIssues(): Promise<LegacyIssue[]> {
  const res = await fetch(`${API_BASE}/migration/issues`);
  if (!res.ok) throw new Error('Failed to fetch legacy issues');
  return res.json();
}

export async function reconcileLegacyIssue(issue_id: string, actual_physical_quantity: number, notes?: string): Promise<LegacyIssue> {
  const res = await fetch(`${API_BASE}/migration/reconcile`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ issue_id, actual_physical_quantity, notes }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Failed to reconcile legacy issue');
  }
  return res.json();
}

export async function sendVoiceQuery(user_query: string, warehouse_id?: string): Promise<VoiceAssistantResponse> {
  const res = await fetch(`${API_BASE}/assistant/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_query, warehouse_id }),
  });
  if (!res.ok) throw new Error('Failed to send voice query');
  return res.json();
}
