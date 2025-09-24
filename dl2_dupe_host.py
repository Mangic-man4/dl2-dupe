import keyboard, time, datetime, sys

def main():
	print("Press F8 to arm. Script will fire at the next 10-second mark.")
	print("Press F9 to quit.")
	
	keyboard.add_hotkey("f8", sync_pickup)
	keyboard.wait("f9")
	print("Exited...")
	sys.exit(0)
	
def sync_pickup():
	pickup_key = "e"	# your interaction key
	sync_interval = 10     # fire at next multiple of 10 seconds

	now = datetime.datetime.now()
	# find next multiple of sync_interval
	target_sec = ((now.second // sync_interval) + 1) * sync_interval
	target_time = now.replace(second=0, microsecond=0) + datetime.timedelta(seconds=target_sec)

	wait_time = (target_time - datetime.datetime.now()).total_seconds()
	print(f"Armed! Will fire at {target_time.strftime('%H:%M:%S')} ms "
		  f"(in {wait_time:.2f}s).")

	time.sleep(wait_time)

	keyboard.press_and_release(pickup_key)
	print("Pressed, press again to trigger again.")
	return


if __name__ == "__main__":
	main()