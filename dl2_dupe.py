import keyboard, time, datetime, sys, threading, os

def main():
	try:
		is_host = threading.Event()		# flag for non-host lag compensation
		pickup_key = "e"	# your interaction key
		sync_interval = 10     # fire at next multiple of 10 seconds
		non_host_lag = 0.12	      # extra wait for non-hosts

		print(f"Press F7 to toggle lag compensation (default: {'On, host = no lag' if is_host.is_set() else 'Off, non-host = lag'}).")
		print("Press F8 to arm. Script will fire at the next 10-second mark.")
		print("Press F9 to quit.")

		keyboard.add_hotkey("f7", toggle_host, args=[is_host])
		keyboard.add_hotkey("f8", sync_pickup, args=[pickup_key, sync_interval, non_host_lag, is_host])
		keyboard.wait("f9")
		print("Exited...")
		sys.exit(0)
	except KeyboardInterrupt:
		print("Force exited...")
		try:
			sys.exit(130)
		except SystemExit:
			os._exit(130)

def sync_pickup(pickup_key, sync_interval, non_host_lag, is_host: threading.Event):
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
	print("Pressed, press F8 to trigger again, F7 to toggle host mode, F9 to quit.")

def toggle_host(is_host: threading.Event):
	is_host.clear() if is_host.is_set() else is_host.set()
	print(f"Host mode is now {'On' if is_host.is_set() else 'Off'}")

if __name__ == "__main__":
	main()