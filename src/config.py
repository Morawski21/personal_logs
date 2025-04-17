# Constants
TIME_COLUMNS = ["Tech + Praca", "YouTube", "Czytanie", "Gitara", "Inne", "Razem"]
WEEKDAY_ORDER = ['PONIEDZIAŁEK', 'WTOREK', 'ŚRODA', 'CZWARTEK', 'PIĄTEK', 'SOBOTA', 'NIEDZIELA']
FILENAME = "Logbook 2025.xlsx"

# Define the fields and their properties
HABITS_CONFIG = {
    "Tech + Praca": {"color": "#21d3ed", "active": True, "emoji": "💻", "type": "time"},
    "YouTube": {"color": "#c085fd", "active": True, "emoji": "🎥", "type": "time"},
    "Czytanie": {"color": "#fbbf23", "active": True, "emoji": "📚", "type": "time"},
    "Gitara": {"color": "#c41a36", "active": True, "emoji": "🎸", "type": "time"},
    "Inne": {"color": "#94a3b8", "active": True, "emoji": "🔧", "type": "time"},
    "20min clean": {"color": "#ff6b6b", "active": True, "emoji": "🧹", "type": "binary"},
    "YNAB": {"color": "#ffcc00", "active": True, "emoji": "💰", "type": "binary"},
    "Anki": {"color": "#00ccff", "active": True, "emoji": "🧠", "type": "binary"},
    "Pamiętnik": {"color": "#ff66cc", "active": True, "emoji": "✒️", "type": "binary"},
    "Plan na jutro": {"color": "#66ff66", "active": True, "emoji": "📝", "type": "binary"},
    "No porn": {"color": "#ff0000", "active": True, "emoji": "🚫", "type": "binary"},
    "No 9gag": {"color": "#ff9500", "active": True, "emoji": "📱", "type": "binary"},
    "Gaming <1h": {"color": "#0000ff", "active": True, "emoji": "🎮", "type": "binary"},
    "sport": {"color": "#ff9900", "active": True, "emoji": "🏃", "type": "description"},
    "accessories": {"color": "#cc00cc", "active": True, "emoji": "💍", "type": "description"},
    "suplementy": {"color": "#00cc00", "active": True, "emoji": "💊", "type": "binary"},
    "Cronometer": {"color": "#00cc00", "active": True, "emoji": "⌚", "type": "binary"}
}

# Function to get active fields
def get_active_fields():
    return {field: props for field, props in HABITS_CONFIG.items() if props["active"]}

def get_column_colors():
    """Return color mapping for specific columns"""
    return {field: props["color"] for field, props in HABITS_CONFIG.items() if "color" in props}
