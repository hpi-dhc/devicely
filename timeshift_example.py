import devicely, os
import pandas as pd

empatica_folder = "data/Empatica"
empatica = devicely.EmpaticaReader(empatica_folder)
original_times = empatica.start_times.values()
print(original_times)
empatica.timeshift()
os.mkdir('new_path')
empatica.write('new_path')
new_times = empatica.start_times.values()
print(new_times)