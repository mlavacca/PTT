
# Demonstration of polylat

It prints on the screen (or dumps on file) file the monitored functions,
the amount of calls for each of them, statistics about the latency time
and the distribution of latencies as a histogram.

---

``$ ./polylat.py --help``
<pre>
usage: polylat.py [-h] [-v | -b] [-m | -u | -n] [-l LIMIT] [-s SLEEP]
                  [-d DURATION] [-i INPUT] [-o OUTPUT]

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         increase output verbosity
  -b, --brief           reduce output verbosity
  -m, --msecs           use milliseconds as measure unit
  -u, --usecs           use microseconds as measure unit
  -n, --nsecs           use nanoseconds as measure unit
  -l LIMIT, --limit LIMIT
                        count value from which to start tracing
  -s SLEEP, --sleep SLEEP
                        time interval (in secs) between the intermediate
                        prints
  -d DURATION, --duration DURATION
                        duration of the test (in secs)
  -i INPUT, --input INPUT
                        specify input file path
  -o OUTPUT, --output OUTPUT
                        specify output file path
</pre>
---

``#./polylat.py -d 15 -l 350 -o outfile.txt``
<pre>
The function tracer has been launched with the following parameters:
measure unit:          nsecs

occurrency limit:                       350
sleep time:                             5
test duration:                          15
output file                             outfile.txt

Functions tracer starting...please wait


+++++++++++++++++++++  OK  ++++++++++++++++++++++++
You are currently tracing the requested functions, please start your program,
then wait 15 secs or press ^C to stop tracing...

++++++++++++++++++++  STOP  +++++++++++++++++++++++
Test terminated, final stats computing...


#DATE: 2018-12-18               TIME: 21:50             ELAPSED TIME: 00:00:10


++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  BEGIN SUMMARY  ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#FUNCTION                                      COUNT      TOT TIME SPENT (nsecs)        % OVER TOTAL TIME      LATENCY AVG (nsecs)
__cgroup_bpf_run_filter_skb                  4128904              1606795132.000         41.020                  389.158
__bpf_redirect                               2055392               827404304.000         21.123                  402.553
bpf_redirect                                 2049689               743886195.500         18.991                  362.926
bpf_check_uarg_tail_zero                         438                  224037.000          0.006                  511.500
bpf_prog_alloc                                    12                  116730.000          0.003                 9727.500
bpf_prog_calc_tag                                 10                   26107.000          0.001                 2610.700
bpf_prog_realloc                                  22                    8437.000          0.000                  383.500
bpf_jit_blind_constants                            4                    1534.000          0.000                  383.500
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  END SUMMARY  ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

event = '__cgroup_bpf_run_filter_skb'
     nsecs               : count     distribution
         0 -> 1          : 0        |                                        |
         2 -> 3          : 0        |                                        |
         4 -> 7          : 0        |                                        |
         8 -> 15         : 0        |                                        |
        16 -> 31         : 0        |                                        |
        32 -> 63         : 0        |                                        |
        64 -> 127        : 0        |                                        |
       128 -> 255        : 26705    |                                        |
       256 -> 511        : 4049282  |****************************************|
       512 -> 1023       : 512944   |***************                         |
      1024 -> 2047       : 715      |                                        |
      2048 -> 4095       : 519      |                                        |
      4096 -> 8191       : 399      |                                        |
      8192 -> 16383      : 173      |                                        |
     16384 -> 32767      : 86       |                                        |
     32768 -> 65535      : 3        |                                        |

event = '__bpf_redirect'
     nsecs               : count     distribution
         0 -> 1          : 0        |                                        |
         2 -> 3          : 0        |                                        |
         4 -> 7          : 0        |                                        |
         8 -> 15         : 0        |                                        |
        16 -> 31         : 0        |                                        |
        32 -> 63         : 0        |                                        |
        64 -> 127        : 0        |                                        |
       128 -> 255        : 0        |                                        |
       256 -> 511        : 1968838  |****************************************|
       512 -> 1023       : 85147    |*                                       |
      1024 -> 2047       : 702      |                                        |
      2048 -> 4095       : 333      |                                        |
      4096 -> 8191       : 290      |                                        |
      8192 -> 16383      : 178      |                                        |
     16384 -> 32767      : 37       |                                        |
     32768 -> 65535      : 2        |                                        |
...
...
...
</pre>
