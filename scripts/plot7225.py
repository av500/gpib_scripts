#! /usr/bin/env python2.7
import vxi11
import time
import sys
import math

cnt = 0
pen = 0
xpos = 0
ypos = 0

def send_line(line):
	global cnt
	global pen
	if len(line) == 0 :
		return

	if line.find("PU") == 0:
		pen = 0;
	elif line.find("PD") == 0:
		pen = 1;
	
	print("SEND {} : {}".format(cnt, line))
	cnt += 1

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



#instr = vxi11.Instrument("192.168.1.134", "gpib0,5", term_char = '\r')
instr = vxi11.Instrument("192.168.1.29", "COM1,488", term_char = '\r')

print("plotter:  " + instr.ask("OI;"))

print 'plotting:', str(sys.argv[1])

filepath = sys.argv[1]

with open(filepath) as fp:
	readline = fp.readline()
	readline = readline.strip();
	
	cnt = 1
	while readline:
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
			else :
				send_line(line)

		readline = fp.readline()
