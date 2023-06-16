#! /usr/bin/env python3.10
from MIDI import MIDIFile
import pyvisa as visa
import time
import sys

def parse(file):
	c = MIDIFile(file)
	c.parse()
	print(str(c))
	
	cit=iter(c)
	
	t = next(cit)
	t = next(cit)
	t.parse()

	tit = iter(t)
	ev = next(tit)
	start = 0
	dur   = 0
	while ev :
		if "End Of Track" in str(ev.message) :
			break
		time = ev.time
		if ev.command == 0x80 :
			dur = time - start;
			print("time:" + str(start) + " dur:" + str(dur) + " note:" + str(note) + " vel:" + str(vel) )
#			print("OFF :" + str(dur) + "   " + str(ev.data[0]) )
		elif ev.command == 0x90 :
			start = time;
			note  = ev.data[0]
			vel   = ev.data[1]
#			print("ON  :" + str(start) + "   " + str(ev.data[0]) + " : "+ str(ev.data[1])) 
		ev = next(tit)
	exit()

	for idx, track in enumerate(c):
		track.parse()
		print(f'Track {idx}:')
		print(str(track))

parse(sys.argv[1])
exit()

rm = visa.ResourceManager('@py')

instr = rm.open_resource('GPIB0::1::INSTR')

instr.timeout = 5000

instr.write("OI")
print("device: " + instr.read())

if len(sys.argv) < 2 :
	print("usage: play9111 filename.mid")
	exit()

print('playing: ', str(sys.argv[1]))

parse(sys.argv[1])

