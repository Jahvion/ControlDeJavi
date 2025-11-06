import json
import os
from datetime import datetime
from typing import List, Dict, Optional

DATA_FILE = 'data/products.json'
CATEGORIES = ['Gaseosas', 'Aguas', 'Chocolates', 'Alfajores', 'Golosinas']

def ensure_data_file():
    os.makedirs('data', exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump({"products": [], "next_id": 1}, f)

def load_data() -> Dict:
    ensure_data_file()
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data: Dict):
    ensure_data_file()
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def add_product(name: str, category: str, expiration_date: str) -> Dict:
    if category not in CATEGORIES:
        raise ValueError(f"Category must be one of: {', '.join(CATEGORIES)}")
    
    try:
        datetime.strptime(expiration_date, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Expiration date must be in YYYY-MM-DD format")
    
    data = load_data()
    product = {
        "id": data["next_id"],
        "name": name,
        "category": category,
        "expiration_date": expiration_date,
        "created_at": datetime.now().isoformat()
    }
    
    data["products"].append(product)
    data["next_id"] += 1
    save_data(data)
    
    return product

def list_products(category: Optional[str] = None) -> List[Dict]:
    data = load_data()
    products = data["products"]
    
    if category:
        if category not in CATEGORIES:
            raise ValueError(f"Category must be one of: {', '.join(CATEGORIES)}")
        products = [p for p in products if p["category"] == category]
    
    return sorted(products, key=lambda x: x["expiration_date"])

def delete_product(product_id: int) -> bool:
    data = load_data()
    initial_length = len(data["products"])
    data["products"] = [p for p in data["products"] if p["id"] != product_id]
    
    if len(data["products"]) < initial_length:
        save_data(data)
        return True
    return False

def get_product_by_id(product_id: int) -> Optional[Dict]:
    data = load_data()
    for product in data["products"]:
        if product["id"] == product_id:
            return product
    return None
