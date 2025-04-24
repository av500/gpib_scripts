##
## DOES NOT WORK!
##


#! /usr/bin/env python3.10
import pyvisa as visa
import sys

if len(sys.argv) < 2 :
	print("usage: hardcopy_FSEx filename.png")
	exit();

rm = visa.ResourceManager('@py')

# local GPIB USB connection:
instr = rm.open_resource('GPIB0::7::INSTR')

# E5810A GPIB Ethernet Gateway:
#instr = rm.open_resource('TCPIP::192.168.1.29::gpib0,7::INSTR')

print(instr.query("*IDN?"))

instr.write(":HCOPy:DEST1 'SYST:COMM:GPIB'")
instr.write(":HCOPy:DEV:LANG1 'HPGL'")

print(instr.query(":HCOPy:DEST1?"))
print(instr.query(":HCOPy:DEV:LANG1?"))
instr.write("BEEP")

instr.close()

exit()


# for some reason read_raw with default "chunk" size does not work, so use 1024
data = instr.read_raw(1024)
print("size " + str(len(data)))

filepath = sys.argv[1]
f = open(filepath, "wb")
f.write(data)
f.close()

