pathIndex = "/mnt/d/Experiment/enwiki-20200101-pages-articles-multistream-index.txt"
outputfile = "/mnt/d/Experiment/index.txt"
with open(pathIndex, "r") as indices, open(outputfile, "w") as out:
	lines = indices.readlines()
	num = 0
	prev = 0
	for line in lines:
		i = 0
		for c in line:
			if c != ':':
				i += 1
			else:
				break
		num = line[:i]
		if num != prev:
			out.write(num+'\n')
			prev = num
