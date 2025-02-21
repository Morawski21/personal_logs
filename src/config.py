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
    "Pamiętnik": {"color": "#ff66cc", "active": True, "emoji": "📔", "type": "binary"},
    "Plan na jutro": {"color": "#66ff66", "active": True, "emoji": "📝", "type": "binary"},
    "No porn": {"color": "#ff0000", "active": False, "emoji": "🚫", "type": "binary"},
    "Gaming <1h": {"color": "#0000ff", "active": True, "emoji": "🎮", "type": "binary"},
    "sport": {"color": "#ff9900", "active": True, "emoji": "🏃", "type": "description"},
    "accessories": {"color": "#cc00cc", "active": True, "emoji": "💍", "type": "description"},
    "suplementy": {"color": "#00cc00", "active": True, "emoji": "💊", "type": "binary"}
}

def get_fields(types=None, active_only=True, include_system=False):
    """
    Get fields filtered by multiple criteria.
    
    Args:
        types (str|list, optional): One or more field types ('time', 'binary', 'description')
        active_only (bool): Whether to return only active fields
        include_system (bool): Whether to include system columns (Data, WEEKDAY, Razem)
    
    Returns:
        dict: Filtered fields and their properties
    """
    # Convert single type to list for consistent handling
    if isinstance(types, str):
        types = [types]
    
    fields = HABITS_CONFIG.items()
    
    # Apply filters
    if active_only:
        fields = ((k, v) for k, v in fields if v["active"])
    if types:
        fields = ((k, v) for k, v in fields if v["type"] in types)
        
    result = dict(fields)
    
    # Add system columns if requested
    if include_system:
        return list(result.keys()) + ['Data', 'WEEKDAY', 'Razem']
    
    return result

def get_column_colors():
    """Return color mapping for specific columns"""
    return {field: props["color"] for field, props in HABITS_CONFIG.items() if "color" in props}
