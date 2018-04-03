import os
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
matplotlib.rcParams.update({'font.size':36})

lines = open('Parking_meters.csv', 'r')

devices = []
for line in lines:
	line = line.split(',')
	print line[0], line[4], line[10], [11], line[15]

lines = open('Traffic_Signals.csv', 'r')
