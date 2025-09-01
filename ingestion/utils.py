import os
import csv

def compare_utc_date(date_before, new_date):
    diff_seconds = abs((new_date - date_before).total_seconds())
    return diff_seconds


def save_waiting_data_into_csv(table_name, price, date):
    os.makedirs("waiting_data_store", exist_ok=True)
    filepath = os.path.join("waiting_data_store", table_name+".csv")
    with open(filepath, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([price, date])
    print(f"DATA SAVE into {filepath}")
