# utils.py
from datetime import datetime, timedelta

def calculate_dose_times(medication):
    dose_times = []
    current_time = datetime.combine(datetime.today(), medication.time_of_first_dose)
    for _ in range(medication.doses_per_day):
        dose_times.append(current_time.time())
        current_time += timedelta(hours=medication.interval_hours)
    return dose_times