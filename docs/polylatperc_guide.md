# Polylatperc reference guide
## Goal

The [polylatperc.py](../tools/polylatperc.py) tool allows the developer of a polycube service to monitor which kernel functions his program calls and the amount for each of them; in addition to this, it allows to know the total time spent by each kernel function, the average latency and the spent percentage over the total time of the eBPF program that is being monitored. All the latencies computed by this tool are very accurate, thanks to the two phases analysis (tuning and tracing) that allows to cancel the overhead intrinsic in the tracing operations.

## Note

There are two different working modes: *eBPF* (by default) and *XDP* (--xdp option). The kernel function which is considered as the BPF program is the ``cls_bpf_classify`` (for the eBPF working mode) or ``net_rx_action`` (for XDP working mode), therefore it is recommended to use this tool only to trace functions which are called inside them (by not doing it the result can be meaningless and impredictible). The tool functionality is splitted into two different phases: *tuning* and *tracing* (see later).

## Vocabulary
* Analysis context: the set of kernel functions that are being monitored.
* Entry-point: the ingress point of a function, before the first instruction.
* Exit-point: the egress point of a function, after the return statement and before the caller gets the control back.
* kprobe, kretprobe: kernel primitives which allow the developer to attach a tracing function to the entry-point (kprobe) or the exit-point (kretprobe) of a function.
## The algorithm
### 1. Creation of the analysis context
In order to set the analysis context, the developer has to specify an input file from which to take the functions to trace: by default it is the ``~/PTT/polycube_dump.txt `` file (created by the first tool) but can also be specified by using the ``-i`` option.

### 2. Polylatperc launch
This tool is intended to be used in a two steps manner:

1.  ``polylatperc.py tune``: the tool asks the developer to launch a simplebridge service in polycube and to make it work by using some traffic generator (e.g., iperf3); the true latency of the three main functions used by the tool are computed and used later for ensuring a very accurate measure of the functions latency. The computed latencies are stored in ~/.config/PTT/tuning.conf
2. ``polylatperc.py trace``: the tool gets the latency values previously computed (in the tune phase) and uses them to calculate the latency of any function the developer wants to trace.

### 3. Startup prints

* tuning phase:
  * list of tuned functions (``if --brief == false``);
  * list of computed latencies (``if --verbose == true``).
* tracing phase
  * list of analysis parameters (``if --brief == false``): verbosity, duration, sleep\_time, output file;
  * list of probed functions (``if --verbose == true``): the entire list of the probed functions.
### 4. Analysis
The tool in the trace phase works in the following manner:
* Creation of the BPF program: the eBPF program is created at runtime, by taking all the functions to monitor and creating a callback for the entry-point and a callback for the exit-point of each of them.
* Callbacks hooking: each entry-callback is linked to the entry-point of the function by using the kprobe mechanism (``BPF.attach_kprobe()``) and each exit-callback is linked to the exit-point of the function by using the kretprobe mechanism (``BPF.attach_kretprobe()``).
* Function analysis: at each call of the probed functions, the entry-point callback is triggered before the called function is being executed: it stores the current time of the system in a hashmap and return the control to the probed function. After the probed function has been executed, before it returns the control to its caller, the exit-point callback is triggered and is being executed: it fetches the previously stored time, computes the time spent, increments a counter and stores data on a hashmap.
* In order to have accurate measurements, the result of this analysisi must be manipulated accordingly to the data computed in the tune phase; this manipulation is described later, in the optimization algorithm section.
### 5. Intermediate and final prints
Every *sleep\_time* the tool prints on screen a partial summary of the measurements, which includes, for each function:
* total count;
* total time;
* percentage over the BPF program total time;
* average latency.  

The final print occurs when the developer stops the test (by using ``^C``) or when the internal clock of the tool reaches the duration specified through the ``-d`` option. The final print has got the same format of the intermediate prints.
## The optimization algorithm
This algorithm is used in the tune phase to calculate the exact latency of the functions used by the tool; without this shrewdness the result of the trace phase can be very inaccurate.
### Problem
By having the total count and the total time of every function it is possible to trivially calculate the average time for each of them:

