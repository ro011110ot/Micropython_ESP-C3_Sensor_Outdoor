import time

import ntptime
from machine import RTC  # Import machine.RTC


def cettime():
    """
    Calculates the current Central European Time (CET/CEST) including daylight saving.

    This function assumes the system clock has been previously set to UTC
    (e.g., by `ntptime.settime()`).

    Returns:
        tuple: A tuple formatted for `machine.RTC().datetime()`:
               (year, month, day, weekday, hour, minute, second, subsecond)
               Note: weekday is 1-7 (Monday-Sunday) for RTC.datetime().
    """
    year = time.localtime()[0]

    # Determine DST start and end times for the current year in Europe.
    # DST starts on the last Sunday of March (at 1:00 UTC, which is 2:00 CET)
    # Formula for last Sunday of a month: (31 - (int(5 * year / 4 + X)) % 7)
    # For March (month 3), X=4. For October (month 10), X=1.
    dst_start_utc = time.mktime(
        (year, 3, (31 - (int(5 * year / 4 + 4)) % 7), 1, 0, 0, 0, 0)
    )
    # DST ends on the last Sunday of October (at 1:00 UTC, which is 2:00 CEST)
    dst_end_utc = time.mktime(
        (year, 10, (31 - (int(5 * year / 4 + 1)) % 7), 1, 0, 0, 0, 0)
    )

    now_utc = time.time()

    # Apply timezone offset based on whether DST is active
    if dst_start_utc <= now_utc < dst_end_utc:
        # CEST: Central European Summer (UTC+2 hours)
        offset_seconds = 7200
    else:
        # CET: Central European Time (UTC+1 hour)
        offset_seconds = 3600

    # Convert UTC time to local time with the determined offset
    cet_tuple = time.localtime(now_utc + offset_seconds)

    # `time.localtime()` returns: (year, month, mday, hour, minute, second, weekday_0_6, yearday)
    # `machine.RTC.datetime()` expects: (year, month, mday, weekday_1_7, hour, minute, second, microsecond)
    # Note: `time.localtime()` weekday is 0-6 (Monday=0, Sunday=6).
    # `machine.RTC.datetime()` expects 1-7 (Monday=1, Sunday=7).

    year, month, day, hour, minute, second, weekday_0_6, _ = cet_tuple

    # Adjust weekday format for the RTC
    weekday_1_7 = weekday_0_6 + 1

    # Create the tuple in the format expected by RTC.datetime()
    rtc_tuple = (year, month, day, weekday_1_7, hour, minute, second, 0)

    return rtc_tuple


def sync_time():
    """
    Synchronizes the device's real-time clock (RTC) with an NTP server (UTC)
    and then sets the RTC to Central European Time (CET/CEST).
    Retries a few times if it fails.
    """
    print("Synchronizing RTC with NTP server (UTC)...")

    max_retries = 3
    for attempt in range(max_retries):
        try:
            ntptime.settime()  # Sets RTC to UTC
            time.sleep(2)  # Give RTC a moment to settle

            # Now calculate CET/CEST and set the RTC
            rtc = RTC()
            cet_datetime = cettime()
            rtc.datetime(cet_datetime)

            # Get current time to verify (now in local CET/CEST)
            year, month, day, weekday, hour, minute, second, _ = rtc.datetime()

            # Check if the year is plausible (e.g., > 2023)
            if year > 2023:
                print(
                    f"Time synchronized successfully to CET/CEST: {day:02d}-{month:02d}-{year} {hour:02d}:{minute:02d}:{second:02d}"
                )
                return True
            else:
                raise ValueError(
                    "Invalid time received from NTP server or CET calculation."
                )

        except Exception as e:
            print(
                f"Error synchronizing time (attempt {attempt + 1}/{max_retries}): {e}"
            )
            time.sleep(5)

    print("Failed to synchronize time after several retries.")
    return False
