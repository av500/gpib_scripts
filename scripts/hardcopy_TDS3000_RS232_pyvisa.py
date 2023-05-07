#! /usr/bin/env python3.10
import pyvisa as visa
import sys
import struct

def print_hex(data):
	hex_str = ":".join("{:02x}".format(c) for c in data)
	print(hex_str + " | " + str(data) )

if len(sys.argv) < 2 :
	print("usage: hardcopy_TDS3000 filename.png")
	exit();

rm = visa.ResourceManager('@py')

instr = rm.open_resource('TCPIP::192.168.1.29::COM1,488::INSTR')

print(instr.query("*IDN?"))

filepath = sys.argv[1]
f = open(filepath, "wb")

instr.write("HARDC:COMPRESS OFF")
instr.write("HARDC:FORM PNG")
instr.write("HARDC:INKS OFF")
instr.write("HARDC:LAY LAN")
instr.write("HARDC:PAL NORM")
instr.write("HARDC:PORT RS232")
instr.write("HARDCOPY START")

instr.read_termination = None
instr.end_input = False

data = instr.read_bytes(8)
print_hex(data)
f.write(data)

while 1:
	data = instr.read_bytes(4)
	length = struct.unpack(">I",data)[0]
	print("CHUNK LEN: " + str(length))
	f.write(data)

	chunk = instr.read_bytes(4)
	print_hex(chunk)
	f.write(chunk)
		
	data = instr.read_bytes(length + 4)
	f.write(data)

	if chunk == b'IEND' :
		break

print("TOTAL SIZE: " + str(f.tell()))

f.close()

