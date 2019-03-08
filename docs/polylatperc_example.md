# Demonstration of polylatperc

It prints on the screen (or dumps on file) file the monitored functions, 
the amount of calls for each of them, statistics about the latency time 
and the percentage of time over the total time of the BPF program to monitor.

---

``./polylatperc.py -h``
<pre>
usage: polylatperc.py [-h] {tune,trace} ...

positional arguments:
  {tune,trace}
    tune        tuning functionality
    trace       tracing functionality

optional arguments:
  -h, --help    show this help message and exit
</pre>

---

``./polylatperc.py tune -h``
<pre>
usage: polylatperc.py tune [-h] [-v | -b]

optional arguments:
  -h, --help     show this help message and exit
  -v, --verbose  increase output verbosity
  -b, --brief    reduce output verbosity
</pre>
---

``./polylatperc.py trace -h``
<pre>
usage: polylatperc.py trace [-h] [-v | -b] [-x] [-s SLEEP] [-d DURATION]
                            [-i INPUT] [-o OUTPUT]

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         increase output verbosity
  -b, --brief           reduce output verbosity
  -x, --xdp             execute xdp tracing
  -s SLEEP, --sleep SLEEP
                        time interval (in secs) between the intermediate
                        prints
  -d DURATION, --duration DURATION
                        duration of the test (in secs)
  -i INPUT, --input INPUT
                        input file path
  -o OUTPUT, --output OUTPUT
                        output file path
</pre>
---

``#./polylatperc.py trace -o out.txt -d 10``

<pre>
The function tracer has been launched with the following parameters:

sleep time:                             5
test duration:                          10
output file                             out.txt

Functions tracer starting...please wait


+++++++++++++++++++++  OK  ++++++++++++++++++++++++
You are currently tracing the requested functions, please start your program,
then wait 10 secs or press ^C to stop tracing...

++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  BEGIN SUMMARY  ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#FUNCTION                                      COUNT      TOT TIME SPENT (nsecs)        % OVER TOTAL TIME      LATENCY AVG (nsecs)

BPF PROGRAM                                   775706                   808027083         100.00                     1041

htab_map_update_elem                          775716                   110151672          13.63                      142
bpf_ktime_get_ns                              775593                    58169475           7.20                       75
__htab_map_lookup_elem                        775719                    35683074           4.42                       46
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  END SUMMARY  ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

...
...
...

++++++++++++++++++++  STOP  +++++++++++++++++++++++
Test terminated, final stats computing...

#DATE: 2018-12-18               TIME: 22:08             ELAPSED TIME: 00:00:10

++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  BEGIN SUMMARY  ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#FUNCTION                                      COUNT      TOT TIME SPENT (nsecs)        % OVER TOTAL TIME      LATENCY AVG (nsecs)

BPF PROGRAM                                  2017096                  2078281245         100.00                     1030

htab_map_update_elem                         2017189                   282406460          13.59                      140
bpf_ktime_get_ns                             2016916                   149251784           7.18                       74
__htab_map_lookup_elem                       2017221                    90774945           4.37                       45
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  END SUMMARY  ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
</pre>