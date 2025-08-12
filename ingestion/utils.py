from datetime import datetime

def compare_utc_date(date_str_before, date_str_after):
    date1 = datetime.strptime(date_str_before, "%Y-%m-%d %H:%M:%S%z")
    date2 = datetime.strptime(date_str_after, "%Y-%m-%d %H:%M:%S%z")
    diff_seconds = abs((date2 - date1).total_seconds())
    return diff_seconds