# ntp.py
import time
import ntptime
from machine import RTC

def cettime():
    """
    Calculates the current Central European Time (CET/CEST) including daylight saving.
    Expects system clock to be set to UTC.
    """
    year = time.localtime()[0]

    # DST calculation (last Sunday of March and October)
    dst_start_utc = time.mktime(
        (year, 3, (31 - (int(5 * year / 4 + 4)) % 7), 1, 0, 0, 0, 0)
    )
    dst_end_utc = time.mktime(
        (year, 10, (31 - (int(5 * year / 4 + 1)) % 7), 1, 0, 0, 0, 0)
    )

    now_utc = time.time()
    # CEST: UTC+2, CET: UTC+1
    if dst_start_utc <= now_utc < dst_end_utc:
        offset_seconds = 7200 # Summer
    else:
        offset_seconds = 3600 # Winter

    cet_tuple = time.localtime(now_utc + offset_seconds)
    year, month, day, hour, minute, second, weekday_0_6, _ = cet_tuple

    # RTC expects weekday 1-7 (Monday=1)
    return (year, month, day, weekday_0_6 + 1, hour, minute, second, 0)

def sync():
    """
    Synchronizes RTC with NTP server and applies CET/CEST offset.
    """
    print("Synchronizing RTC with NTP server (UTC)...")
    rtc = RTC()
    max_retries = 3
    for attempt in range(max_retries):
        try:
            ntptime.settime()
            if rtc.datetime()[0] > 2021:
                cet_datetime = cettime()
                rtc.datetime(cet_datetime)
                print("Time synchronized successfully to CET/CEST.")
                return True
        except Exception as e:
            print(f"NTP attempt {attempt + 1} failed: {e}")
            time.sleep(2)
    return False