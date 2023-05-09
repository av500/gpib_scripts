#! /usr/bin/env python3.10
import pyvisa as visa
import sys
from pyvisa import constants

def print_hex(data):
	hex_str = ":".join("{:02x}".format(c) for c in data)
	print(hex_str + " | " + str(data) )

if len(sys.argv) < 2 :
	print("usage: hardcopy_FSEx filename.png")
	exit();

rm = visa.ResourceManager('@py')

instr = rm.open_resource("ASRL/dev/ttyUSB0::INSTR") 

instr.baud_rate = 19200
instr.set_visa_attribute(constants.VI_ATTR_ASRL_FLOW_CNTRL, constants.VI_ASRL_FLOW_XON_XOFF)
instr.stop_bits = constants.StopBits.one
instr.parity = constants.Parity.none
instr.data_bits = 8
instr.read_termination  = '\r'
instr.write_termination = '\r'

# starting the hardcopy takes some time...
instr.timeout = 5000

print(instr.query("*IDN?"))

# for some reason this does not work!!
#instr.write(":HCOP:DEST1 'SYST:COMM:SER1'")
#instr.write(":HCOP:DEV:LANG1 'HPGL_LS'")

print(instr.query(":HCOP:DEST1?"))
print(instr.query(":HCOP:DEV:LANG1?"))

#exit()

filepath = sys.argv[1]
f = open(filepath, "wb")

instr.write(":HCOPY:IMM")

instr.read_termination = None
instr.end_input = False

while 1:
	try:
		data = instr.read_bytes(1)
	except:
		break;
	else:
		if data == b'\r' :
			continue
		f.write(data)
		size = f.tell()
		if  size > 1 :
			instr.timeout = 1000
		if (size % 256) == 0 :
			print(size)
		
print("TOTAL SIZE: " + str(f.tell()))

f.close()

