def convert_time(time_in_seconds):
    time_list = [
                 {'sec': 0},
                 {'mins': 0},
                 {'hrs': 0},
                 {'day': 0},
                ]
    time_list[1]['mins'], time_list[0]['sec'] = divmod(time_in_seconds, 60)
    time_list[2]['hrs'], time_list[1]['mins'] = divmod(time_list[1]['mins'], 60)
    time_list[3]['day'], time_list[2]['hrs'] = divmod(time_list[2]['hrs'], 24)
    time = ""
    for time_unit in time_list:
        for unit in time_unit:
            if time_unit[unit] != 0:
                time = str(time_unit[unit]) + unit + " " + time
    return time


def convert_memory(memory_in_bytes):
    memory_in_mb = memory_in_bytes/(1024.0*1024)
    if memory_in_mb >= 1:
        if (memory_in_mb/1024.0) >= 1:
            return str("%.3f" %(memory_in_mb/1024.0)) + " GB" 
        return str("%.3f" %memory_in_mb) + " MB"
    return str("%.3f" %(memory_in_bytes/1024.0)) + " KB"
