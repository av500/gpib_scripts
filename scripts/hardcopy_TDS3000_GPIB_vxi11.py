#! /usr/bin/env python3
import vxi11
import sys
import struct

if len(sys.argv) < 2 :
	print("usage: hardcopy_TDS3000 filename.png")
	exit();

instr = vxi11.Instrument("192.168.1.29", "gpib0,1")
instr.timeout = 5

print("device: " + instr.ask("*IDN?"))

instr.write("HARDC:COMPRESS OFF")
instr.write("HARDC:FORM PNG")
instr.write("HARDC:INKS OFF")
instr.write("HARDC:LAY LAN")
instr.write("HARDC:PAL NORM")
instr.write("HARDC:PORT GPIB")
instr.write("HARDCOPY START")

data = read_raw()

print("size: " + str(len(data)))

filepath = sys.argv[1]
f = open(filepath, "wb")
f.write(data)
f.close()

exit()
