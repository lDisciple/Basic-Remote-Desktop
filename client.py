from PIL import Image
import socket
import pygame
import os
import time
import sys

port = 8080
ip = sys.argv[1]

sw = 640
sh = 480

w = 400
h = 400
mode = "RGB"
scale = 1

running = True
tcpSocket = None

def sendKey(evt):
	if tcpSocket != None and len(evt.unicode) > 0:
		tcpSocket.send((("K"+evt.unicode).ljust(12)).encode())

def sendMousePos(evt):
	if tcpSocket != None:
		mx = int((evt.pos[0]/sw)*w)
		my = int((evt.pos[1]/sh)*h)
		tcpSocket.send((("M"+str(mx)+":"+str(my)).ljust(12)).encode())

def sendMouseClick(evt):
	if tcpSocket != None:
		cmd = "C"
		if evt.type == pygame.MOUSEBUTTONUP:
			if evt.button == 5 or evt.button == 4:
				return # Dont send mouse wheel ups
			cmd += 'U'
		else:
			cmd += 'D'
		cmd += str(evt.button)
		if len(cmd) >= 3:
			tcpSocket.send(cmd.ljust(12).encode())

def quit(evt):
	global running
	running = False;

def updateImage(data):
	f = open('ImageBuffer.png','wb')
	f.write(data)
	f.close()
	img = pygame.image.load('ImageBuffer.png')
	img = pygame.transform.scale(img, (sw, sh))
	#img.save("test.png","PNG")
	screen.blit(img,(0,0))
	pygame.display.flip()
	#pass

#UDP
udpSocket = socket.socket(socket.AF_INET, # Internet
	socket.SOCK_DGRAM) # UDP
udpSocket.bind(('10.42.0.1',port))
udpSocket.settimeout(0.01)
#TCP Setup
tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpSocket.connect((ip,port))
recv = tcpSocket.recv(1024)
tcpSocket.settimeout(0.01)
parts = recv.decode().split("/")
for part in parts:
	keyval = part.split(":")
	if keyval[0] == "MODE":
		mode = keyval[1]
	elif keyval[0] == "WIDTH":
		w = int(keyval[1])
	elif keyval[0] == "HEIGHT":
		h = int(keyval[1])
	elif keyval[0] == "SCALE":
		scale = float(keyval[1])

print(w)
print(h)
print(mode)
pygame.init()
size=(sw,sh)
screen = pygame.display.set_mode(size)

image = Image.open(os.getcwd()+"/pic1.jpg")
fl = open(os.getcwd()+"/pic1.jpg",'rb')
data = fl.read()
fl.close()
updateImage(data)
while running:
	#Manage Keys and Mouse
	for evt in pygame.event.get():
		if evt.type == pygame.QUIT:
			quit(evt)
		elif evt.type == pygame.KEYDOWN:
			sendKey(evt)
		elif evt.type == pygame.MOUSEMOTION:
			sendMousePos(evt)
		elif evt.type == pygame.MOUSEBUTTONUP or evt.type == pygame.MOUSEBUTTONDOWN:
			sendMouseClick(evt)

	#Get image
	try:
		data = udpSocket.recvfrom(65507)
		updateImage(data[0])
	except socket.timeout:	
		pass

	#Check for TCP updates
	try:
		data = tcpSocket.recv(12)
		parts = data.decode()[:-2].split("!~")
		for part in parts:
			if "SCALE:" in part:
				scale = float(part[6:])
			elif part == "CLOSE":
				running = False
	except socket.timeout:	
		pass
	
	time.sleep(0.1)

tcpSocket.send("CLOSE".ljust(12).encode())
tcpSocket.close()
