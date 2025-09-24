import keyboard
import time
import datetime

pickup_key = "e"
burst = 15           # number of presses
interval = 0.04      # seconds between presses (40 ms)
sync_interval = 10   # trigger every 10s (00, 10, 20...)

print("Press F8 to arm. Script will fire at the next 10-second mark.")
print("Press F9 to quit.")

def sync_pickup():
    now = datetime.datetime.now()
    # find next multiple of sync_interval
    target_sec = ((now.second // sync_interval) + 1) * sync_interval
    target_time = now.replace(second=0, microsecond=0) + datetime.timedelta(seconds=target_sec)

    wait_time = (target_time - datetime.datetime.now()).total_seconds()
    print(f"Armed! Will fire at {target_time.strftime('%H:%M:%S')} (in {wait_time:.2f}s).")

    time.sleep(wait_time)
    print("Firing burst!")
    for _ in range(burst):
        keyboard.press_and_release(pickup_key)
        time.sleep(interval)
    print("Done.")

keyboard.add_hotkey("f8", sync_pickup)
keyboard.add_hotkey("f9", lambda: exit())
keyboard.wait()
