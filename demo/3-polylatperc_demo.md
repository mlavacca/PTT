# Polylatperc.py video
[![asciicast](https://asciinema.org/a/231759.svg)](https://asciinema.org/a/231759)

### Video summary

1. like in the previous demos, let's create a poly cube network and make it work by using iperf3
2. start polylatperc.py in tune mode
   * this mode performs an analysis needed by the tool in order to give an accurate result in the tracing phase
3. modify the polycube_dump.txt file in order to tell the tool which functions to monitor
   * comment the unwanted rows
4. start polylatper.py in trace mode
5. the output of this tool gives the real time taken by each monitored function in relation to total time taken by the eBPF program