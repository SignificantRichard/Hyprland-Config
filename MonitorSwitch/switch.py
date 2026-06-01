# near unreadable :thumbsup:
import pygame as pg
from subprocess import check_output, run
from json import loads
from time import sleep
from math import sqrt

root = pg.display.set_mode((1080, 610))
bgColor = (0, 0, 0)

class Dragger:
	def __init__(self, info, resolutions):
		self.x = info.getX()
		self.y = info.getY()
		self.w = info.getW()
		self.h = info.getH()
		self.id = info.id
		self.name = info.name
		self.monitor = info
		self.resolutions = resolutions

	def mouseInHitbox(self, scaleDownFactor):
		mx, my = pg.mouse.get_pos()
		mx -= self.x / scaleDownFactor
		my -= self.y / scaleDownFactor

		return 0 < mx < self.w / scaleDownFactor and 0 < my < self.h / scaleDownFactor

	def followMouse(self, scaleDownFactor):
		mx, my = pg.mouse.get_pos()
		self.x, self.y = mx * scaleDownFactor, my * scaleDownFactor
		for resolution in self.resolutions:
			mx = self.x % resolution[0]
			if mx < 400:
				self.x = resolution[0] * int(self.x / resolution[0])

			my = self.y % resolution[1]
			if my < 400:
				self.y = resolution[1] * int(self.y / resolution[1])

class Monitor:
	def __init__(self, info):
		self.id = info["id"]
		self.name = info["name"]
		self.dimensions = (info["width"], info["height"])
		self.position = (info["x"], info["y"])
		self.refreshRate = info["refreshRate"]
		self.scale = info["scale"]
		self.disabled = info["disabled"]

	def getX(self):
		return self.position[0]

	def getY(self):
		return self.position[1]

	def getW(self):
		return self.dimensions[0]

	def getH(self):
		return self.dimensions[1]

	def refresh(self):
		print('false' if self.disabled else 'true')
		run(["hyprctl", "eval",
			"hl.monitor({" +
			f"output = '{self.name}'," +
			f"mode = '{self.getW()}x{self.getH()}@{self.refreshRate}'," +
			f"position = '{self.getX()}x{self.getY()}'," +
			f"scale = {self.scale}," +
			f"disabled = {'false' if self.disabled else 'true'}" +
			"})"
		])

draggers = []

def main():

	def drawButton(x, y, w, h, text="Edit This", font=None):
		color = (255, 255, 255)
		pg.draw.rect(root, color, (x + 5, y, w - 10, h))
		pg.draw.rect(root, color, (x, y + 5, w, h - 10))

		w -= 5
		h -= 5

		pg.draw.circle(root, color, (x + 5, y + 5), 5, draw_top_left=True)
		pg.draw.circle(root, color, (x + 5, y + h), 5, draw_bottom_left=True)
		pg.draw.circle(root, color, (x + w, y + h), 5, draw_bottom_right=True)
		pg.draw.circle(root, color, (x + w, y + 5), 5, draw_top_right=True)

		w += 5
		h += 5

		if not font:
			return

		text = font.render(text, True, (0, 0, 0), None)
		textRect = text.get_rect()
		textRect.center = (x + w / 2, y + h / 2)
		root.blit(text, textRect)

	def checkHitboxes(draggers, scaleDownFactor):
		for dragger in draggers:
			if dragger.mouseInHitbox(scaleDownFactor):
				return dragger
		return None

	pg.font.init()

	mouseState = pg.mouse.get_pressed(num_buttons=3)
	font = pg.font.Font("freesansbold.ttf", 32)

	data = check_output(["hyprctl", "monitors", "-j"])
	data = loads(data)

	numberOfMonitors = len(data)

	global draggers

	perFrameExecEvent = None

	extremes = [0, 0, 0, 0] # 0 l 1 t 2 r 3 b

	resolutions = []
	for i in range(numberOfMonitors):
		resolution = (data[i]["width"], data[i]["height"])
		if not resolution in resolutions:
			resolutions.append(resolution)

	for i in range(numberOfMonitors):
		monitor = Monitor(data[i])
		draggers.append(Dragger(monitor, resolutions))
		extremes[0] = data[i]["x"] if data[i]["x"] < extremes[0] else extremes[0]
		extremes[2] = data[i]["x"] + data[i]["width"] if data[i]["x"] + data[i]["width"] > extremes[2] else extremes[2]
		extremes[1] = data[i]["y"] if data[i]["y"] < extremes[1] else extremes[1]
		extremes[3] = data[i]["y"] + data[i]["height"] if data[i]["y"] + data[i]["height"] > extremes[3] else extremes[3]

	scaleDownFactor = max(
		abs(extremes[0]) + abs(extremes[2]) / root.get_size()[0],
		abs(extremes[1]) + abs(extremes[3]) / root.get_size()[1]
	) * 2

	baseDrawOffset = (1920 / scaleDownFactor, 1080 / scaleDownFactor)

	while True:
		for event in pg.event.get():
			if event.type == pg.QUIT:
				return

		currentMouseState = pg.mouse.get_pressed(num_buttons=3)

		mouseDifferences = []

		for i in range(len(currentMouseState)):
			mouseDifferences.append(currentMouseState[i] != mouseState[i])

		if mouseDifferences[0]: # lclick
			# check hitboxes
			hurt = checkHitboxes(draggers, scaleDownFactor)
			if hurt:
				# clicked a box?
				if currentMouseState[0]:
					# start dragging
					perFrameExecEvent = hurt.followMouse
			if not currentMouseState[0]:
				perFrameExecEvent = None
		if mouseDifferences[1]: # mclick
			print("m2 dif")
		if mouseDifferences[2]: # rclick
			hurt = checkHitboxes(draggers, scaleDownFactor)
			if hurt:
				if not currentMouseState[2]:
					hurt.monitor.disabled = not hurt.monitor.disabled

		if perFrameExecEvent:
			perFrameExecEvent(scaleDownFactor)

		root.fill(bgColor)

		# draw elements
		for dragger in draggers:
			drawButton(
				dragger.x / scaleDownFactor,
				dragger.y / scaleDownFactor,
				dragger.w / scaleDownFactor,
				dragger.h / scaleDownFactor,
				dragger.name,
				font
			)

		pg.display.flip()
		mouseState = currentMouseState
		sleep(1 / 60)

main()

# apply changes
for dragger in draggers:
	print("dragger")
	monitor = dragger.monitor
	monitor.position = (int(dragger.x), int(dragger.y))
	monitor.refresh()

# reapply the wallpaper

run(["pkill", "hyprpaper"])
run(["hyprctl", "eval", 'hl.exec_cmd("hyprpaper &")'])

print("exit")
