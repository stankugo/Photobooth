from datetime import timedelta

with open('/proc/uptime', 'r') as f:
    uptime_seconds = float(f.readline().split()[0])
    uptime_string = str(timedelta(seconds = int(uptime_seconds)))
    
    print int(uptime_seconds)
            
    message = 'uptime: ' + uptime_string
    print message