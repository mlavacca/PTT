from os.path import expanduser

class Parameters:

	verbose = False
	brief = False
	sleep_time = 5
	duration = -1
	file_path = expanduser("~") + "/PTT/polycube_dump.txt"
	config_path = expanduser("~") + "/.config/PTT"
	tuning_file = config_path + "/tuning.conf"
	output_file_path = ""
	xdp = False

	active_functions = []
	erased_functions = []	# functions that cannot be probed
	found_functions = []	# necessary to avoid multiple probe attaching

	prog = """
		#include <uapi/linux/ptrace.h>

		#define NAME_SIZE 64	

		typedef struct latency {
			u64 counter;
			u64 total_time;	
		} latency_t;

		typedef struct tsp_key {
			u64 pid;
			u64 index;
		} tsp_key_t;

		BPF_HASH(start, tsp_key_t, u64);
		BPF_HASH(lats, u64, latency_t);
	"""
