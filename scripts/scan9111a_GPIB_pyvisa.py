#! /usr/bin/env python3.10
import pyvisa as visa
import time
import sys
import math

def twos(val, ):
	"""compute the 2's complement of int value val"""
	if (val & (1 << 15)) != 0:
		val = val - (1 << 16)
	return val

def verbose_status(s):
	if s & 4 :
		print("DPT ", end='')
	else :
		print("--- ", end='')
#	if s & 8 :
#		print("INI ", end='')
#	else :
#		print("--- ", end='')
#	if s & 16:
#		print("RDY ", end='')
#	else :
#		print("--- ", end='')
	if s & 32:
		print("ERR ", end='')
	else :
		print("--- ", end='')
	if s & 64:
		print("SRQ ", end='')
	else :
		print("--- ", end='')
	if s & 128 :
		print("KEY ", end='')
	else :
		print("--- ", end='')
	if s & 256 :
		print("PRO ", end='')
	else :
		print("--- ", end='')
#	if s & 512 :
#		print("CUR ", end='')
#	else :
#		print("--- ", end='')
	if s & 1024 :
		print("PEN ", end='')
	else :
		print("--- ", end='')
	print("")

def scan_raw():
	while True :
		data = instr.read_bytes(6);
		x = twos(data[1] + (data[0] << 8))
		y = twos(data[3] + (data[2] << 8))
		s = data[5] + (data[4] << 8)
		print(str(x) + "  " + str(y) + "   ", end='')
		verbose_status(s)

		if s & 256 :
			note = x / 250
			if note < 0 :
				note = 0
			if note > 48 :
				note = 48
			note = int(note)

			dur = y / 100 + 10
			if dur < 10 :
				dur = 10
			dur = int(dur)

			cmd = "BP" + str(note) + "," + str(dur) + "," + str(4)
			print(cmd)
			instr.write(cmd)
		else :
			time.sleep(0.01);

def scan_hpgl():
	while True :
		instr.write("DP")

		while True :
			instr.write("OS")
			ret = int(instr.read())
			if ret & 0x80 : 
				instr.write("OK")
				print("key:    " + instr.read())
				instr.write("SK")
			if ret & 512 : 
				instr.write("OC")
				print("cursor: " + instr.read())
			time.sleep(0.01)

		instr.write("OD")
		print("pos:    " + instr.read())
    
rm = visa.ResourceManager('@py')

instr = rm.open_resource('GPIB0::1::INSTR')

instr.timeout = 1000;

print(instr.read_stb())

if 1 :
	scan_raw()
else :
	instr.write("OI")
	print("plotter:  " + instr.read())

	instr.write("OS")
	print("status:   " + instr.read())

	instr.write("OE")
	print("error:    " + instr.read())

	scan_hpgl()

