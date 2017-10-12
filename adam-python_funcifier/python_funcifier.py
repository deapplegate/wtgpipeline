#! /usr/bin/env python
#adam-use# use with any python script that is a long list of functions to see which functions call which other functions
#adam-old# other_words2include=["clusters_db","slrstatus"] can do this to get funcs that deal with these words and the other funcs that they call
other_words2include=[] 
import sys
import os
import re
code_full_path=sys.argv[-1]
code=os.path.basename(code_full_path)
codeshort=code.rsplit('.')[0]
fl_def="def_logger-%s.log" % (codeshort)
fl_func="func_logger-%s.log" % (codeshort)
fl_docstring="docstring_logger-%s.log" % (codeshort)

if not os.path.isfile(fl_def):
	command_def='grep "^def\ " %s > %s' % (code_full_path,fl_def)
	print 'command_def=',command_def
        ooo=os.system(command_def)
        if ooo!=0: raise Exception("the line os.system(command_def) failed\ncommand_def="+command_def)



fo=open(fl_def,'r')
lines=fo.readlines()

def_lines=[l[4:] for l in lines if l.startswith('def')]
funcs=[l.split('(')[0] for l in def_lines]
func_info={}
for func in funcs:
    func_info[func]={'calls':[],'called_by':[],'calls_lines':[],'called_by_lines':[],'docstring':'','inputs':[],'returns':[],'cant_place':[]}

func_words_str='\<'+'\>\|\<'.join(funcs+other_words2include)+'\>'
if not os.path.isfile(fl_func):
	command_grep_funcs= 'grep "'+func_words_str+'\|\<return\>" '+code_full_path+" > "+fl_func
	print 'command_grep_funcs=',command_grep_funcs
        ooo=os.system(command_grep_funcs)
	#suggested add-ons: %g/'''/d ; %g/^\s*#/d ; %g/^\s*print/d
        if ooo!=0: raise Exception("the line os.system(command_grep_funcs) failed\ncommand_grep_funcs="+command_grep_funcs)
	my_input=raw_input('want to clean up the file (%s) first? [y/n]' % (fl_func))
	if my_input=='y':
		raw_input('Hit Enter when youre done')
	elif my_input=='n':
		pass
	else:
		raise Exception("You have to enter 'y' or 'n'!")

fo=open(fl_func,'r')
lines=fo.readlines()

for line in lines:
	#don't deal with docstrings yet
	#don't deal with body of file yet
	#should make sure lines are really within the function (using the line numbers)
	if line.startswith('def'):
		defmatch=re.match("def (.*)\((.*)\):.*\n",line)
		function=defmatch.group(1)
		inputs=defmatch.group(2).split(',')
		func_info[function]['inputs']=inputs
	elif line.startswith('  ') or line.startswith('\t'):
		ls=line.strip()
		if ls.startswith("if") or ls.startswith("elif") or ls.startswith("else"):
			if ":" in line:ls=line.split(":",1)[-1].strip()
		if "print " in ls:
			ls=ls[6:]
		Neq=ls.count('=')
		Npar=ls.count("(")
		if ls.startswith("#"):
			continue
		elif ls.startswith("return"):
			returnmatch=re.match("return(.*)",ls)
			returns=returnmatch.group(1).split(',')
			func_info[function]['returns']=returns
			for func in funcs:
				if func in ls:
					func_called=func
					func_info[function]['calls'].append(func_called)
					func_info[function]['calls_lines'].append(line.strip())
					func_info[func_called]['called_by'].append(function)
					func_info[func_called]['called_by_lines'].append(line.strip())					
		elif Neq and Npar:
			Ieq=ls.index('=')
			Ipar=ls.index("(")
			if Ieq<Ipar: #of the form a=func(...)
				func_called=ls[Ieq+1:Ipar].strip()
				if func_called in funcs:
					func_info[function]['calls'].append(func_called)
					func_info[function]['calls_lines'].append(line.strip())
					func_info[func_called]['called_by'].append(function)
					func_info[func_called]['called_by_lines'].append(line.strip())
				else:
					func_info[function]['cant_place'].append(line.strip())
					print function+' (cant_place): '+line.strip()
			else: #of the form func(a=1,...)
				func_called=ls[:Ipar].strip()
				if func_called in funcs:
					func_info[function]['calls'].append(func_called)
					func_info[function]['calls_lines'].append(line.strip())
					func_info[func_called]['called_by'].append(function)
					func_info[func_called]['called_by_lines'].append(line.strip())
				else:
					func_info[function]['cant_place'].append(line.strip())
					print function+' (cant_place): '+line.strip()
		elif Npar: #of the form func(...)
			Ipar=ls.index("(")
			func_called=ls[:Ipar].strip()
			if func_called in funcs:
				func_info[function]['calls'].append(func_called)
				func_info[function]['calls_lines'].append(line.strip())
				func_info[func_called]['called_by'].append(function)
				func_info[func_called]['called_by_lines'].append(line.strip())
			else:
				func_info[function]['cant_place'].append(line.strip())
				print function+' (cant_place): '+line.strip()
		else:
			func_info[function]['cant_place'].append(line.strip())
			print function+' (cant_place): '+line.strip()

## now print it out so it can be coppied into the code
for func in funcs:
    f=func_info[func]
    print "\n#####",func,"#####"
    k="inputs"
    print "    '''%s: %s" % (k,",".join(f[k]))
    k="returns"
    print "    %s: %s" % (k,",".join(f[k]))
    k="calls"
    print "    %s: %s" % (k,",".join(f[k]))
    k="called_by"
    print "    %s: %s'''" % (k,",".join(f[k]))


fo=open(fl_docstring,'w')
for func in funcs:
    f=func_info[func]
    fo.write( "\n##### "+func+" #####\n")
    k="inputs"
    fo.write( "    '''%s: %s\n" % (k,",".join(f[k])))
    k="returns"
    fo.write( "    %s: %s\n" % (k,",".join(f[k])))
    k="calls"
    fo.write( "    %s: %s\n" % (k,",".join(f[k])))
    k="called_by"
    fo.write( "    %s: %s'''\n" % (k,",".join(f[k])))
fo.close()
