# Polylat reference guide
## Goal
The [polylat.py](../tools/polylat.py) tool allows the developer of a polycube service to monitor which kernel functions his program calls and to get some information about the latency time for each of them. The output of this tool is composed by two parts:

* brief summary containing the amount of calls, the latency and the percentage over total time taken by all the traced functions;
* set of histograms showing the latency distribution for each monitored function in a logarithmic scale.

### Note 
The statistics obtained from this tool are inaccurate, they are useful for monitoring the distribution of values (thanks to the histograms) and the relation between the called functions inside the eBPF program. For having an accurate value of the functions latencies (without the histogram feature), please use the [polylatperc.py](../tools/polylatperc.py) tool.
## Vocabulary
* Analysis context: the set of kernel functions that are being monitored.
* Entry-point: the ingress point of a function, before the first instruction.
* Exit-point: the egress point of a function, after the return statement and before the caller gets the control back.
* kprobe, kretprobe: kernel primitives which allow the developer to attach a tracing function to the entry-point (kprobe) or the exit-point (kretprobe) of a function.
## The algorithm
### 1. Analysis context setting
Whenever this tool starts, it takes an input file which must have the format of the output file produced by polycount.py (please, follow the advice for use section in the [README](../README.md) file); the path to this file can be specified by using the -i option, otherwise it is ``~/PTT/polycube_dump.txt`` by default.
### 2. Polylat launch
When the developer starts the tool, he can do it by passing some optional parameter related to the verbosity of the output, the features of the analysis, the measure unit of the latency, the input file from which to get the functions to monitor, and the output file in which to write the result.
### 3. Startup prints
According to the options specified there are two different kind of prints:
* list of analysis parameters (``if --brief == false``): verbosity, duration, sleep_time, output file;
* list of probed functions (``if --verbose == true``): the entire list of the probed functions.
### 4. Analysis
The tool works in the following manner:
* Creation of the BPF program: the eBPF program is created at runtime, by taking all the functions to monitor and creating a callback for the entry-point of each of them.
* Callbacks hooking: each entry-callback is linked to the entry-point of the function by using the kprobe mechanism (``BPF.attach_kprobe()``) and each exit-callback is linked to the exit-point of the function by using the kretprobe mechanism (``BPF.attach_kretprobe()``).
* Function analysis: at each call of the probed functions, the entry-point callback is triggered before the called function is being executed: it stores the current time of the system in a hashmap and return the control to the probed function. After the probed function has been executed, before it returns the control to its caller, the exit-point callback is triggered and is being executed: it fetches the previously stored time, computes the time spent, increments a counter and stores data on a hashmap.
### 5. Intermediate and final prints
Every sleep_time the tool prints on screen a partial summary of the measurements (``if --brief == false``), which includes, for each function:
* total count;
* total time;
* percentage over the BPF program total time;
* average latency.

It also prints (``if --verbose == true``) the latency distribution for each traced function visualized as a histogram.  
The final print occurs when the developer stops the test (by using ``^C``) or when the internal clock of the tool reaches the duration specified through the ``-d`` option. The final print has got the same format of the intermediate prints, regardless of the ``--verbose`` and ``--brief``options; if specified (``--output``), the final print is dumped on the output file.

