from datetime import datetime


def time_diff(timestamp):
    current_time = datetime.utcnow()
    t_delta = (current_time - timestamp).total_seconds()
    time_conversions = {"mins": 60, "hrs": 60, "days": 24, "years": 365}
    t_delta_str = "Online"
    for x in time_conversions:
        num = time_conversions[x]
        if t_delta / num > 1:
            t_delta_str = str(int(t_delta // num)) + " " + x + " ago"
            t_delta = t_delta / num
        else:
            break

    return t_delta_str
