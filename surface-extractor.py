import csv
import sys
import operator

csv.field_size_limit(sys.maxsize)

# Input file should have the destination surface names in sorted order!
PATH_INPUT_SURFACE_NAMES = '/datapartition/surface-names/output2016/sorted_sn.csv'
PATH_OUTPUT_SURFACE_NAMES = '/datapartition/surface-names/output2016/sn_count.csv'

reader = csv.reader(open(PATH_INPUT_SURFACE_NAMES), delimiter=",")

# Since the csv file is very large, we have to read it using a generator
# Creating a list will exceed typical memory limits
def gen_reader():
    for row in reader:
        yield row

with open(PATH_OUTPUT_SURFACE_NAMES, 'w') as output:
    outputWriter = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
    outputWriter.writerow(["Article", "Surface Name", "Frequency"])

    prevArticle = ""
    nextArticle = ""
    articleDict = {}
    first = True
    index = 0
    totalRows = 182453116
    for row in gen_reader():
        index += 1
        prevArticle = nextArticle
        try:
            nextArticle	= row[2]
        except IndexError: # Since the csv file will not be 100% clean, i.e, some rows may have poor formatting
            continue
        try:
            surfaceName = row[3]
        except IndexError:
            continue
        if surfaceName in articleDict:
            articleDict[surfaceName] += 1
        else:
            articleDict[surfaceName] = 1
        if nextArticle != prevArticle and first == False:
            for key, value in articleDict.items():
                outputWriter.writerow([prevArticle, key, value])
            articleDict = {}
            print("Progress = %s percent" % (index/totalRows))
        first = False
