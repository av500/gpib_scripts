#! /usr/bin/env python3.10
import pyvisa as visa
import sys

if len(sys.argv) < 2 :
	print("usage: hp2225  filename")
	exit();

filepath = sys.argv[1]
f = open(filepath, newline="\r\n")
txt = f.read()
f.close()

rm = visa.ResourceManager('@py')
instr = rm.open_resource('GPIB0::1::INSTR')
instr.timeout = 50;

txt_norm = "&k0S"
txt_ec   = "&k3S"
bold_on  = ""
bold_off = ""

instr.write(txt_norm)
instr.write(bold_on)

txt = txt.splitlines()
for line in txt:
    instr.write(line)

