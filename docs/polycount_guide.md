# Polycount reference guide
## Goal
The [polycount.py](../tools/polycount.py) tool allows the developer of a polycube service to monitor which kernel functions his program calls and the amount of calls for each of them.
## Vocabulary
* Analysis context: the set of kernel functions that are being monitored.

## The algorithm
### 1. Selection of kernel functions
In order to tell the tool which kernel functions to monitor there are two different data structures to customize:
* **whitelist**: by modifying this list according to the python regex syntax it is possible to tell the program whether to add a single function or a set of them to the analysis context;
*  **blacklist**: by modifying this list according to the python regex syntax it is possible to tell the program whether to remove a single function or a set of them from the analysis context.

For customizing these two data structures it is necessary to give the tool an input file (by using the -i option) which must contain all the whitelisted functions, a blank row and then all the blacklisted functions.
If no file is provided by the user, the tool creates the default configuration file ``~/PTT/polycount_functions.conf`` which contains some regular expressions to monitor both for white and blacklist; this file can be modified according to the user preferences.

It is worth to notice that the function which computes the regex is the [match](https://docs.python.org/2.0/lib/matching-searching.html) function, therefore it must be formulated accordingly.
### 2. Polycount launch
After the developer has set the analysis context he can launch the tool by giving some optional parameters related to the verbosity of the output and the output file in which to write the result.
### 3. Startup prints
According to the options specified there are two different kind of prints:
* addiction and subtraction filters (``if --brief == false``): the whitelist and the blacklist;
* list of probed functions (``if --verbose == true``): the entire list of the probed functions.

### 4. Analysis
The tool works in the following manner:
1. Creation of the BPF program: the eBPF program is created at runtime, by taking all the functions to monitor and creating a callback for the entry point of each of them.
2. Callbacks hooking: each callback is linked to the entry point of the function by using the kprobe mechanism through the ``BPF.attach_kprobe()``.
4. Function counting: at each call of the probed functions the BPF callback increments the counter related to that function.

### 5. File dumping
After the tool started it goes to sleep forever and must be stopped by using ``^C``. Whenever the tool is stopped the python program analyzes the BPF hashmap, computes the percentage of calls for each functions (in relationship to the total), and dumps the stats on a file (``~/PTT/polycube_dump.txt`` by default, otherwise specified through the ``-o`` option).
