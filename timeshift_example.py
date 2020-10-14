import devicely, os
import pandas as pd

def test_empatica_correctness(read_path, write_path):
    signal_names = ['BVP', 'EDA', 'HR', 'TEMP', 'ACC']
    all_equal = True
    for signal_name in signal_names:
        read_csv = pd.read_csv(os.path.join(read_path, f"{signal_name}.csv"), header=None)
        write_csv = pd.read_csv(os.path.join(write_path, f"{signal_name}.csv"), header=None)
        all_equal &= read_csv.equals(write_csv)

    ibi_read_csv = pd.read_csv(os.path.join(read_path, "IBI.csv"), header=None)
    ibi_write_csv = pd.read_csv(os.path.join(write_path, "IBI.csv"), header=None)
    all_equal &= ibi_read_csv[0].equals(ibi_write_csv[0])
    all_equal &= ibi_read_csv.loc[1:, 1].equals(ibi_write_csv.loc[1:, 1])

    return all_equal

read_path = "data/Empatica"
empatica = devicely.EmpaticaReader(read_path)
print(empatica.joined_dataframe)
#empatica.timeshift()
os.mkdir('new_path')
empatica.write('new_path')
write_path = 'new_path/Empatica_test_data_read'
print(test_empatica_correctness(read_path, write_path))