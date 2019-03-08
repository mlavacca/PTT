#!/usr/bin/python

import sys
import os
import argparse
import time
import math
from os.path import expanduser
from bcc import BPF

sys.path.insert(0, 'polylatperc_lib')
from Tracer import Tracer as trace_func
from Tuner import Tuner as tune_func
from params import Parameters

NAME_SIZE = 64
TASK_COMM_LEN = 16

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()
tune = subparsers.add_parser("tune", help="tuning functionality")
tune.set_defaults(func=tune_func)
trace = subparsers.add_parser("trace", help="tracing functionality")
trace.set_defaults(func=trace_func)

verbosity = trace.add_mutually_exclusive_group()
verbosity.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
verbosity.add_argument("-b", "--brief", help="reduce output verbosity", action="store_true")

verbosity2 = tune.add_mutually_exclusive_group()
verbosity2.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
verbosity2.add_argument("-b", "--brief", help="reduce output verbosity", action="store_true")

trace.add_argument("-x", "--xdp", help="execute xdp tracing", action="store_true")
trace.add_argument("-s", "--sleep", type=int, help="time interval (in secs) between the intermediate prints")
trace.add_argument("-d", "--duration", type=int, help="duration of the test (in secs)")
trace.add_argument("-i", "--input", help="input file path")
trace.add_argument("-o", "--output", help="output file path")

args = parser.parse_args()

parameters = Parameters()
element = args.func(args, parameters)

start_time = time.time() # for the elapsed time

if parameters.brief is not True:
	element.intro_print(parameters)
	
if parameters.verbose is True:
	element.verbose_print(parameters)

element.make_bpf_program(parameters)	

b = BPF(text = parameters.prog)

for f in parameters.active_functions:
	try:		
		b.attach_kprobe(event = f, fn_name = f + "_start")
		b.attach_kretprobe(event = f, fn_name = f + "_end")
	except Exception:
		print("cannot trace " + f + " function\n")
		parameters.erased_functions.append(f)

lats = b.get_table("lats")

element.start_print(parameters)

element.forever_loop(parameters, lats, start_time)

print("Please wait, probes detaching...")
		
exit()
	




