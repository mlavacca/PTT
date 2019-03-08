# PTT - Polycube Tracing Toolkit
PTT is a set of tools which allows the polycube services developer to trace and profile his own eBPF services by knowing which functions (and the amount) are called by them, and the latency expended, giving some additional informations such as latency distribution in histograms and the latency percentage for each kernel function in relation to total time taken by the whole eBPF service. With these informations it is possible to have a report about the key points and the bottlenecks of the polycube services. It makes use of BCC, a toolkit for creating efficient kernel tracing and manipulation programs that uses extended BPF for creating kprobes and attach callbacks to them.
## Requirements
* PTT needs the [BCC](https://github.com/iovisor/bcc) toolkit to be installed.
* For being able to make an exhaustive use of the advice for use section it is recommended to install [iperf3](https://software.es.net/iperf/) with ``sudo apt-get install iperf3``.

## Reference guides
See [docs](docs/README.md) for the reference guides and some examples of PTT tools.
## Tools
* tools/[polycount.py](tools/polycount.py): counts monitored functions calls inside an eBPF service. [Example](docs/polycount_example.md).
* tools/[polylat.py](tools/polylat.py): measures the count and the latency of eBPF monitored functions; as result it gives a brief summary and a histograms for each monitored function showing the latency distribution in logarithmic scale (the computation of the latency can be not so precise). [Example](docs/polylat_example.md).
* tools/[polylatperc.py](tools/polylatperc.py): measures the count and the latency of monitored functions inside eBPF service in a very precise way and gives the occurrency percentage relating to the total amount of eBPF program calls. [Example](docs/polylatperc_example.md).
## Advice for use
In order to perform an effective polycube service analysis, the developer can refer to the demo videos in the [demo](demo) section; the videos should be watched according to the following order:
1. [polycount_demo](demo/1-polycount_demo.md)
2. [polylat_demo](demo/2-polylat_demo.md)
3. [polylatperc_demo](demo/3-polylatperc_demo.md)

It is available a powerpoint presentation which gives a quick overview of the whole project: [slides](docs/PTT_slides.pptx).

