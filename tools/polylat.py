#!/usr/bin/python

import sys
import re
import os
import argparse
import time
import math
import datetime
import ctypes as ct
from os.path import expanduser
from bcc import BPF

NAME_SIZE = 64
TASK_COMM_LEN = 16

# params
verbose = False		# If true it shows total stats each sleep_time
			# and shows the list of the traced functions at the startup
brief = False		# If true it doesn't show the resume of the parameters at the startup
			# and doesn't show intermediate summaries each sleep_time 
measure_unit = "nsecs"
limit = 0
sleep_time = 5
duration = -1
file_path = expanduser("~") + "/PTT/polycube_dump.txt"
output_file_path = ""

# options description
parser = argparse.ArgumentParser()

verbosity = parser.add_mutually_exclusive_group()
verbosity.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
verbosity.add_argument("-b", "--brief", help="reduce output verbosity", action="store_true")

measure = parser.add_mutually_exclusive_group()
measure.add_argument("-m", "--msecs", help="use milliseconds as measure unit", action="store_true")
measure.add_argument("-u", "--usecs", help="use microseconds as measure unit", action="store_true")
measure.add_argument("-n", "--nsecs", help="use nanoseconds as measure unit", action="store_true")

parser.add_argument("-l", "--limit", type=int, help="count value from which to start tracing")
parser.add_argument("-s", "--sleep", type=int, help="time interval (in secs) between the intermediate prints")
parser.add_argument("-d", "--duration", type=int, help="duration of the test (in secs)")
parser.add_argument("-i", "--input", help="specify input file path")
parser.add_argument("-o", "--output", help="specify output file path")

args = parser.parse_args()

# parameters assignement
if args.verbose:
	verbose = True
if args.brief:
	brief = True
if args.msecs:
	measure_unit = "msecs"
if args.usecs:
	measure_unit = "usecs"
if args.nsecs:
	measure_unit = "nsecs"
if args.limit:
	limit = args.limit
if args.sleep:
	sleep_time = args.sleep
if args.duration:
	duration = args.duration
if args.input:
	file_path = args.input
if args.output:
	output_file_path = args.output

# summary print
def print_summary(dist):
	summary = {}
	total_time = 0
	for k, v in dist.items():
		if k.name not in summary.keys():
			summary[k.name] = [{k.slot: v.value}]
			summary[k.name].append(v.value)
			t = v.value*((math.pow(2, k.slot)-1 + math.pow(2, k.slot-1))/2)
			summary[k.name].append(t)
			total_time += t
		else:
			summary[k.name][0][k.slot] = v.value
			summary[k.name][1] += v.value
			t = v.value*((math.pow(2, k.slot)-1 + math.pow(2, k.slot-1))/2)
			summary[k.name][2] += t
			total_time += t
	for k in summary.keys():
		summary[k].append(summary[k][2]/total_time*100)
		summary[k].append(summary[k][2]/summary[k][1])
	pos = []
	perc_max = 0
	k_max = ""
	i = 0
	while i < len(summary.keys()):
		for k in summary.keys():
			if k not in pos and summary[k][3] > perc_max:
				perc_max = summary[k][3]
				k_max = k
		pos.append(k_max)
		perc_max = 0
		i+=1		
	print("\n\n++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  BEGIN SUMMARY  ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
	print("%-40s%15s%28s%25s%25s" % ("#FUNCTION", "COUNT", "TOT TIME SPENT (" + measure_unit + ")", "% OVER TOTAL TIME", "LATENCY AVG (" + measure_unit + ")"))
	for k in pos:
		print("%-40s%15d%28.3f%15.3f%25.3f" % (k, summary[k][1], summary[k][2], summary[k][3], summary[k][4]))
	print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  END SUMMARY  ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

# histogram print
def print_total(dist):
	dist.print_log2_hist(measure_unit, "event")

def final_print(start_time, dist):
	print("\n\n++++++++++++++++++++  STOP  +++++++++++++++++++++++")
	print("Test terminated, final stats computing...")	
	now = datetime.datetime.now()
	if(output_file_path != ""):
		try:		
			output_file = open(output_file_path, "w")
			
		except IOError:
			print("ERROR, cannot create " + output_file_path + "...exit")
			exit()
		output_file.write("%-25s%18s%35s" % (
							"#DATE: " + now.strftime("%Y-%m-%d"), 
							"TIME: " + now.strftime("%H:%M"), 
							"ELAPSED TIME: " + time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time))))
		stdout_backup = sys.stdout
		sys.stdout = output_file
		print_summary(dist)
		print_total(dist)
		output_file.close()
		sys.stdout = stdout_backup
	print("\n\n%-25s%18s%35s" % (
					"#DATE: " + now.strftime("%Y-%m-%d"), 
					"TIME: " + now.strftime("%H:%M"), 
					"ELAPSED TIME: " + time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time))))
	print_summary(dist)
	print_total(dist)


