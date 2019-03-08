import os
from sys import stdout
from params import *
import params
import time
import datetime
from ctypes import *

class Tuner:

	active_functions = [	# functions selected in the debug subsystem
		"bpf_ktime_get_ns",
		"cls_bpf_classify",
		"__htab_map_lookup_elem",
		"htab_map_update_elem"
	]


	def __init__(self, args, parameters):
		if os.path.isdir(parameters.config_path) is False:
			os.makedirs(parameters.config_path)

		parameters.active_functions = self.active_functions
		parameters.brief = args.brief
		parameters.verbose = args.verbose


	def make_bpf_program(self, parameters):
		i = 0
		for foo in self.active_functions:
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
		print("The tuner is going to measure the real latency of the following functions:\n")
		print("bpf_ktime_get_ns")
		print("htab_map_update_elem")
		print("__htab_map_update_elem")


	def verbose_print(self, parameters):
		#definire le stampe verbose di Tuner
		pass

	
	def start_print(self, parameters):
		print("\nThe tuner is ready to start...")
		raw_input("Please launch the simple bridge in polycube and make it work, then press any key to start tuning")
		print("\n\n+++++++++++++++++++  START  ++++++++++++++++++++++\n")

	def forever_loop(self, parameters, lats, start_time):
		for i in range(10, -1, -1):
			stdout.write("\rPlease wait:\t%2d" % i)
			stdout.flush()
			time.sleep(1)
		stdout.write("\n")

		self.print_summary(lats, parameters, start_time)
		print("\n++++++++++++++++++++  END  +++++++++++++++++++++++\n\n")
		if parameters.verbose is True:
			print("Computed latencies:\n")

	def print_summary(self, lats, parameters, start_time):
		summary = {}
		summary_perc = {}
		for k, v in lats.items():
			name = parameters.active_functions[c_long(k.value).value]
			summary[name] = [v.counter, v.total_time, 100, v.total_time / v.counter]	
		try:
			total_prog_time = summary["cls_bpf_classify"][1]
			for k in summary.keys():
				summary[k][2] = float(summary[k][1]) / float(total_prog_time) * 100
				summary_perc[k] = summary[k][2]

			summary_perc = sorted(summary_perc.items(), key=lambda (k,v): (v,k), reverse=True)
			(tmpkey, tmpval) = summary_perc[0]
			summary_perc[0] = ("BPF PROGRAM", tmpval)
			summary["BPF PROGRAM"] = summary[tmpkey]
			summary.pop(tmpkey)
			latencies = self.compute_latencies(summary)
			try:
				output_file = open(parameters.tuning_file, "w")
			
			except IOError:
				print("ERROR, cannot create " + parameters.tuning_file + "...exit")
				exit()
			now = datetime.datetime.now()
			output_file.write("%-25s%18s%35s\n\n" % (
					"#DATE: " + now.strftime("%Y-%m-%d"), 
					"TIME: " + now.strftime("%H:%M"), 
					"ELAPSED TIME: " + time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time))))
			output_file.write("MUTA:\t%d\n" % latencies[0])
			output_file.write("MLTA:\t%d\n" % latencies[1])
			output_file.write("KTTA:\t%d\n" % latencies[2])

			print("Latency values printed in %s" % parameters.tuning_file)
			output_file.close()
		except:
			print("Print on file failed")
			pass
	

	def compute_latencies(self, summary):

		MUA = summary["htab_map_update_elem"][3]
		MLA = summary["__htab_map_lookup_elem"][3]
		KTA = summary["bpf_ktime_get_ns"][3]

		for k in summary.keys():
			if k == "htab_map_update_elem":
				MUTA = (4*MUA-MLA-2*KTA)/5
				summary[k][3] = MUTA
				summary[k][1] = summary[k][0]*MUTA
			if k == "__htab_map_lookup_elem":
				MLTA = (-MUA+4*MLA-2*KTA)/5
				summary[k][3] = MLTA
				summary[k][1] = summary[k][0]*MLTA
			if k == "bpf_ktime_get_ns":
				KTTA = (-MUA-MLA+3*KTA)/5
				summary[k][3] = KTTA
				summary[k][1] = summary[k][0]*KTTA
			
		return [MUTA, MLTA, KTTA]





