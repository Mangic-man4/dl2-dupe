import keyboard
import time
import datetime

pickup_key = "e"
sync_interval = 10    # trigger every 10s (00, 10, 20...)
lag_delay = 0.08      # 80 ms compensation delay

print("Press F8 to arm. Script will fire at the next 10-second mark + lag delay.")
print("Press F9 to quit.")

def sync_pickup():
    now = datetime.datetime.now()
    # find next multiple of sync_interval
    target_sec = ((now.second // sync_interval) + 1) * sync_interval
    target_time = now.replace(second=0, microsecond=0) + datetime.timedelta(seconds=target_sec)

    wait_time = (target_time - datetime.datetime.now()).total_seconds()
    print(f"Armed! Will fire at {target_time.strftime('%H:%M:%S')} + {int(lag_delay*1000)} ms "
          f"(in {wait_time:.2f}s).")

    time.sleep(wait_time + lag_delay)  # add the compensation here
    keyboard.press_and_release(pickup_key)
    print("Pickup pressed.")

keyboard.add_hotkey("f8", sync_pickup)
keyboard.add_hotkey("f9", lambda: exit())
keyboard.wait()
