import keyboard, time, datetime, sys, threading, os, yaml
from pathlib import Path

CONFIG_PATH = Path("config.yml")

def main():
	try:
		cfg = load_config()
		is_host = threading.Event()		# flag for non-host lag compensation

		if cfg["host_mode"]:
			is_host.set()

		state = {
			"pickup_key": str(cfg["pickup_key"]),
			"sync_interval": int(cfg["sync_interval"]),
			"non_host_lag": float(cfg["non_host_lag"])
		}

		config_messages = {
			"pickup_key": {
				"info": "Enter new pickup key (single key, e.g. 'e'): ",
				"error": "Interval must be > 0. No change made."
			},
			"sync_interval": {
				"info": "Enter new sync interval in seconds (int > 0): ",
				"error": "Lag must be >= 0. No change made."
			},
			"non_host_lag": {
				"info": "Enter non-host lag compensation in seconds (e.g., 0.12): ",
				"error": "No change made."
			}
		}


		
		print(f"Press F4 to change pickup key (set as: {state['pickup_key']})")
		print(f"Press F5 to change refresh interval (set as: {state['sync_interval']})")
		print(f"Press F6 to change lag compensation timer (set as: {state['non_host_lag']})")
		print(f"Press F7 to toggle lag compensation (set as: {'On, host = no lag' if is_host.is_set() else 'Off, non-host = lag'}).")
		print("Press F8 to arm. Script will fire at the next 10-second mark.")
		print("Press F9 to quit.")

		keyboard.add_hotkey("f4", change_config, args=[cfg, state, config_messages, "pickup_key"])
		keyboard.add_hotkey("f5", change_config, args=[cfg, state, config_messages, "sync_interval"])
		keyboard.add_hotkey("f6", change_config, args=[cfg, state, config_messages, "non_host_lag"])
		keyboard.add_hotkey("f7", toggle_host, args=[cfg, is_host])
		keyboard.add_hotkey("f8", sync_pickup, args=[state, is_host])

		keyboard.add_hotkey("f7", toggle_host, args=[is_host])
		keyboard.add_hotkey("f8", sync_pickup, args=[state, is_host])
		keyboard.wait("f9")
		print("Exited...")
		sys.exit(0)
	except KeyboardInterrupt:
		print("Force exited...")
		try:
			sys.exit(130)
		except SystemExit:
			os._exit(130)


def load_config():
	defaults = {
		"pickup_key": "f",
		"sync_interval": 10,
		"non_host_lag": 0.1,
		"host_mode": False
	}

	if CONFIG_PATH.exists():
		with CONFIG_PATH.open("r", encoding="utf-8") as file:
			data = yaml.safe_load(file) or {}
		defaults.update({key: data.get(key, value) for key, value in defaults.items()})

	return defaults

def save_config(cfg: dict):
	with CONFIG_PATH.open("w", encoding="utf-8") as file:
		yaml.safe_dump(cfg, file, sort_keys=False)

def sync_pickup(state, is_host: threading.Event):
	pickup_key = state["pickup_key"]
	sync_interval = state["sync_interval"]
	non_host_lag = state["non_host_lag"]
	
	lag_delay = 0.0 if is_host.is_set() else non_host_lag

	now = datetime.datetime.now()
	# find next multiple of sync_interval
	target_sec = ((now.second // sync_interval) + 1) * sync_interval
	target_time = now.replace(second=0, microsecond=0) + datetime.timedelta(seconds=target_sec)

	wait_time = (target_time - datetime.datetime.now()).total_seconds()
	print(f"Will press key at {target_time.strftime('%H:%M:%S')}, with {int(lag_delay*1000)} ms lag compensation "
		  f"(in {wait_time:.2f}s).")

	time.sleep(max(0.0, wait_time + lag_delay))

	keyboard.press_and_release(pickup_key)
	print("Pressed, press F8 to trigger again, F5-F7 to change settings, F9 to quit.")
	
def change_config(cfg: dict, state: dict, message: dict, key: str):
	try:
		raw = input(message[key]["info"]).strip()
		if key == "sync_interval" and val <= 0:
			val = int(raw)
		elif key == "non_host_lag" and val <= 0.0:
			val = float(raw)
		else:
			val = raw

		if key == "sync_interval" and val <= 0:
			print(message[key]["error"])
			return
		elif key == "non_host_lag" and val <= 0.0:
			print(message[key]["error"])
			return
		elif key == "pickup_key" and not val:
			print(message[key]["error"])
			return
			
		state[key] = val
		cfg[key] = val
		save_config(cfg)
		print(f"Saved {key} = {val}")
	except Exception as e:
		print(f"Failed to change {key}: {e}")

def toggle_host(cfg: dict, is_host: threading.Event):
	is_host.clear() if is_host.is_set() else is_host.set()
	cfg["host_mode"] = bool(is_host.is_set())
	save_config(cfg)
	print(f"Host mode is now {'On' if is_host.is_set() else 'Off'} (saved)")

if __name__ == "__main__":
	main()