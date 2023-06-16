#! /usr/bin/env python3.10
from MIDI import MIDIFile
import pyvisa as visa
import time
import sys

start_note = 0

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
	wait  = 0
	last  = 0
	factor = 1.2
	
	while ev :
		if "End Of Track" in str(ev.message) :
			break
		now = ev.time

		if ev.command == 0x90 :
			wait  = now - start
			start = now
			note  = ev.data[0]
			vel   = ev.data[1]

		elif ev.command == 0x80 :
			if wait == start :
				wait = 0
			dur = now - start;
			print("time:" + str(start) + " wait:" + str(wait) + " dur:" + str(dur) + " note:" + str(note) + " vel:" + str(vel) )
			
			if vel >= 100 :
				v = 4
			else :
				v = 3
			d = int(dur * factor)	
			cmd = "BP" + str(note - start_note) + "," + str(d) + "," + str(v)
			#print(cmd)
			instr.write(cmd)

			time.sleep(factor * (wait - last)/1000)
			last = dur
			
		ev = next(tit)
	exit()

	for idx, track in enumerate(c):
		track.parse()
		print(f'Track {idx}:')
		print(str(track))

rm = visa.ResourceManager('@py')

instr = rm.open_resource('GPIB0::1::INSTR')

instr.timeout = 5000

instr.write("OI")
print("device: " + instr.read())

#instr.write("BP0,100,4")

if len(sys.argv) < 2 :
	print("usage: play9111a filename.mid [start_note]")
	print("")
	print("       we can omly play notes 0 - 48,")
	print("       so [start_note] will be subtracted")
	print("       from the MIDI note number")
	
	exit()

if len(sys.argv) > 2 :
	start_note = int(sys.argv[2])
print("playing: " + str(sys.argv[1]) + "  from note: " + str(start_note))

parse(sys.argv[1])

