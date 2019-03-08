# Polycount.py video

[![asciicast](https://asciinema.org/a/231689.svg)](https://asciinema.org/a/231689)

### Video summary:

1. start polycubed

2.  launch a bash script that creates a network with a simplebridge connecting 2 namespaces ns1 and ns2

3. use ns1 as iperf3 server

4. use ns2 as iperf3 client

5. start polycount.py

   - if no input is specified, an automatic configuration file is created and used (~/PTT/polycount_functions.conf)
   - it is possible to edit that file to customize your tracing

6. the output of this tool contains the list of monitored functions, the counter of calls and the percentage over the total amount of monitored functions' calls.

   - by default the output is written into ~/PTT/polycube_dump,txt

   - this file will also be used as the input file by the other tools