from datetime import datetime, timedelta

def time_diff(timestamp):
    current_time = datetime.utcnow()
    t_delta = (current_time - timestamp).total_seconds()
    time_conversions = {60:'mins', 3600:'hrs', 86400:'days', 31536000:'years'}
    t_delta_str = "Online"
    for x in time_conversions:
        if t_delta/x > 1:
            t_delta_str = str(int(t_delta//x)) + " " + time_conversions[x] + " ago"
            t_delta = t_delta/x
        else:
            break

    return t_delta_str

