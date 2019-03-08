# Demonstration of polycount

It prints on the ``~/polycube_dump.txt`` file the monitored functions and the amount of calls for each of them

---

``$ ./polycount.py --help``
<pre>
usage: polycount.py [-h] [-v | -b] [-o OUTPUT] [-i INPUT]

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         increase output verbosity
  -b, --brief           reduce output verbosity
  -o OUTPUT, --output OUTPUT
                        specify output file path
  -i INPUT, --input INPUT
                        specify input file
</pre>
--- 

``#./polycount.py``
<pre>

#DATE: 2018-12-16                  TIME: 14:09                ELAPSED TIME: 00:00:16

#FUNCTION                                                          COUNT           %
#TOTAL COUNT                                                     6976478     100.000

htab_map_update_elem:                                            1739825      24.938
__htab_map_lookup_elem:                                          1739702      24.937
bpf_ktime_get_ns:                                                1738209      24.915
bpf_redirect:                                                    1738114      24.914
bpf_opcode_in_insntable:                                           13434       0.193
bpf_adj_branches:                                                    630       0.009
bpf_prog_realloc:                                                    618       0.009
bpf_patch_insn_single:                                               614       0.009
bpf_patch_insn_data:                                                 464       0.007
bpf_int_jit_compile:                                                 316       0.005
</pre>