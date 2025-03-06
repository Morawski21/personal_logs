# Personal Logs

Repository for a personal habit tracking and analytics tool hosted on NAS.

## Features

### Habit Streaks

The Streaks page shows your current and best streaks for your habits. Key features:

- **Dynamic Habit Detection**: The app now automatically detects habits from your Excel/CSV file
- **Habit Management**:
  - Display/hide specific habits using checkboxes
  - See which habits are available in your data vs. which are configured but missing
- **Responsive Layout**: The habit cards adjust automatically based on how many habits you have

### Adding New Habits

To add a new habit:

1. Add a new column in your Excel file (the column name must match a habit defined in `src/config.py`)
2. For binary habits: use 1 for completion, 0 for non-completion
3. For time-based habits: enter minutes spent (20+ minutes counts as completed)
4. Save the Excel file
5. The app will automatically detect the new habit

### Configuring Habits

Habits are defined in `src/config.py` in the `HABITS_CONFIG` dictionary. Each habit needs:

- `color`: HEX color code
- `active`: Boolean (True/False)
- `emoji`: Icon to display
- `type`: Either "binary" or "time"