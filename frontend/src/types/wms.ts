export type UserRole = 'OWNER' | 'MANAGER' | 'TRUSTED_STAFF' | 'NEW_HIRE';

export interface User {
  id: string;
  username: string;
  email?: string;
  full_name: string;
  role: UserRole;
  facility_scope?: string | null;
  status?: string;
  created_by?: string;
  access_token?: string;
}

export interface InventoryItem {
  id: string;
  product_id: string;
  product_sku: string;
  product_upc: string;
  product_name: string;
  warehouse_id: 'RENO' | 'COLUMBUS';
  seller_id: string;
  seller_name: string;
  quantity_good: number;
  quantity_damaged: number;
  updated_at: string;
}

export interface Product {
  id: string;
  sku: string;
  upc: string;
  name: string;
  description?: string;
  seller_id: string;
}

export interface ShipmentItemLine {
  product_sku: string;
  product_name: string;
  quantity: number;
  condition: 'GOOD' | 'DAMAGED';
  damage_reason?: string;
  internal_barcode?: string;
}

export interface Shipment {
  id: string;
  tracking_number: string;
  ticket_number?: string;
  warehouse_id: 'RENO' | 'COLUMBUS';
  seller_id: string;
  status: 'PENDING' | 'RECEIVED';
  created_by_user_id: string;
  received_at?: string;
  created_at: string;
  is_duplicate_attempt?: boolean;
  items?: ShipmentItemLine[];
}

export interface OrderItemLine {
  product_sku: string;
  product_name: string;
  quantity: number;
}

export interface Order {
  id: string;
  order_number: string;
  warehouse_id: 'RENO' | 'COLUMBUS';
  seller_id: string;
  customer_name?: string;
  status: 'PENDING' | 'SHIPPED' | 'CANCELLED';
  created_by_user_id: string;
  shipped_at?: string;
  weight_lbs?: string;
  created_at: string;
  items?: OrderItemLine[];
}

export interface AuditLog {
  id: string;
  timestamp: string;
  user_id: string;
  user_name: string;
  role: string;
  warehouse_id?: string;
  action: string;
  entity_type: string;
  entity_id: string;
  old_value?: any;
  new_value?: any;
  details?: string;
}

export interface LegacyIssue {
  id: string;
  issue_type: string;
  description: string;
  warehouse_id: 'RENO' | 'COLUMBUS';
  seller_name: string;
  product_sku: string;
  excel_quantity: number;
  actual_physical_quantity?: number | null;
  status: 'UNRESOLVED' | 'RECONCILED';
}

export interface VoiceAssistantResponse {
  intent: string;
  spoken_response: string;
  action_executed: boolean;
  data?: any;
}
