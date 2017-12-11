#!/usr/bin/perl

chdir ("/home/vasudevan/Desktop/Plots/icdcs/IoTSecurity/Plots/abstraction/");
system("pwd");
`python line.py`;
chdir("/home/vasudevan/Desktop/Plots/icdcs/IoTSecurity/Plots/composition/");
system("pwd");
`python line.py`;
chdir("/home/vasudevan/Desktop/Plots/icdcs/IoTSecurity/Plots/cpu/");
system("pwd");
`python bar_8.py`;
chdir("/home/vasudevan/Desktop/Plots/icdcs/IoTSecurity/Plots/depth/");
system("pwd");
`python line.py`;
chdir("/home/vasudevan/Desktop/Plots/icdcs/IoTSecurity/Plots/memory-abstraction/");
system("pwd");
`python bar.py`;
chdir("/home/vasudevan/Desktop/Plots/icdcs/IoTSecurity/Plots/memory-composition/");
system("pwd");
`python bar.py`;
chdir("/home/vasudevan/Desktop/Plots/icdcs/IoTSecurity/Plots/comparison");
system("pwd");
`python bar.py`;
chdir("/home/vasudevan/Desktop/Plots/icdcs/IoTSecurity/Plots/data-vis");
system("pwd");
`python plot.py`;
