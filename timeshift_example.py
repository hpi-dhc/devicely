import devicely, os
import pandas as pd

empatica_folder = "data/Empatica"
empatica = devicely.EmpaticaReader(empatica_folder)
original_times = empatica.start_times.values()
print(original_times)
empatica.timeshift(pd.Timedelta(1, unit='d'))
os.mkdir("new_path")
empatica.write("new_path")
new_empatica_folder = "new_path/Empatica"
empatica = devicely.EmpaticaReader(new_empatica_folder)
shifted_times = empatica.start_times.values()
print(shifted_times)