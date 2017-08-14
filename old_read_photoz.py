import sys, os

inputtable = sys.argv[1]
inputzs = sys.argv[2]
outputtable = sys.argv[3]

outrename2 = '/tmp/zs4'


asconf = '/tmp/ascout.conf'
asc = open(asconf,'w')
keys = ['photID','photoz','less045','greater045']
for name in keys:
	asc.write('#\nCOL_NAME = ' + name + '\nCOL_TTYPE= FLOAT\nCOL_HTYPE= FLOAT\nCOL_COMM= ""\nCOL_UNIT= ""\nCOL_DEPTH= 1\n')
	#asc.write('#\nCOL_NAME = ' + mag_name_err + '_color_' + filter + '\nCOL_TTYPE= FLOAT\nCOL_HTYPE= FLOAT\nCOL_COMM= ""\nCOL_UNIT= ""\nCOL_DEPTH= 1\n')
asc.close()

command = "asctoldac -i " + inputzs + " -o " + outrename2 + " -t OBJECTS -c " + asconf
print command
os.system(command)

input = reduce(lambda x,y: x + " " + y,keys)

command = "ldacjoinkey -t OBJECTS -i " + inputtable + " -p " + outrename2 + " -o " + outputtable + " -k " + input
print command
os.system(command)
