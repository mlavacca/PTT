#!/usr/bin/python

import operator
import argparse
import re
import os
import time
import datetime
from os.path import expanduser
from bcc import BPF

NAME_SIZE = 64
TASK_COMM_LEN = 16

white_list = [
]
black_list = [
]
active_functions = []		# functions selected in the debug subsystem
erased_functions = []		# functions that cannot be probed
found_functions = []		# necessary to avoid multiple probe attaching

# parameters
verbose = False
brief = False
user = expanduser("~")
file_path = user + "/PTT/polycube_dump.txt"
input_file = user + "/PTT/polycount_functions.conf"

# parameterization
parser = argparse.ArgumentParser()

verbosity = parser.add_mutually_exclusive_group()
verbosity.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
verbosity.add_argument("-b", "--brief", help="reduce output verbosity", action="store_true")
parser.add_argument("-o", "--output", help="specify output file path")
parser.add_argument("-i", "--input", help="specify input file")

args = parser.parse_args()

# parameters assignement
if args.verbose:
	verbose = True
if args.brief:
	brief = True
if args.output:
	file_path = args.output
if args.input:
	file_input = args.input

if os.path.isdir(user + "/PTT") is False:
	os.makedirs(user + "/PTT")
if os.path.isfile(input_file) is False:
	print("no configuration file found, a default conf file is going to be created at " + user+"/PTT/polycount_functions.conf\n")
	funcs = ["bpf_ktime_get_ns\n", ".*htab_map.*\n", "\n", "htab_map_delete\n", ".*fd.*\n"]
	try:
		fp = open(input_file, "w")
	except IOError:
		print("Error, cannot create input file")
		exit()
	for func in funcs:
		fp.write(func)
	fp.close()


# dump the events on file
def dump(b, start_time):
	counts = {}
	total_count = 0

	try:
		output_file = open(file_path, "w")
	except IOError:
		print("\nERROR: cannot open " + file_path + "...exit\n")
		exit()	
	
	raw_counts = b.get_table("events")
	for (key, count) in raw_counts.items():
		counts[key.name] = count.value
		total_count += count.value
	sorted_counts = sorted(counts.items(), key=operator.itemgetter(1), reverse=True)
	
	now = datetime.datetime.now()	

	# headers print
	output_file.write("%-28s%18s%38s\n\n" % ("#DATE: " + now.strftime("%Y-%m-%d"), "TIME: " + now.strftime("%H:%M"), "ELAPSED TIME: " + time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time))))
	output_file.write("%-64s%8s%12s\n" % ("#FUNCTION", "COUNT", "%"))
	output_file.write("%-64s%8s%12.3f\n\n" % ("#TOTAL COUNT", str(total_count), float(100)))

	for (key, count) in sorted_counts:
		if len(key) > 63:
			key = key[0-62]
		key += ":"
		output_file.write("%-64s%8s%12.3f\n" % (key, str(count), float(count)/total_count * 100))
	output_file.close()

start_time = time.time()		# for the elapsed time

try:
	fp_input = open(input_file, "r")
except IOError:
	print("\nERROR: cannot open " + input_file + "...exit\n")
	exit()
black = False
func = fp_input.readline()
while func:
	func = func.replace("\n", "")
	if func == "":
		black = True
		func = fp_input.readline()
		continue
	if black is False:
		white_list.append(func)
	else:
		black_list.append(func)
	func = fp_input.readline()


# creation of the regex pattern for filtering the available_filter_functions
pattern = ""
for white_elem in white_list:
	if white_elem != white_list[0]:
		pattern += "|";
	pattern += white_elem
white_pattern = re.compile(pattern)
pattern = ""
for black_elem in black_list:
	if black_elem != black_list[0]:
		pattern += "|";
	pattern += black_elem
black_pattern = re.compile(pattern)

# read all the functions from the available_filter_functions file and filter them according to the filtering pattern
available_filter_functions_file = open("/sys/kernel/debug/tracing/available_filter_functions", "r")
ff = available_filter_functions_file.readline()

while ff:
	ffs = ff.split(" ")
	filter_function = ffs[0].replace("\n", "")
	
	if (white_pattern.match(filter_function) and
		(black_pattern.match(filter_function) is None
		 or pattern == "")):
		if filter_function not in found_functions:
			found_functions.append(filter_function)
			filter_function = filter_function.replace(".", "_")
			active_functions.append(filter_function)
	ff = available_filter_functions_file.readline()


# intro prints
if brief is False:
	print("I'm going to trace all the functions according to the following filter rules...\n")
	print("ADDICTION FILTERS:")
	for elem in white_list:
		print(elem)
	print("\nSUBTRACTION FILTERS:")
	for elem in black_list:
		print(elem)
	print("")

if verbose is True:
	print("These are the functions that are going to be traced:")
	for elem in active_functions:
		print(elem)
	print("")
print("functions tracer starting...please wait\n")

prog = """
	#include <uapi/linux/ptrace.h>
	#include <linux/sched.h>

	#define NAME_SIZE 64
		
	struct data_t{
	char name[NAME_SIZE];
	};

	BPF_HASH(events, struct data_t, u64);
	BPF_HASH(test, u64, u64);
"""

for line in active_functions:
	prog += """
	int PLACEHOLDER_NAME_func(struct pt_regs *ctx) {
		u64 pid_tgid = bpf_get_current_pid_tgid();
		if(FILTER)
			return 0;

		struct data_t data = {};

		char name[64] = "PLACEHOLDER_NAME";
		bpf_probe_read_str(&data.name, sizeof(name), &name);
		test.update(&pid_tgid, &pid_tgid);
		u64 initCtr = 0;
		u64 *countPtr = events.lookup_or_init(&data, &initCtr);

		(*countPtr) += 1;

        return 0;
    	}
"""
	prog = prog.replace("FILTER", "pid_tgid == " + str(os.getpid()))
	prog = prog.replace("PLACEHOLDER_NAME", line)
b = BPF(text=prog)

for func in active_functions:
	try:	
		b.attach_kprobe(event=func, fn_name = func + "_func")			
	except Exception:
		print("cannot trace " + func + " function\n")
		erased_functions.append(func)

# start print
print("++++++++++++++++  OK  ++++++++++++++++++")
print("You are currently tracing the specified functions, please start your program,")
print("then press ^C to stop tracing...\n")

while 1:
	try:
		time.sleep(9999)
	except KeyboardInterrupt:
		print("\n\n+++++++++++++++  STOP  +++++++++++++++++")
		print("Please wait, writing on file " + file_path + " and probes detaching...")
		dump(b, start_time)
		exit()

