import csv
import os

class CSVHelper:
    def __init__(self, csv_path: str):
        # Resolve path if not found in current directory
        resolved_path = csv_path
        if not os.path.exists(resolved_path):
            alt_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), csv_path)
            if os.path.exists(alt_path):
                resolved_path = alt_path
            else:
                alt_path2 = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Automation_Testing_POM", csv_path)
                if os.path.exists(alt_path2):
                    resolved_path = alt_path2

        self.file = open(resolved_path, mode="r", newline="", encoding="utf-8")
        self.reader = csv.reader(self.file)
        # Skip header line
        next(self.reader, None)

    def get_next_row(self):
        try:
            return next(self.reader)
        except StopIteration:
            return None

    def close_csv(self):
        if self.file and not self.file.closed:
            self.file.close()

    # Aliases for exact Java compatibility
    getNextRow = get_next_row
    closeCSV = close_csv
