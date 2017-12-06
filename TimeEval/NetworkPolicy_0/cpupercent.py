import psutil
gmaxcpu = float("-inf")
gmaxmem = float("-inf")
try:
	while True:
		gmaxcpu = max(gmaxcpu,psutil.cpu_percent(interval=1))
		gmaxmem = max(gmaxmem,psutil.virtual_memory().percent)
except:
	print(gmaxcpu)
	print(gmaxmem)