![alt text](http://mathurl.com/yalush2l.png "Latency average")  

Nevertheless by looking the code in depth it is possible to see that every time a function tracer is being called (e.g., the callback that traces ``bpf_ktime_get_ns()``), a set of function is being called for measuring the latency time and for incrementing the counter related to the traced function. In particular, for every traced function call, the measured latency time is affected by 2 ``bpf_ktime_get_ns()``, a ``htab_map_update_elem()`` and 2 ``htab_map_lookup_elem()``. As a conseguence of this there is a not negligible overhead carried by the tracing functions (e.g., by supposing that all the functions have the same latency time, by tracing a ``bpf_ktime_get_ns()`` an overhead of 4 times the true time affects the measure).

### Thesis
In order to solve this problem and to perform a reliable and accurate tracing it is possible to solve a mathematical problem which leans over a system of 3 linear equations in 3 variables (i.e., the problem leads to a unique real solution).

### Constraints
The thesis relies on 3 different assumptions:
* the traced functions **must** perform operations of ``bpf_ktime_get_ns()``, ``htab_map_update_elem()``, and ``htab_map_lookup_elem()``;
* the traced functions must use the hashmaps in order to access and store data; in order to avoid this constraint, a different version of this tool which uses ``array_map`` for tracing the programs that use ``array_map`` for storing data can be developed.
* by having the hashmaps in which data are stored, the computational cost of access and storage on them by the tracing function and the traced functions is being considered equivalent: this is true whether the maps (networking and tracing) are similar to each other in terms of load factor.

If these constraints are satisfied, this tracing tool gives the developer of a polycube service a latency time and a percentage over the total time taken by his networking program which are very accurate, by eliminating all the overhead from the measure.

### Solution
1. The analysis of the tracing code leads to this system of equations:  

	![alt text](http://mathurl.com/y9tj2s55.png "equations system")  

	where:  
	* ![alt text](http://mathurl.com/yat7f5m9.png "Latency true def") is the true latency of the function func (MU = map_update, ML = map_lookup, KT = ktime_get_ns);  
	* ![alt text](http://mathurl.com/y8bcoxnj.png "Latency def") is the measured latency of the function func;  
	* *X* is the overhead carried by the tracing function.
	
2. As previously explained the overhead *X* for each tracing function is composed by:  
![alt text](http://mathurl.com/yaejytqu.png "X")

3. By substituting the X, grouping all the variables and putting them in a matrix form:

	![alt text](http://mathurl.com/y8q657xd.png "substituted")

	![alt text](http://mathurl.com/y95n2drz.png "substitued2")
	
	![alt text](http://mathurl.com/ybpnw7s3.png "matrix form")

4. The system's solution is:

	![alt text](http://mathurl.com/ycnenxeb.png "solution")  
	which means that each one of the 3 functions used in the tracing functions depends on the real measurements. Thanks to this it is possible to know which is the true latency of these 3 main functions.

5. The whole eBPF program's latency is defined as follow:  

	![alt text](http://mathurl.com/yasy6naj.png "BPFtot")  
where:
	* ![alt text](http://mathurl.com/ybr3tfcx.png "BPFtot") is the true latency of the whole eBPF program;
	* ![alt text](http://mathurl.com/yc3xt6sj.png "BPFtot") is the measured latency of the eBPF program;
	* *Y* is the total overhead of the eBPF program.
6. The total overhead which affects every eBPF program (as it is possible to see in the code) is composed by K times (X +  1``htab_map_lookup_elem()`` (latency necessary to each tracing function for fetching the struct containing counter and total time from the hash map)), where K is the number of tracing functions which operate inside the eBPF program.

	![alt text](http://mathurl.com/ya89y5ze.png "Y")
	
7. Therefore the true eBPF latency time is computed as follows:

	![alt text](http://mathurl.com/y9umb6kv.png "LBPFT")

8. Since the tracing tools must use the ``bpf_get_current_pid_tgid()`` function for working, a factor experimentally obtained is used to get a ``cls_bpf_classify()`` latency as accurate as possible: it is  named as ``pid_overhead`` in the code.
### Footnote
 By uncoupling the tune phase from the trace phase, it is possible to measure in a very accurate manner every function the eBPF program calls. 
