
def compare_utc_date(date_before, new_date):
    diff_seconds = abs((new_date - date_before).total_seconds())
    return diff_seconds