from PIL import Image
import pyscreenshot as ImageGrab  
import socket
import os
import pyautogui

def packageImage(img,quality):
	img = img.convert('L')
	size = (int(img.size[0]*quality),int(img.size[1]*scale))
	img = img.resize(size, Image.ANTIALIAS)
	return img

port = 8081
ip = "localhost"
mouseButtons = {'1':'left','2':'middle','3':'right'} 
#UDP
udpSocket = socket.socket(socket.AF_INET, # Internet
	socket.SOCK_DGRAM) # UDP
clientIP = 'localhost'

#TCP
tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpSocket.bind((ip,port))
tcpSocket.listen(1);
connection,addr = tcpSocket.accept();
connection.settimeout(0.01)
clientIP = addr

scale = 0.6
img = ImageGrab.grab()
connection.send(("MODE:"+img.mode+"/WIDTH:"+str(img.size[0])+"/HEIGHT:"+str(img.size[1])+"/SCALE:"+str(scale)).encode())

mousePos = (0,0)
try:
	while True:
		#Send screen share
		screenGrab = ImageGrab.grab()
		screenGrab = packageImage(screenGrab,scale)
		
		screenGrab.save("buffer.png",'PNG')
		f = open('buffer.png','rb')
		data = f.read()
		f.close()
		
		while len(data) >= 65507:
			scale -= 0.01
			scale = round(scale,2)
			screenGrab = ImageGrab.grab()
			screenGrab = packageImage(screenGrab,scale)
			screenGrab.save("buffer.png",'PNG')
			f = open('buffer.png','rb')
			data = f.read()
			f.close()
		udpSocket.sendto(data, (clientIP[0], port))
		if len(data) > 50000:
			scale += 0.01
			scale = round(scale,2)
			connection.send((("SCALE:"+str(scale)).ljust(12)).encode())
		#Read keys and mouse
		pyautogui.moveTo(mousePos[0],mousePos[1])
		try:
			while True:
				reply = connection.recv(12).decode()
			
				reply = reply.strip()
				if len(reply) > 0:
					if reply[0] == 'K':
						print('key pressed: ' + reply[1])
						#pyautogui.typewrite(reply[1])
					elif reply[0] == 'M':
						x,y = reply[1:].split(":")
						mousePos = (int(x),int(y))
						print('Mouse moved: ' + x + ", " + y)
					elif reply[0] == 'C':
						if reply[2] in mouseButtons:
							if reply[1] == 'U': 
								print('Mouse up: '+reply[2])
								#pyautogui.mouseUp(mousePos[0],mousePos[1],mouseButtons[reply[2]])
							else:
								print('Mouse down: ' + reply[2])
								#pyautogui.mouseUp(mousePos[0],mousePos[1],mouseButtons[reply[2]])
						elif reply[2] == '4' :
							print('Mouse wheeled up')
							#pyautogui.scroll(1)
						elif reply[2] == '5':
							print('Mouse wheeled down')
							#pyautogui.scroll(-1)
						
		except socket.timeout as e:
			pass
finally:
	connection.close()
	udpSocket.close()