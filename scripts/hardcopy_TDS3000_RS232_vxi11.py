#! /usr/bin/env python3
import vxi11
import sys
import struct

def print_hex(data):
	hex_str = ":".join("{:02x}".format(c) for c in data)
	print(hex_str + " | " + str(data) )

def read_bytes(size):
	global instr
	data = bytearray()
	while size > 0:
		buf = instr.read_raw(size)
		size = size - len(buf)
		data.extend(buf)
	return data
		
if len(sys.argv) < 2 :
	print("usage: hardcopy_TDS3000 filename.png")
	exit();

instr = vxi11.Instrument("192.168.1.29", "COM1,488", term_char='\r')
instr.timeout = 5

print("device: " + instr.ask("*IDN?"))

filepath = sys.argv[1]
f = open(filepath, "wb")

instr.write("HARDC:COMPRESS OFF")
instr.write("HARDC:FORM PNG")
instr.write("HARDC:INKS OFF")
instr.write("HARDC:LAY LAN")
instr.write("HARDC:PAL NORM")
instr.write("HARDC:PORT RS232")
instr.write("HARDCOPY START")

data = read_bytes(8)
print_hex(data)
f.write(data)

while 1:
	data = read_bytes(4)
	length = struct.unpack(">I",data)[0]
	print("CHUNK LEN: " + str(length))
	f.write(data)

	chunk = read_bytes(4)
	print_hex(chunk)
	f.write(chunk)
		
	data = read_bytes(length + 4)
	f.write(data)

	if chunk == "IEND" :
		break

print("TOTAL SIZE: " + str(f.tell()))

f.close()

exit()
