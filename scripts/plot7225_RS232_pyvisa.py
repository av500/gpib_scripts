#! /usr/bin/env python3.10
import pyvisa as visa
from pyvisa import constants
import time
import sys
import math
cnt = 0
pen = 0
xpos = 0
ypos = 0

def print_hex(data):
	hex_str = ":".join("{:02x}".format(c) for c in data)
	print(hex_str + " | " + str(data) )

def read_string(instr):
	string = ""
	while True:
		byte = instr.read_bytes(1)
		if byte == b'\r' :
			break;
		elif byte != b'\n' :
			string += byte.decode('utf-8')
	return string

def get_buffer():
	instr.write(chr(0x1b) + ".B")
	free = int(read_string(instr))
	return free
		
def send_line(line):
	global cnt
	global pen
	global free
	if len(line) == 0 :
		return

	if line.find("PU") == 0:
		pen = 0;
	elif line.find("PD") == 0:
		pen = 1;
	
	print("SEND {} : {}".format(cnt, line))
	cnt += 1
	#print_hex(line.encode(encoding = 'ASCII'))

	instr.write(line)
			
def handle_CI(line):
	global xpos, ypos

	print("handle_CI")
	if len(line) == 0 :
		return
	nums = line.split(",")
	nlen = len(nums)
	angle = 0;
	if nlen > 2:
		return
	elif nlen == 2 :
		if ";" in nums[1] :
			nums[1] = nums[1][:-1]
		angle = int(nums[1])

	if ";" in nums[0] :
		nums[0] = nums[0][:-1]

	radius = int(nums[0])
	if angle == 0 :
		angle = 6
	old_pen = pen;
	arcs = 360 / angle
	incr = angle * 2.0 * math.pi / 360
	print("r %d, a %d  arcs %d  incr %f" % (radius, angle, arcs, incr))
	for i in range(arcs) :
		x = math.cos(i * incr) * radius
		y = math.sin(i * incr) * radius
		print("i %d, x %f  y %f" % (i, x, y))
		if(i == 0) :
			send_line("PU;")
			# move to start point
			send_line("PA" + str(int(xpos + x)) + "," + str(int(ypos + y)) + ";")
			send_line("PD;")
		else :
			# move to next point
			send_line("PA" + str(int(xpos + x)) + "," + str(int(ypos + y)) + ";")

	# close the arc
	send_line("PA" + str(int(xpos + radius)) + "," + str(int(ypos + 0)) + ";")

	# move back to xpos, ypos
	send_line("PU;")
	send_line("PA" + str(int(xpos)) + "," + str(int(ypos)) + ";")
	if( old_pen == 1 ) :	
		send_line("PD;")

def handle_PA(prefix, line):
	global xpos, ypos
	send_line(prefix)

	if len(line) == 0 :
		return
	nums = line.split(",")
	nlen = len(nums)
	max_len = 16;
	if nlen > 0:
		pos = 0;
		while nlen > 0:
			line = "PA";
			loop = min(max_len, nlen)
			for x in range(loop) :
				#print(nums[pos])
				if ";" in nums[pos] :
					nums[pos] = nums[pos][:-1]
				line = line + nums[pos]
				coord = int(nums[pos])
				if (pos % 2) == 0 :
					xpos = coord
				else :
					ypos = coord
					#print("x %d  y %d  pen %d" % (xpos, ypos, pen))

				if x < loop - 1 :
					line = line + ","
				elif ";" not in nums[pos] :
					line = line + ";"
				pos += 1				
			nlen -= max_len
			send_line(line)

def handle_LB(line):
	global xpos, ypos

	print("handle_LB")
	if len(line) == 0 :
		return
	nums = line.split(";")
	nlen = len(nums)
	if nlen < 2 :
		return;
	send_line("LB" + nums[0] + chr(0x03))
	return;

def handle_DP():
	instr.write("DP;")

	while True :
		instr.write("OS;")
		ret = int(read_string(instr))
		print("status: " + str(ret))
		if ret & 0x04 : 
			break;
		time.sleep(0.5)
	
	instr.write("OD;")
	print("pos:  " + read_string(instr))

rm = visa.ResourceManager('@py')

instr = rm.open_resource("ASRL/dev/ttyUSB0::INSTR") 

instr.baud_rate = 2400
instr.set_visa_attribute(constants.VI_ATTR_ASRL_FLOW_CNTRL, constants.VI_ASRL_FLOW_RTS_CTS)
instr.stop_bits = constants.StopBits.one
instr.parity    = constants.Parity.none
instr.data_bits = 8
instr.read_termination  = '\r'
instr.write_termination = '\r'
instr.timeout = 5000

instr.write("OI;")
print("plotter:  " + read_string(instr))

instr.write("OS;")
print("status:   " + read_string(instr))

instr.write("OE;")
print("error:    " + read_string(instr))

instr.write(chr(0x1b) + ".L")
print("buffer:   " + read_string(instr))

# XONOFF control does not seem to work with the 7225A/B and the 17603A RS232 card
#xon = chr(0x1b) + ".I80;;" + chr(0x13) + ":" + chr(0x1b) + ".N;" + chr(0x11) + ":"
#print_hex(xon.encode(encoding = 'ASCII'))
#instr.write(xon)

if len(sys.argv) < 2 :
	print("usage: plot7225 filename.hpgl")
	exit()

print('plotting: ', str(sys.argv[1]))

filepath = sys.argv[1]

with open(filepath) as fp:
	readline = fp.readline()
	readline = readline.strip()
	
	cnt = 1
	while readline:
		if readline[0] == chr(0x1b) :
			print("ESC!")
			send_line(readline)
			readline = fp.readline()
			continue
		lines = readline.split(";")
		for line in lines:
			if line == "PD0,90":
				print("ignore: {}".format(line))
				continue
			if len(line) == 0 :
				continue
			if line[0] == '\n' or line[0] == '\r':
				continue
			line += ";"
			if line.find("PU") == 0:
				if line.find("PU;") == -1:
					# HP7225A does not understand PUx,y....
					handle_PA("PU;", line[2:])
				else : 
					send_line(line)
			elif line.find("PD") == 0:
				if line.find("PD;") == -1:
					# HP7225A does not understand PDx,y....
					handle_PA("PD;", line[2:])
				else :
					send_line(line)
			elif line.find("PA") == 0:
					# break long PA lines
					handle_PA("", line[2:])
			elif line.find("CI") == 0:
					# handle circle
					handle_CI(line[2:])
			elif line.find("LB") == 0:
					# handle label
					handle_LB(line[2:])
			else :
				send_line(line)

		readline = fp.readline()
