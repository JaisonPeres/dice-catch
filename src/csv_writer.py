import pandas as pd # type: ignore
import os

class CsvWriter:
    def __init__(self, filename):
        self.filename = filename
        
        if not os.path.isfile(self.filename):
            with open(self.filename, 'w') as file:
                pass

    def add_row(self, row):
        if os.path.getsize(self.filename) == 0:
            df = pd.DataFrame([row])
            df.to_csv(self.filename, mode='w', sep=';', header=True, index=False)
        else:
            df = pd.DataFrame([row])
            df.to_csv(self.filename, mode='a', header=False, index=False)