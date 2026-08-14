import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# Ensure directories exist
for dir_path in [DATA_DIR, STATIC_DIR, TEMPLATES_DIR]:
    dir_path.mkdir(exist_ok=True)

# Application settings
APP_CONFIG = {
    "app_name": "Northstar Support Bot",
    "version": "1.0.0",
    "debug": True,
    "secret_key": os.urandom(24).hex(),
    
    # Data settings
    "data_dir": str(DATA_DIR),
    "orders_file": str(DATA_DIR / "orders.json"),
    "inventory_file": str(DATA_DIR / "inventory.json"),
    "chat_history_dir": str(DATA_DIR / "chat_history"),
    
    # UI settings
    "max_message_length": 500,
    "chat_history_limit": 100,
    
    # Support categories
    "support_categories": [
        "order_status",
        "returns_refunds",
        "stock_availability"
    ],
    
    # Quick replies
    "quick_replies": [
        {"label": "📦 Order Status", "text": "I need to check my order status"},
        {"label": "🔄 Returns", "text": "How do I return an item?"},
        {"label": "📊 Stock", "text": "Is the Smart Watch in stock?"},
        {"label": "💬 Other", "text": "I have a different question"}
    ]
}