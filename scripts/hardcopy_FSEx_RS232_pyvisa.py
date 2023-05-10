#! /usr/bin/env python3.10
import pyvisa as visa
import sys
from pyvisa import constants
import os
from datetime import datetime

def print_hex(data):
	hex_str = ":".join("{:02x}".format(c) for c in data)
	print(hex_str + " | " + str(data) )

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

tmp_path = "__temp.hpgl"

cmd = "which hpgs >/dev/null 2>&1"
res = os.system(cmd)

if res :
	print("'hpgs' not found, creating HPGL file")
	has_hpgs = 0
else :
	print("'hpgs' found, creating PNG file")
	has_hpgs = 1
	
if len(sys.argv) < 2 :
	now = datetime.now()
	if has_hpgs :
		filepath = now.strftime("FSEx_%Y%m%d_%H%M%S.png")
	else :
		filepath = now.strftime("FSEx_%Y%m%d_%H%M%S.hpgl")
else :
	filepath = sys.argv[1]
	
print("[file] " + filepath)	

f = open(tmp_path, "wb")

# force pen colors to match FSEB screen colors
f.write(b'PC 1, 128, 128, 128\n');
f.write(b'PC 2, 255, 255,   0\n');
f.write(b'PC 3,   0, 255,   0\n');
f.write(b'PC 5,   0, 255,   0\n');
f.write(b'PC 6,   0,   0, 255\n');

instr.write(":HCOPY:IMM")

instr.read_termination = None
instr.end_input = False

size = 0

while 1:
	try:
		data = instr.read_bytes(1)
	except:
		break;
	else:
		if data == b'\r' :
			continue
		f.write(data)
		size = size + 1
		if  size > 1 :
			instr.timeout = 1000
		if (size % 16) == 0 :
			print("bytes read: "+ str(size), end='\r')
		
print("TOTAL SIZE: " + str(size))

f.close()

if has_hpgs :
	cmd = "hpgs -r 150 -w 0.2  --no-linetype --darkmode --paper=A4l -d png_256 -o {0} {1}".format(filepath, tmp_path)
	print(cmd)
	os.system(cmd)
	cmd = "rm {0}".format(tmp_path)
	os.system(cmd)
else :
	cmd = "mv {0} {1}".format(tmp_path, filepath)
	print(cmd)
	os.system(cmd)

exit()

