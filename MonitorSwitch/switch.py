# near unreadable :thumbsup:

import tkinter as tk
from subprocess import check_output, run
from json import loads

root = tk.Tk()

selectedMonitor = None

def forceMonitorToPlayNice(monitor):
	run(["hyprctl", "eval",
		"hl.monitor({" +
		f'output="{monitor[1]}",' +
		f"disabled={monitor[4]}," +
		f"scale={monitor[5]}," +
		f"position='{monitor[6]}x{monitor[7]}'," +
		f"mode='{monitor[2]}x{monitor[3]}@{monitor[8]}'" +
		"})"
	])

def changeMonitorState(monitor, monitors):
	amountOn = 0
	for m in monitors:
		if not m[4]:
			amountOn += 1
		if amountOn > 1:
			break
	if amountOn == 1 and not findMonitors()[monitor[0]][4]:
		return
	elif amountOn == 0:
		run(["hyprctl", "reload"])

	run(["hyprctl", "eval",
		"hl.monitor({" +
		f'output="{monitor[1]}",' +
		f"disabled={'false' if findMonitors()[monitor[0]][4] else 'true'}," +
		f"scale={monitor[5]}," +
		f"position='{monitor[6]}x{monitor[7]}'," +
		f"mode='{monitor[2]}x{monitor[3]}@{monitor[8]}'" +
		"})"
	])

	for i in range(len(monitors)):
		if i == monitor[0]:
			continue
		forceMonitorToPlayNice(monitors[i])

	root.destroy()

def checkCollisions(monitors):
	# returns offending monitor, and collided monitor

	# x check
	def checkColliderX(ox, ow, cx, cw):
		if ox < cx and ox + ow > cx or cx < ox and cx + cw > cx:
			return True
		return ox == cx

	# y check
	def checkColliderY(oy, oh, cy, ch):
		if oy < cy and ox + ow > cx or cx < ox and cx + cw > cx:
			return True
		return oy == cy

	for offender in monitors:
		for collided in monitors:
			ox, oy, ow, oh = offender[6], offender[7], offender[2], offender[3]
			cx, cy, cw, ch = collided[6], collided[7], collided[2], collided[3]

			print(ox, oy, ow, oh)
			print(cx, cy, cw, ch)

			if checkColliderX(ox, ow, cx, cw) and checkColliderY(oy, oh, cy, ch):
				print("collided")
				return offender, collided

	return None, None

def monitorPositionChange(monitor, secondMonitor, monitors):
	# edit monitor data
	# 6 x 7 y

	# xor swap x
	monitor[6] ^= secondMonitor[6]
	secondMonitor[6] ^= monitor[6]
	monitor[6] ^= secondMonitor[6]

	# xor swap y
	monitor[7] ^= secondMonitor[7]
	secondMonitor[7] ^= monitor[7]
	monitor[7] ^= secondMonitor[7]

	monitors[monitor[0]] = monitor
	monitors[secondMonitor[0]] = secondMonitor

	print(monitor, secondMonitor)

	# check collisions
	offender, collided = checkCollisions(monitors)

	depth = 0

	# move things to the right if monitor takes offence
	# while offender != None and depth < len(monitors):
	# 	depth += 1
	# 	offender, collided = checkCollisions(monitors)

	# temp move monitor off somewhere
	forceMonitorToPlayNice([
		secondMonitor[0],
		secondMonitor[1],
		secondMonitor[2],
		secondMonitor[3],
		secondMonitor[4],
		secondMonitor[5],
		-99999,
		-99999,
		secondMonitor[8]
	])
	forceMonitorToPlayNice(monitor)
	forceMonitorToPlayNice(secondMonitor)
	root.destroy()

def monitorSelectionContext(monitor, monitors):
	global selectedMonitor
	if monitor == selectedMonitor:
		changeMonitorState(monitor, monitors)
	elif monitor != selectedMonitor and selectedMonitor != None:
		# swap places | selectedMonitor <=x=> monitor
		monitorPositionChange(selectedMonitor, monitor, monitors)
	selectedMonitor = monitor

class MonitorSelect:
	def __init__(self, monitor, total, twidth, monitors):
		self.me = tk.Button(
			root,
			text=monitor[1],
			command=lambda: monitorSelectionContext(monitor, monitors)
		)
		self.info = monitor

def findMonitors():
	raw = check_output(["hyprctl", "monitors", "all", "-j"])
	raw = loads(raw)
	monitors = []

	for monitor in raw:
		obj = [ # magic numbers :)
			monitor["id"],		# 0
			monitor["name"],	# 1
			monitor["width"],	# 2
			monitor["height"],	# 3
			monitor["disabled"],	# 4
			monitor["scale"],	# 5
			monitor["x"],		# 6
			monitor["y"],		# 7
			monitor["refreshRate"]	# 8
		]

		monitors.append(obj)
	return monitors


def main():
	root.title("Monitor Selection")
	root.resizable(False, False)

	monitors = findMonitors()
	totalMonitors = len(monitors)
	length = 250 * totalMonitors

	root.geometry(f"{length + 100}x250")

	topLeft = [9999999, 9999999]

	monitorObjects = []
	for i in range(totalMonitors):
		monitor = MonitorSelect(monitors[i], totalMonitors, length, monitors)
		topLeft[0] = topLeft[0] if topLeft[0] < monitor.info[6] else monitor.info[6]
		topLeft[1] = topLeft[1] if topLeft[1] < monitor.info[7] else monitor.info[7]
		monitorObjects.append(monitor)
	x, y, topLeft = topLeft[0], topLeft[1], None
	for monitor in monitorObjects:
		monitor.me.place(x=50 + (monitor.info[6] - x) / monitor.info[2] * length / totalMonitors, rely=0.125, width=length / totalMonitors, relheight=0.75)

	root.mainloop()

main()

# reapply the wallpaper

run(["pkill", "hyprpaper"])
run(["hyprctl", "eval", 'hl.exec_cmd("hyprpaper &")'])
