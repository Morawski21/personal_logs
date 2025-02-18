import utils
from datetime import datetime

df, loaded_path = utils.load_logbook_data()
# Filter out future dates
df = df[df['Data'] <= datetime.now()]


print(df.tail())