from datetime import datetime, timedelta

print("1:")
now = datetime.now()
five_days_ago = now - timedelta(days=5)
print(five_days_ago.strftime('%Y-%m-%d'))

print("2:")
today = datetime.now()
yesterday = today - timedelta(days=1)
tomorrow = today + timedelta(days=1)
print(f"Yesterday: {yesterday.strftime('%Y-%m-%d')}")
print(f"Today: {today.strftime('%Y-%m-%d')}")
print(f"Tomorrow: {tomorrow.strftime('%Y-%m-%d')}")

print("3:")
dt = datetime.now()
dt_no_microseconds = dt.replace(microsecond=0)
print(dt_no_microseconds)

print("4:")
date1 = datetime(2024, 1, 1, 12, 0, 0)
date2 = datetime(2024, 1, 2, 12, 0, 0)
diff = (date2 - date1).total_seconds()
print(int(diff))
