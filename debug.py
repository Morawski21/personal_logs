import src.data_handler as data_handler
from datetime import datetime

df, loaded_path = data_handler.get_logbook_data()
print(df.tail())