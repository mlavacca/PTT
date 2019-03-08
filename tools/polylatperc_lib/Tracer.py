import os
import re
import sys
from ctypes import *
import time
import datetime
import params


class Tracer:

	true_latencies = {}

	def __init__(self, args, parameters):
		if os.path.isfile(parameters.tuning_file) is False:
			print("No tuning file detected, first perform the tuning operation\nClosing...\n")
			exit()
		
		if args.verbose:
			parameters.verbose = True
		if args.brief:
			parameters.brief = True
		if args.sleep:
			parameters.sleep_time = args.sleep
		if args.duration:
			parameters.duration = args.duration
		if args.input:
			parameter.file_path = args.input
		if args.output:
			parameters.output_file_path = args.output
		if args.xdp:
			parameters.xdp = True

		try:
			input_file = open(parameters.file_path, "r")
		except:
			print("error opening %s file" % parameters.file_path)
			exit()

		if parameters.xdp is True:
			parameters.active_functions.append("net_rx_action")
		else:
			parameters.active_functions.append("cls_bpf_classify")

		line = input_file.readline()
		while line:
			if "#" in line or line in ['\n', '\r\n']:
				line = input_file.readline()
				continue
			[event, val] = line.split(":")
			parameters.active_functions.append(event)
			line = input_file.readline()
		input_file.close()
		
		try:
			input_file = open(parameters.tuning_file, "r")
		except:
			print("error opening %s file" % parameters.tuning_file)
			exit()

		line = input_file.readline()
		while line:
			if "#" in line or line in ['\n', '\r\n']:
				line = input_file.readline()
				continue
			[foo, val] = line.split(":")
			self.true_latencies[foo] = int(val)
			line = input_file.readline()
		input_file.close()


	def make_bpf_program(self, parameters):
		i = 0
		for foo in parameters.active_functions:
			parameters.prog += """
			
			int PLACEHOLDER_NAME_start(struct pt_regs *ctx) {
		
				u64 pid = bpf_get_current_pid_tgid();
				u64 ts = bpf_ktime_get_ns();

				tsp_key_t key = {};
				key.index = INDEX;
				key.pid = pid;

				start.update(&key, &ts);		

				return 0;
			}


			int PLACEHOLDER_NAME_end(struct pt_regs *ctx) {
		
				u64 index = INDEX;
				tsp_key_t key = {};

				u64 pid = bpf_get_current_pid_tgid();
			
				key.index = index;
				key.pid = pid;
		
				u64 *tsp = start.lookup(&key);

				if(tsp == 0 || *tsp == 0){
					return 0;
				}

				latency_t lat_init = {};
				lat_init.counter = 0;
				lat_init.total_time = 0;
		
				u64 start_time = bpf_ktime_get_ns();

				latency_t* data_stored = lats.lookup_or_init(&index, &lat_init);

				u64 delta = start_time - *tsp;
				*tsp = 0;

				(*data_stored).counter ++;
				(*data_stored).total_time += delta;
			
				return 0;
			}
			"""

			parameters.prog = parameters.prog.replace("PLACEHOLDER_NAME", foo)
			parameters.prog = parameters.prog.replace("INDEX", str(i))
			i += 1


	def intro_print(self, parameters):
		print("The tracer function has been launched with the following parameters:\n")
		if parameters.xdp is False:
			print("%-40s" % ("Performing BPF analysis"))
		else:
			print("%-40s" % ("Performing XDP analysis"))
		print("%-40s%-s" % ("sleep time:", str(parameters.sleep_time)))
		if parameters.duration == -1:
			print("%-40s%-s" % ("test duration:", "infinite"))
		else:
			print("%-40s%-s" % ("test duration:", str(parameters.duration)))
		if parameters.output_file_path != "":
			print("%-40s%-s" % ("output file", parameters.output_file_path))
	

	def verbose_print(self, parameters):
		print("\nI'm going to trace the following functions:\n")
		for elem in parameters.active_functions:
			if elem not in parameters.erased_functions:
				print(elem)
		print("")


	def start_print(self, parameters):
		print("\n\n+++++++++++++++++++++  OK  ++++++++++++++++++++++++")
		print("You are currently tracing the requested functions, please start your program,")
		if parameters.duration != -1:
			print("then wait " + str(parameters.duration) + " secs or press ^C to stop tracing...\n")
		else:
			print("then press ^C to stop tracing...\n")


	
	def print_summary(self, parameters, lats):
		summary = {}
		summary_perc = {}
		for k, v in lats.items():
			name = parameters.active_functions[c_long(k.value).value]
			summary[name] = [v.counter, v.total_time, 100, v.total_time / v.counter]	
		try:
			if "cls_bpf_classify" in summary.keys():
				total_prog_time = summary["cls_bpf_classify"][1]
			else:
				total_prog_time = summary["net_rx_action"][1]
			for k in summary.keys():
				summary[k][2] = float(summary[k][1]) / float(total_prog_time) * 100
				summary_perc[k] = summary[k][2]

			summary_perc = sorted(summary_perc.items(), key=lambda (k,v): (v,k), reverse=True)

			(tmpkey, tmpval) = summary_perc[0]
			summary_perc[0] = ("BPF PROGRAM", tmpval)
			summary["BPF PROGRAM"] = summary[tmpkey]
			summary.pop(tmpkey)
			summary = self.factor_values(summary)
		except:
			raise
			pass

		print("\n\n++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  BEGIN SUMMARY  ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
		print("%-40s%15s%28s%25s%25s\n" % ("#FUNCTION", "COUNT", "TOT TIME SPENT (nsecs)", "% OVER TOTAL TIME", "LATENCY AVG (nsecs)"))
		for k, v in summary_perc:
			print("%-40s%15d%28d%15.2f%25d" % (k, summary[k][0], summary[k][1], summary[k][2], summary[k][3]))
			if k == "BPF PROGRAM":
				print("")
		print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  END SUMMARY  ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
	

	def forever_loop(self, parameters, lats, start_time):
		while(1):
			if parameters.duration - parameters.sleep_time <= 1 and parameters.duration != -1:
				try:
					time.sleep(parameters.duration)
					break
				except KeyboardInterrupt:
					break
			else:
				try:
					time.sleep(parameters.sleep_time)
				except KeyboardInterrupt:
					break
				if parameters.duration != -1:
					parameters.duration -= parameters.sleep_time
				if parameters.brief is not True:
					self.print_summary(parameters, lats)

		self.final_print(parameters, start_time, lats)
		print("\n\n++++++++++++++++++++  END  ++++++++++++++++++++++++")


	def factor_values(self, summary):

		MUA = summary["htab_map_update_elem"][3]
		MLA = summary["__htab_map_lookup_elem"][3]
		KTA = summary["bpf_ktime_get_ns"][3]

		MUTA = self.true_latencies["MUTA"]
		MLTA = self.true_latencies["MLTA"]
		KTTA = self.true_latencies["KTTA"]

		for k in summary.keys():
			if k == "htab_map_update_elem":
				summary[k][3] = MUTA
				summary[k][1] = summary[k][0]*MUTA
			if k == "__htab_map_lookup_elem":
				summary[k][3] = MLTA
				summary[k][1] = summary[k][0]*MLTA
			if k == "bpf_ktime_get_ns":
				summary[k][3] = KTTA
				summary[k][1] = summary[k][0]*KTTA

		PID_overhead = (MUTA + MLTA + KTTA)/3.6

		single_overhead = MUA - MUTA
		total_overhead = 0

		nProbes = len(summary)
		total_overhead  += (single_overhead + MLTA + 2*PID_overhead) * (nProbes-1)
		total_overhead += 2*KTTA + MUTA + MLTA	
	
		for k in summary.keys():
			if k not in ("BPF PROGRAM", "htab_map_update_elem", "__htab_map_lookup_elem", "bpf_ktime_get_ns"):
				summary[k][3] -= (MUTA + MLTA + 2*KTTA)
				summary[k][1] = summary[k][0]*summary[k][3]
				if summary[k][1] < 0:
					summary[k][1] = 0
				if summary[k][2] < 0:
					summary[k][2] = 0
				if summary[k][3] < 0:
					summary[k][3] = 0
		
		summary["BPF PROGRAM"][3] -= total_overhead
		summary["BPF PROGRAM"][1] = summary["BPF PROGRAM"][3]*summary["BPF PROGRAM"][0]
		
	
		for k in summary.keys():
			if k != "BPF PROGRAM":
				summary[k][2] = float(summary[k][1]) / float(summary["BPF PROGRAM"][1]) * 100.0
			
		return summary


	# it prints both on screen and file by using output redirection and calling print_summary
	def final_print(self, parameters, start_time, lats):
		print("\n\n++++++++++++++++++++  STOP  +++++++++++++++++++++++")
		print("Test terminated, final stats computing...")	
		now = datetime.datetime.now()
		if(parameters.output_file_path != ""):
			try:		
				output_file = open(parameters.output_file_path, "w")		
			except IOError:
				print("ERROR, cannot create " + parameters.output_file_path + "...exit")
				exit()
			output_file.write("%-25s%18s%35s" % (
							"#DATE: " + now.strftime("%Y-%m-%d"), 
							"TIME: " + now.strftime("%H:%M"), 
							"ELAPSED TIME: " + time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time))))
			stdout_backup = sys.stdout
			sys.stdout = output_file
			self.print_summary(parameters, lats)
			output_file.close()
			sys.stdout = stdout_backup

		print("\n\n%-25s%18s%35s" % (
					"#DATE: " + now.strftime("%Y-%m-%d"), 
					"TIME: " + now.strftime("%H:%M"), 
					"ELAPSED TIME: " + time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time))))
		self.print_summary(parameters, lats)
		






