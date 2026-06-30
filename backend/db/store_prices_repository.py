from datetime import datetime, timezone, timedelta
from backend.db.firestore_client import db

PRICE_EXPIRY_DAYS = 30


def _store_id(store_name: str, city: str, state: str) -> str:
    """Deterministic doc ID — same store from different users merges."""
    raw = f"{store_name}_{city}_{state}".lower()
    return raw.replace(" ", "_").replace("/", "_").replace("\\", "_").strip("_")


def save_store_prices(
    uploaded_by: str,
    store_name:  str,
    city:        str,
    state:       str,
    country:     str,
    address:     str,
    items:       dict,          # {"black beans": {"price": 1.29, "unit": "can"}}
    receipt_date: str = None,   # "2026-06-27"
    lat: float = None,
    lng: float = None,
) -> dict:
    """
    Upserts store prices into Firestore.
    Merges new items with existing — newer price wins per item.
    """
    store_id  = _store_id(store_name, city, state)
    now       = datetime.now(timezone.utc)
    expires   = now + timedelta(days=PRICE_EXPIRY_DAYS)
    ref       = db.collection("store_prices").document(store_id)
    existing  = ref.get()

    # Merge existing items with new ones (new price wins)
    merged_items = {}
    if existing.exists:
        merged_items = existing.to_dict().get("items", {})

    for item_name, item_data in items.items():
        key = item_name.lower().strip()
        merged_items[key] = {
            "price":      item_data.get("price"),
            "unit":       item_data.get("unit", ""),
            "updated_at": now,
        }

    doc = {
        "store_id":    store_id,
        "store_name":  store_name.strip(),
        "address":     address.strip() if address else "",
        "city":        city.strip(),
        "state":       state.strip(),
        "country":     country.strip(),
        "items":       merged_items,
        "uploaded_by": uploaded_by,
        "receipt_date": receipt_date or now.strftime("%Y-%m-%d"),
        "expires_at":  expires,
        "updated_at":  now,
    }
    if lat is not None: doc["lat"] = lat
    if lng is not None: doc["lng"] = lng

    ref.set(doc, merge=True)
    print(f"[store_prices] saved {len(merged_items)} items for {store_name} ({city}, {state})")
    return {"store_id": store_id, "item_count": len(merged_items)}


def get_store_prices(store_name: str, city: str, state: str) -> dict:
    """Returns price dict for a specific store. {} if not found or expired."""
    store_id = _store_id(store_name, city, state)
    try:
        doc = db.collection("store_prices").document(store_id).get()
        if not doc.exists:
            return {}
        data = doc.to_dict()
        # Check expiry
        expires_at = data.get("expires_at")
        if expires_at and expires_at < datetime.now(timezone.utc):
            print(f"[store_prices] prices expired for {store_name}")
            return {}
        return data.get("items", {})
    except Exception as e:
        print(f"[store_prices] error fetching prices: {e}")
        return {}


def get_stores_in_city(city: str, state: str) -> list:
    """Returns all stores with prices in a given city."""
    try:
        now  = datetime.now(timezone.utc)
        docs = (
            db.collection("store_prices")
            .where("city",  "==", city.strip())
            .where("state", "==", state.strip())
            .stream()
        )
        results = []
        for doc in docs:
            data = doc.to_dict()
            expires_at = data.get("expires_at")
            if expires_at and expires_at < now:
                continue  # skip expired
            results.append({
                "store_id":   data.get("store_id"),
                "store_name": data.get("store_name"),
                "address":    data.get("address"),
                "city":       data.get("city"),
                "state":      data.get("state"),
                "item_count": len(data.get("items", {})),
                "updated_at": data.get("updated_at"),
            })
        return results
    except Exception as e:
        print(f"[store_prices] error listing stores in {city}: {e}")
        return []


def get_real_price(item: str, store_name: str, city: str, state: str) -> float | None:
    """
    Returns real price for an item at a store, or None if not found.
    Used by store_finder.py to override mock prices.
    """
    prices = get_store_prices(store_name, city, state)
    item_lower = item.lower().strip()

    # Exact match first
    if item_lower in prices:
        return prices[item_lower].get("price")

    # Partial match — "black beans" matches "canned black beans"
    for key, val in prices.items():
        if item_lower in key or key in item_lower:
            return val.get("price")

    return None
