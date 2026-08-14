
"""
Voice & Chat Assistant Service for Whitfield Fulfillment WMS.

Processes natural language voice transcripts and text queries to provide
hands-free stock information, order status, and automated action execution.
"""

from typing import Dict, Any, Optional
import json
import os
import re
import urllib.request
from commons.logger import logger
from core.cruds.wms_cruds import CRUDWMS

logging = logger(__name__)


class AssistantService:
    """Assistant natural language processing engine."""

    def __init__(self):
        """Initialize the assistant engine with database CRUD facade."""
        logging.info("Executing AssistantService.__init__")
        self.crud = CRUDWMS()

    def process_query(
        self,
        query: str,
        user_info: Dict[str, Any],
        warehouse_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Parse natural language query and route to domain handler.

        Args:
            query (str): Transcribed spoken text or chat input string.
            user_info (Dict[str, Any]): Active user claim details.
            warehouse_context (Optional[str]): Current active warehouse context ('RENO' / 'COLUMBUS').

        Returns:
            Dict[str, Any]: Dict containing intent, spoken_response, action_executed, and data.
        """
        logging.info(f"Executing AssistantService.process_query for query: '{query}'")
        text = query.lower().strip()
        wh = warehouse_context or user_info.get("facility_scope")
        if wh == "ALL":
            wh = None

        # Intent 1: Stock / Inventory lookup
        if any(w in text for w in [
            "how many", "stock", "quantity", "inventory", "do we have", "count",
            "present", "exists", "exist", "available", "in stock"
        ]):
            return self._handle_stock_query(text, wh)

        # Intent 2: Order status lookup
        elif any(w in text for w in ["order", "shipment status", "pending order", "shipped"]):
            return self._handle_order_query(text, wh)

        # Intent 3: Hands-free Receiving instruction
        elif any(w in text for w in ["receive", "log shipment", "incoming scan"]):
            return self._handle_voice_receive(text, user_info, wh)

        # Intent 4: Hands-free Shipping instruction
        elif any(w in text for w in ["ship order", "dispatch order", "pack order"]):
            return self._handle_voice_ship(text, user_info, wh)

        # Default help
        else:
            gemini_response = self._call_gemini_fallback(text, wh)
            if gemini_response:
                return {
                    "intent": "HELP",
                    "spoken_response": gemini_response,
                    "action_executed": False,
                    "data": {"source": "gemini"},
                }
            return {
                "intent": "HELP",
                "spoken_response": "I can help with stock counts, order status, and hands-free receiving or shipping. Try asking: 'How many units of SKU-101 do we have in Reno?' or 'What is the status of order ORD-501?'.",
                "action_executed": False,
                "data": None,
            }

    def _call_gemini_fallback(self, text: str, wh: Optional[str]) -> Optional[str]:
        """Use Gemini as a fallback chat layer when a valid API key is configured."""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return None

        try:
            inventory_context = self.crud.get_inventory_summary(warehouse_id=wh)
            inventory_summary = "\n".join(
                f"- {item['product_sku']} ({item['product_name']}): {item['quantity_good']} good, {item['quantity_damaged']} damaged in {item['warehouse_id']}"
                for item in inventory_context[:10]
            ) or "No inventory data available."

            prompt = (
                "You are a warehouse operations assistant for Whitfield Fulfillment WMS. "
                "Answer the user's question using the provided inventory summary and keep replies concise. "
                f"Warehouse context: {wh or 'all warehouses'}\n"
                f"Inventory summary:\n{inventory_summary}\n\n"
                f"User question: {text}"
            )

            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.2,
                    "topP": 0.9,
                    "maxOutputTokens": 256,
                },
            }
            data = json.dumps(payload).encode("utf-8")
            model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
            request = urllib.request.Request(
                url=f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent",
                data=data,
                headers={
                    "Content-Type": "application/json",
                    "X-goog-api-key": api_key,
                },
                method="POST",
            )

            with urllib.request.urlopen(request, timeout=30) as response:
                body = json.loads(response.read().decode("utf-8"))
                candidates = body.get("candidates") or []
                if not candidates:
                    return None
                parts = candidates[0].get("content", {}).get("parts", [])
                if not parts:
                    return None
                return parts[0].get("text", "").strip() or None
        except Exception as exc:
            logging.warning(f"Gemini fallback unavailable: {exc}")
            return None

    def _handle_stock_query(self, text: str, wh: Optional[str]) -> Dict[str, Any]:
        """Query inventory levels based on SKU or keyword match."""
        inv_list = self.crud.get_inventory_summary(warehouse_id=wh)

        # Extract SKU if present (e.g. SKU-101, PROD-1, etc.)
        sku_match = re.search(r"(sku-[0-9a-z]+|prod-[0-9a-z]+|wireless|organic|gaming|ergonomic)", text)

        if sku_match:
            term = sku_match.group(1)
            filtered = [
                item for item in inv_list
                if term in item["product_sku"].lower() or term in item["product_name"].lower()
            ]
            if filtered:
                item = filtered[0]
                wh_name = item["warehouse_id"]
                good = item["quantity_good"]
                damaged = item["quantity_damaged"]
                if any(w in text for w in ["present", "exists", "exist", "available", "in stock"]):
                    response_text = f"Yes — {item['product_name']} ({item['product_sku']}) is present in {wh_name} warehouse with {good} good units and {damaged} damaged units available."
                else:
                    response_text = f"We have {good} good units and {damaged} damaged units of {item['product_name']} (SKU: {item['product_sku']}) in {wh_name} warehouse."
                return {
                    "intent": "GET_STOCK",
                    "spoken_response": response_text,
                    "action_executed": False,
                    "data": filtered,
                }
            else:
                return {
                    "intent": "GET_STOCK",
                    "spoken_response": f"No inventory found matching '{term}' in warehouse {wh or 'all locations'}.",
                    "action_executed": False,
                    "data": [],
                }

        # Return total stock summary across SKUs
        total_good = sum(i["quantity_good"] for i in inv_list)
        total_damaged = sum(i["quantity_damaged"] for i in inv_list)
        total_skus = len(set(i["product_sku"] for i in inv_list))

        location_str = f"in {wh}" if wh else "across both Reno and Columbus warehouses"
        response_text = f"Total inventory {location_str}: {total_good} good units and {total_damaged} damaged units across {total_skus} active SKUs."

        return {
            "intent": "GET_STOCK",
            "spoken_response": response_text,
            "action_executed": False,
            "data": inv_list[:5],
        }

    def _handle_order_query(self, text: str, wh: Optional[str]) -> Dict[str, Any]:
        """Query order queue status."""
        orders = self.crud.get_orders(warehouse_id=wh)
        pending = [o for o in orders if o["status"] == "PENDING"]
        shipped = [o for o in orders if o["status"] == "SHIPPED"]

        response_text = f"Currently there are {len(pending)} pending orders awaiting pick and pack, and {len(shipped)} completed orders."
        return {
            "intent": "CHECK_ORDER",
            "spoken_response": response_text,
            "action_executed": False,
            "data": {"pending_count": len(pending), "shipped_count": len(shipped), "pending_orders": pending[:3]},
        }

    def _handle_voice_receive(self, text: str, user_info: Dict[str, Any], wh: Optional[str]) -> Dict[str, Any]:
        """Process hands-free receiving parsing."""
        target_wh = wh or "RENO"
        # Try to parse quantity and SKU/UPC from command like "receive 20 units of SKU-101 tracking TRK-999"
        qty_match = re.search(r"(\d+)\s*(units|pieces|boxes|items)?", text)
        qty = int(qty_match.group(1)) if qty_match else 10
        tracking = f"VOICE-TRK-{re.sub(r'[^0-9]', '', str(hash(text)))[:6]}"

        try:
            shipment, is_dup = self.crud.receive_shipment_atomic(
                tracking_number=tracking,
                warehouse_id=target_wh,
                seller_id="SEL-001",
                user_info=user_info,
                items_data=[{"product_id": "SKU-101", "quantity": qty, "condition": "GOOD"}],
            )
            response_text = f"Successfully received {qty} units into {target_wh} warehouse under tracking reference {tracking}."
            return {
                "intent": "RECEIVE_ITEM",
                "spoken_response": response_text,
                "action_executed": True,
                "data": shipment,
            }
        except Exception as err:
            return {
                "intent": "RECEIVE_ITEM",
                "spoken_response": f"Voice receiving failed: {err}",
                "action_executed": False,
                "data": None,
            }

    def _handle_voice_ship(self, text: str, user_info: Dict[str, Any], wh: Optional[str]) -> Dict[str, Any]:
        """Process hands-free shipping execution."""
        target_wh = wh or "RENO"
        orders = self.crud.get_orders(warehouse_id=target_wh)
        pending = [o for o in orders if o["status"] == "PENDING"]

        if not pending:
            return {
                "intent": "SHIP_ORDER",
                "spoken_response": f"No pending orders available to ship in warehouse {target_wh}.",
                "action_executed": False,
                "data": None,
            }

        target_order = pending[0]
        try:
            shipped_order = self.crud.ship_order_atomic(
                order_id=target_order["id"],
                user_info=user_info,
                weight_lbs="1.8 lbs",
            )
            response_text = f"Successfully shipped order {target_order['order_number']} from {target_wh} warehouse."
            return {
                "intent": "SHIP_ORDER",
                "spoken_response": response_text,
                "action_executed": True,
                "data": shipped_order,
            }
        except Exception as err:
            return {
                "intent": "SHIP_ORDER",
                "spoken_response": f"Failed to ship order {target_order['order_number']}: {err}",
                "action_executed": False,
                "data": None,
            }
