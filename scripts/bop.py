#! /usr/bin/env python3.10
import pyvisa as visa

rm = visa.ResourceManager('@py')
lib = rm.visalib

b = rm.open_resource('GPIB0::INTFC')
lib.gpib_control_ren(b.session, visa.constants.VI_GPIB_REN_ASSERT)
b.close()
    
instr = rm.open_resource('GPIB0::30::INSTR')

instr.timeout = 50;

instr.write("050099")

