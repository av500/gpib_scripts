#! /usr/bin/env python2.7
import socket
import vxi11
import sys
import os
from datetime import datetime
from subprocess import Popen, PIPE

output = Popen(['logname'], stdout = PIPE)
response = output.communicate()
user = response[0][:-1]

print("+---------------------------------------------+")
print("| MAKE SURE THE FIREWALL IS OPEN FOR PORT 515 |")
print("|       and maybe you need to use sudo!       |")
print("+---------------------------------------------+")
print("")

s = socket.socket()
host_ip   = "192.168.1.22"
host_port = 515
s.bind((host_ip,host_port))
s.listen(5)

scope_ip = "192.168.1.160" 

print("[host] " + host_ip)
print("[user] " + user)
print("[scop] " + scope_ip)

instr = vxi11.Instrument("TCPIP::" + scope_ip + "::INSTR")
print("[IDN?] " + instr.ask("*IDN?"))

instr.write("HARDC:FORM BMPC")
instr.write("HARDC:INKS OFF")
instr.write("HARDC:LAY PORTRAIT")
instr.write("HARDC:PALE NORM")
instr.write("HARDC:PORT ETHER")
instr.write("HARDC:COMPRESS OFF")
instr.write("HARDCOPY START")

while True:
	print("[wait] ...")
	c, addr = s.accept()
	print("[conn] " + repr(addr[0]) + ":" + repr(addr[1]))

	data = c.recv(4096)

#	print("len " + str(len(data)))
#	print(ord(data[0]))

	if(ord(data[0]) != 2) :
		print("not RECEIVE JOB!")
		c.close()
		continue

	print("[JOB ]")
	#ACK
	c.send(bytearray([0]))

	data = c.recv(4096)

#	print("len " + str(len(data)))
#	print(ord(data[0]))

	if ord(data[0]) != 2 :
		print("not CTRL file!")
		c.close()
		continue

	print("[CTRL]")
	#ACK
	c.send(bytearray([0]))
			
	# get CTRL bla
	data = c.recv(4096)
#	print("len " + str(len(data)))
	#ACK
	c.send(bytearray([0]))

	# get 0 octect
	data = c.recv(1)
#	print("len " + str(len(data)))
#	print(ord(data[0]))
	#ACK
	c.send(bytearray([0]))

	data = c.recv(4096)
#	print("len " + str(len(data)))
#	print(ord(data[0]))

	if ord(data[0]) != 3 :
		print("not DATA file!")
		c.close()
		continue

	print("[DATA]")

	#ACK
	c.send(bytearray([0]))

	f = open("__temp.bmp", "wb")
				
	while True:
		data = c.recv(4096)
#		print("len " + str(len(data)))
		if len(data) == 0 :
			#final ACK
			c.send(bytearray([0]))
			break;
		f.write(data)

	c.close()

	f.truncate(f.tell() - 1)
	f.close()

	print("[done] ...")

	if len(sys.argv) < 2 :
		now = datetime.now()
		filepath = now.strftime("TDS3000_%Y%m%d_%H%M%S.png")
	else :
		filepath = sys.argv[1]
		
	print("[file] " + filepath)	
	
	cmd = "convert __temp.bmp {0}".format(filepath)
	os.system(cmd)
	os.system("rm __temp.bmp")

	cmd = "chown {0}:users {1}".format(user, filepath)
	os.system(cmd)

	break

exit()

