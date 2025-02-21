# Constants
TIME_COLUMNS = ["Tech + Praca", "YouTube", "Czytanie", "Gitara", "Inne", "Razem"]
WEEKDAY_ORDER = ['PONIEDZIAŁEK', 'WTOREK', 'ŚRODA', 'CZWARTEK', 'PIĄTEK', 'SOBOTA', 'NIEDZIELA']

# Define the fields and their statuses
FIELDS = {
    "Tech + Praca": True,
    "YouTube": True,
    "Czytanie": True,
    "Gitara": True,
    "Inne": True,
    "20min clean": True,
    "YNAB": True,
    "Anki": True,
    "Pamiętnik": True,
    "Plan na jutro": True,
    "No porn": False,
    "Gaming <1h": True,
    "sport": True,
    "accessories": True,
    "suplementy": True
}

# Function to get active fields
def get_active_fields():
    return {field: status for field, status in FIELDS.items() if status}

def get_column_colors():
    """Return color mapping for specific columns"""
    return {
        'Gitara': '#c41a36',
        'YouTube': '#c085fd',
        'Czytanie': '#fbbf23',
        'Tech + Praca': '#21d3ed',
        'Inne': '#94a3b8'
    }
