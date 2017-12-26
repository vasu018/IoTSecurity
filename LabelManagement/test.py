#!/usr/bin/python 
import re
#from numpy import *
#import numpy as np
#from StringIO import StringIO


label_defs_filename = "/etc/neutron/label_definition.conf"

ldef_file_handle = open(label_defs_filename, 'r')
label_file_data_t = ldef_file_handle.read()
ldef_file_handle.close()

spacePattern = re.compile(r'\s+')
label_file_data = re.sub(spacePattern, ' ', label_file_data_t)
label_definitions = re.findall('\{.*?\}', label_file_data)

for label_definition in label_definitions:
    print label_definition

############################
#pat = re.compile(r'\{\W+\}')
#pat = re.compile(r'{\W+')
#result = re.match(pat, s)
#print result


#for entry in pat.findall(s):
#    print "Entry details are:", entry

#DataIn = loadtxt('test.data')
#print DataIn
#data = numpy.loadtxt('test.data')
#print data
#print s

#d = StringIO(s)
#np.loadtxt(d, dtype={'VALUES': ('NAME', 'KEY', 'VALUE', 'DATA_SOURCE', 'CONDITION'), 'formats': ('S1', 'S1', 'S1', 'S1')})
#newLinePattern = re.compile(r'\s+')
#s_mod = re.sub(newLinePattern, ' ', s_mod)
#print s
