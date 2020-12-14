""" 
Description: This tool generates design space expoloration result (Area vs Latency plot)  of a given C/SystemC design
Simulated annealling applied here as meta heuristic  

This tool is designed targeting NEC CyberWorkBench as HLS tool

Command: python explorer.py <name_of_design.c> <name_of_attribute_library.info>
Generates report file, report.CSV	

Option: 
	-h : help


"""



import sys
import re
import os
import random
import time
import numpy
import math
import shutil
#from __future__ import division
 







### This part deals with the arguments
if ("-h" in sys.argv):

	print()
	print("*****Welcome to Help*****")
	print()
	print("Command to run the script: python <name_of_design> <name_of_attribute_library>")
	print("e.g.: python explorer.py ave16.c ave16_atrr_lib.info")
	exit()

elif ( len(sys.argv)>=3):
	
	if (os.path.isfile(sys.argv[1]) and os.path.isfile(sys.argv[2])):
		input_design_file=sys.argv[1]
		input_lib_file=sys.argv[2]
		
	else:
		print("File doesn't exist")
		exit("Please try again")		
	
else:
    print("Missing input file")
    exit("Please try again")
	

#time calculation start 
start_time = time.time()





##Read input files


with open (input_design_file,'r') as design_file:
    design_content=design_file.read()

with open (input_lib_file,'r') as lib_file:
    lib_content=lib_file.read()



#gather design and library info
circuit= re.search('process (.*?)\(\)',design_content).group(1)  #process is equivalent to function in CyberWorkBench
if (circuit)=='':
	exit('No process found')

  
if not (re.search('#include *\"attr\.h\"',design_content)):
	exit('attr.h is not included in design file. Please include atrr.h in your design file')

attr_list=re.findall('#(attr.*)\n',lib_content)
if (attr_list)==[]:
	exit('No attribute found')
total_attr=len(attr_list)



## Create a list with all atrribute options
attr_options_list=[]
for attr in attr_list:
	attr_options_list.append(re.findall('('+attr+'.*?Cyber.*?)\n',lib_content,re.M))
	


#input_parameters for simulated annealling
t_start=100
t_end=75
cool_rate=0.997
attr_change_percentage=20
max_attemp=3  #quits after 3 attempt if no better design is found at a certain temperature 


#number of attributes changed each time



def attribute_gen():
	''' 
	Generates set of attributes from global list attr_options_list
	created from library
	'''
	attrs_selected=[]
	for attr_options in attr_options_list:
		rand_num=random.randrange(0,len(attr_options),1)
		attrs_selected.append(attr_options[rand_num])
	
	return attrs_selected


	
def attribute_change(attr_now):
	'''
	Randomly replaces attributes in the given attr_now list
	Percentage of change is defined by attr_change_percentage
	Returns the modified list
	'''
	
	attr_change_num=round(attr_change_percentage/100*total_attr)
	attr_change_num=int(attr_change_num)
	if (attr_change_num==0):
		attr_change_num=1    

	
	rand_list=random.sample(range(0,total_attr), attr_change_num)
    
	
	
	
	
	for attr_change_index in rand_list:
		
		rand_num=random.randrange(0,len(attr_options_list[attr_change_index]),1)
		attr_now[attr_change_index]=attr_options_list[attr_change_index][rand_num]
		
	return attr_now

def cost_calc(alpha,beta,area,latency):
    '''
	returns value of cost function, cost=aplha*normalized_area+beta*normalized_latency
	'''
	
    cost=alpha*(area/area_max)+beta*(latency/latency_max)
    return cost


def do_HLS():
	'''
	performs HLS based on current 'attr.h'
	returns a flage whether HLS is performed succesfully or note
	'''
	
	global area_max,latency_max
	
	cmd1 = 'bdlpars '+input_design_file 
	cmd2='bdltran  -EE   -c1000 -s -Zresource_fcnt=GENERATE -Zresource_mcnt=GENERATE -Zdup_reset=YES -Zfolding_sharing=inter_stage -EE -lb /eda/cwb/cyber_611/LINUX/packages/asic_90.BLIB -lfl /eda/cwb/cyber_611/LINUX/packages/asic_90.FLIB +lfl '+circuit+'-auto.FLIB +lfl '+circuit+'-amacro-auto.FLIB -lfc '+circuit+'-auto.FCNT +lfc '+circuit+'-amacro-auto.FCNT -lml '+circuit+'-auto.MLIB -lmc '+circuit+'-auto.MCNT '+circuit+'.IFF'
        

	os.system(cmd1) ## parsing design file
	os.system(cmd2) ##doing high level synthesis
	   
	result_file= open(circuit+'.CSV','r')
	result_all=result_file.readlines()

	HLS_done=0  ##the flag which returns whether result has been collected or not
       
	if (result_all!=[]):
		HLS_done= 1
		result_line=result_all[1]
		str=result_line.rsplit(',', 20)
		a=int(str[0])
		b=int(str[18])
		area=a
		latency=b
        
		if (a>area_max):
			area_max=a
         
		if (b>latency_max):
			latency_max=b     

       
	return HLS_done


#initialization
alpha=0.95
beta=0.05
area_max=8647         # based on defualt cwb setting for minimum latency
latency_max=11		  # based on default cwb setting for minimum area
area=1
latency=1

#open a file to write final rerpot


report='AREA,state,FU,REG,MUX,DEC,pin_pair,net,max,min,ave,MISC,MEM,CP_delay,sim,Pmax,Pmin,Pave,Latency,BlockMemoryBit,DSP\n'

for beta in numpy.arange (0.05,1,0.1):	
#for beta in numpy.arange (0,1,1):	
	
	
	## initial design 
	while (1):
		attr_now=attribute_gen()
		
		attr_header_file=open("attr.h","w")
		for attr in attr_now:
			attr_header_file.write('#define '+attr+'\n')
		attr_header_file.close() 
		
		HLS_done=do_HLS()
		
		if(HLS_done):
			break
		else:
			continue
		
	cost_current=1 #initial cost is 1

    #update result
	shutil.copy(circuit+'.CSV', 'current.CSV')
	
	t=t_start
	while (t>=t_end):
        
		m=0
        
		while (m<max_attemp):
            
			while (1):
				attr_now=attribute_change(attr_now)
				
				attr_header_file=open("attr.h","w")
				for attr in attr_now:
					attr_header_file.write('#define '+attr+'\n')
				attr_header_file.close()
				
				HLS_done=do_HLS()
				m=m+1
                
				if (HLS_done):
					m=m-1
					break
                    
				else:
					   
					continue
            
			cost_new=cost_calc(alpha,beta,area,latency)
          
            
			rand_num=random.random()
			delta=cost_new-cost_current
            
			if ((delta<0)|(rand_num<(math.exp(-delta/t)))): 
			
				#update result
				shutil.copy(circuit+'.CSV', 'current.CSV')
				m=max_attemp+1
				cost_current=cost_new
                        
			else:
				m=m+1
   
		t=t-1
    
   
    
	current=open('current.CSV','r')
	current_lines=current.readlines()
	current_line=current_lines[1]
	report=report+current_line
	final_report=open('report.CSV','w')
	final_report.write (report)
	final_report.close()
	current.close()	

	alpha=alpha-0.1

    


#total time elapsed
report_time=open('report_time.txt','w')
report_time.write("--- %s seconds ---" % (time.time() - start_time))
report_time.close()