import keyboard, time, datetime, sys, threading, os, yaml
from pathlib import Path

CONFIG_PATH = Path("config.yml")
CONFIG_DEFAULTS = {
	"pickup_key": "f",
	"sync_interval": 10,
	"non_host_lag": 0.1,
	"host_mode": False
}

def main():
	try:
		cfg, meta = load_config()
		print(f"Config source: {'file' if meta['loaded'] else 'defaults'} ({meta['path']})")

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
				"error": "No change made."
			},
			"sync_interval": {
				"info": "Enter new sync interval in seconds (int > 0): ",
				"error": "Interval must be > 0. No change made."
			},
			"non_host_lag": {
				"info": "Enter non-host lag compensation in seconds (e.g., 0.12): ",
				"error": "Lag must be >= 0. No change made."
			}
		}
		
		print(f"Configurations set as:\n"
		f"	pickup key: {state['pickup_key']}\n"
		f"	refresh interval {state['sync_interval']} sec\n"
		f"	lag compensation: {int(state['non_host_lag']*1000)} ms\n"
		f"	lag compensation mode: {'On, host = no lag' if is_host.is_set() else 'Off, non-host = lag'}\n")
		print_triggers()

		keyboard.add_hotkey("f2", print_triggers)
		keyboard.add_hotkey("f3", print_config, args=[state, is_host])
		keyboard.add_hotkey("f4", change_config, args=[cfg, state, config_messages, "pickup_key"])
		keyboard.add_hotkey("f5", change_config, args=[cfg, state, config_messages, "sync_interval"])
		keyboard.add_hotkey("f6", change_config, args=[cfg, state, config_messages, "non_host_lag"])
		keyboard.add_hotkey("f7", toggle_host, args=[cfg, is_host])
		keyboard.add_hotkey("f8", sync_pickup, args=[state, is_host])
		keyboard.add_hotkey("f10", reload_defaults, args=[cfg, state, is_host])

		keyboard.wait("f9")
		print("Exited...")
		sys.exit(0)
	except KeyboardInterrupt:
		print("Force exited...")
		try:
			sys.exit(130)
		except SystemExit:
			os._exit(130)

def reload_defaults(cfg: dict, state: dict, is_host: threading.Event):
	confirmation = input("You are about to load default values to the settings. Proceed? (Y/Yes) ").strip().lower()
	if confirmation not in ("y", "yes"):
		print("Did not load defaults")
		return
	try:
		with CONFIG_PATH.open("w", encoding="utf-8") as file:
			yaml.safe_dump(CONFIG_DEFAULTS, file, sort_keys=False)

		cfg.clear()
		cfg.update(CONFIG_DEFAULTS)
		state["pickup_key"] = str(cfg["pickup_key"])
		state["sync_interval"] = int(cfg["sync_interval"])
		state["non_host_lag"] = float(cfg["non_host_lag"])
		if cfg["host_mode"]:
			is_host.set()
		else:
			is_host.clear()

		print("Successfully loaded config defaults.")
	except Exception as e:
		print(f"Warning: failed to load defaults to {CONFIG_PATH}: {e}")
	finally:
		print("Press F8 to trigger, F2 for triggers, F3 for settings, F4–F7 to change, F9 to quit.")


def load_config():
	exists = CONFIG_PATH.exists()
	loaded = False
	overrides = {}

	initial_values = CONFIG_DEFAULTS.copy()

	if exists:
		try:
			with CONFIG_PATH.open("r", encoding="utf-8") as file:
				data = yaml.safe_load(file) or {}
			if isinstance(data, dict):
				overrides = {k: data[k] for k in initial_values.keys() if k in data}
				initial_values.update(overrides)
				loaded = True
			else:
				print("Warning: config.yaml content is not a mapping; using defaults.")
		except Exception as e:
			print(f"Warning: failed to read {CONFIG_PATH}: {e}. Using defaults.")

	meta = {
		"exists": exists,
		"loaded": loaded,
		"overrides": list(overrides.keys()),
		"path": str(CONFIG_PATH)
	}
	return initial_values, meta

def save_config(cfg: dict):
	try:
		with CONFIG_PATH.open("w", encoding="utf-8") as file:
			yaml.safe_dump(cfg, file, sort_keys=False)
	except Exception as e:
		print(f"Warning: failed to save to {CONFIG_PATH}.")

def sync_pickup(state: dict, is_host: threading.Event):
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
	print("Press F8 to trigger, F2 for triggers, F3 for settings, F4–F7 to change, F9 to quit.")
	
def change_config(cfg: dict, state: dict, message: dict, key: str):
	try:
		raw = input(message[key]["info"]).strip()
		if key == "sync_interval":
			val = int(raw)
		elif key == "non_host_lag":
			val = float(raw)
		else:
			val = raw

		if key == "sync_interval" and val <= 0:
			print(message[key]["error"])
			return
		elif key == "non_host_lag" and val < 0.0:
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
	finally:
		print("Press F8 to trigger, F2 for triggers, F3 for settings, F4–F7 to change, F9 to quit.")

def toggle_host(cfg: dict, is_host: threading.Event):
	try:
		is_host.clear() if is_host.is_set() else is_host.set()
		cfg["host_mode"] = bool(is_host.is_set())
		save_config(cfg)
		print(f"Host mode is now {'On' if is_host.is_set() else 'Off'}")
	except Exception as e:
		print(f"Failed to toggle host mode")
	finally:
		print("Press F8 to trigger, F2 for triggers, F3 for settings, F4–F7 to change, F9 to quit.")

def print_config(state, is_host: threading.Event):
	print(f"Configurations set as:\n"
	f"	pickup key: {state['pickup_key']}\n"
	f"	refresh interval {state['sync_interval']} sec\n"
	f"	lag compensation: {int(state['non_host_lag']*1000)} ms\n"
	f"	lag compensation mode: {'On, host = no lag' if is_host.is_set() else 'Off, non-host = lag'}")
	print("Press F8 to trigger, F2 for triggers, F3 for settings, F4–F7 to change, F9 to quit.")
	
def print_triggers():
	print(f"Press F2 to show detailed key triggers\n"
	f"Press F3 to show current settings\n"
	f"Press F4 to change pickup key\n"
	f"Press F5 to change refresh interval\n"
	f"Press F6 to change lag compensation\n"
	f"Press F7 to toggle lag compensation mode (host mode)\n"
	f"Press F8 to arm. Script will fire at the next interval.\n"
	f"Press F9 to quit.\n"
	f"Press F10 to load default settings (irreversible).")

if __name__ == "__main__":
	main()