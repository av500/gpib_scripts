#! /usr/bin/env python3.10
import pyvisa as visa
import sys

if len(sys.argv) < 2 :
	print("usage: hardcopy_TDS3000 filename.png")
	exit();

rm = visa.ResourceManager('@py')

# local GPIB USB connection:
# instr = rm.open_resource('GPIB0::1::INSTR')

# E5810A GPIB Ethernet Gateway:
instr = rm.open_resource('TCPIP::192.168.1.29::gpib0,1::INSTR')

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

# for some reason read_raw with default "chunk" size does not work, so use 1024
data = instr.read_raw(1024)
print("size " + str(len(data)))
f.write(data)
f.close()