active_functions = []	# functions selected in the debug subsystem
erased_functions = []	# functions that cannot be probed
found_functions = []	# necessary to avoid multiple probe attaching

start_time = time.time() # for the elapsed time

prog = """
	#include <uapi/linux/ptrace.h>

	#define NAME_SIZE 64

	typedef struct data {
		char name[NAME_SIZE];
		u64 slot;
	} data_t;

	BPF_HASH(start, u64);
	BPF_HISTOGRAM(dist, data_t);
"""

try:
	input_file = open(file_path, "r")
except IOError:
	print("Input file not found...exit")
	exit()

# intro prints
if brief is not True:
	print("The function tracer has been launched with the following parameters:\n")
	print("%-40s%-s" % ("measure unit:", measure_unit))
	print("%-40s%-s" % ("occurrency limit:", str(limit)))
	print("%-40s%-s" % ("sleep time:", str(sleep_time)))
	if duration == -1:
		print("%-40s%-s" % ("test duration:", "infinite"))
	else:
		print("%-40s%-s" % ("test duration:", str(duration)))
	if output_file_path != "":
		print("%-40s%-s" % ("output file", output_file_path))

active_functions = []	
	
line = input_file.readline()
while line:
	if "#" in line or line in ['\n', '\r\n']:
		line = input_file.readline()
		continue
	[event, val] = line.split(":")
	count = re.split(" +", val)
	if int(count[1]) < limit:
		line = input_file.readline()
		continue
	active_functions.append(event)
	prog += """
	int PLACEHOLDER_NAME_start(struct pt_regs *ctx) {
		u64 ts = bpf_ktime_get_ns();
		u64 pid = bpf_get_current_pid_tgid();
		start.update(&pid, &ts);
		return 0;
	}

	int PLACEHOLDER_NAME_end(struct pt_regs *ctx) {
		u64 pid = bpf_get_current_pid_tgid();
		u64 *tsp = start.lookup(&pid);

		if (tsp == 0)
			return 0;
		u64 delta = bpf_ktime_get_ns() - *tsp;

		FACTOR
		start.delete(&pid);
		data_t data = {};
        	char name[] = "PLACEHOLDER_NAME";
        	bpf_probe_read_str(&data.name, NAME_SIZE, &name);
		data.slot = bpf_log2l(delta);
		dist.increment(data);

		return 0;
	}
	"""
	prog = prog.replace("PLACEHOLDER_NAME", event)
	if measure_unit == "nsecs":
		prog = prog.replace("FACTOR", "")
	if measure_unit == "msecs":
		prog = prog.replace("FACTOR", "delta = delta / 1000000;")
	if measure_unit == "usecs":
		prog = prog.replace("FACTOR", "delta = delta / 1000;")
	line = input_file.readline()
input_file.close()

# verbose print
if verbose is True:
	print("\nI'm going to trace the following functions:\n")
	for elem in active_functions:
		if elem not in erased_functions:
			print(elem)
	print("")
print("\nFunctions tracer starting...please wait")

b = BPF(text = prog)

# start print
print("\n\n+++++++++++++++++++++  OK  ++++++++++++++++++++++++")
print("You are currently tracing the requested functions, please start your program,")
if duration != -1:
	print("then wait " + str(duration) + " secs or press ^C to stop tracing...\n")
else:
	print("then press ^C to stop tracing...\n")

for f in active_functions:
	try:		
		b.attach_kprobe(event = f, fn_name = f + "_start")
		b.attach_kretprobe(event = f, fn_name = f + "_end")
	except Exception:
		print("cannot trace " + f + " function\n")
		erased_functions.append(f)

dist = b.get_table("dist")

while(1):
	if duration - sleep_time <= 1 and duration != -1:
		try:
			time.sleep(duration)
			break
		except KeyboardInterrupt:
			break
	else:
		try:
			time.sleep(sleep_time)
		except KeyboardInterrupt:
			break
	if duration != -1:
		duration -= sleep_time
	if brief is not True:
		print_summary(dist)
	if verbose is True:
		print_total(dist)

final_print(start_time, dist)
dist.clear()

print("\n\n++++++++++++++++++++  END  ++++++++++++++++++++++++")
print("Please wait, probes detaching...")
	
exit()
	




