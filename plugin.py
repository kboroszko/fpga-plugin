
import re
import os
import os.path
import sys
import logging

import sublime
import sublime_plugin
#import time
# from .parse import *
from .const.const import *

#print("fpga plugin time=",time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()))
class GeneratorCommand(sublime_plugin.TextCommand):

	def __init__(self, x):
		self.conns = []
		self.logger = logging.getLogger('driver_generator')
		self.logger.setLevel(logging.DEBUG)
		self.logger.propagate = False

		ch = logging.StreamHandler()
		ch.setLevel(logging.DEBUG)
		formatter = logging.Formatter('%(asctime)s\t%(levelname)s: function:\"%(funcName)s\" : %(message)s')
		ch.setFormatter(formatter)
		self.logger.handlers = []
		self.logger.addHandler(ch)

		super(GeneratorCommand, self).__init__(x)
		#print("GC init time=",time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()))


	def find_in_region(self, reg, pattern):
		tmp = []
		region = self.view.find(pattern, reg.begin())
		while  region and region.begin() >= reg.begin() and region.end() <= reg.end() :
			tmp.append(region)
			region = self.view.find(pattern, region.end())
		return tmp

	def find_conns(self):
		"znajdź nazwy plików conn"
		found = False
		regions = self.view.find_all("conn_file:")
		for r in regions :
			l = self.view.line(r)
			reg_match = conn_file_name.match(self.view.substr(l))
			if reg_match : 
				pwd = os.path.dirname(os.path.abspath(__file__))
				full_path = str(pwd) + "\\" + reg_match.group(1)
				self.logger.debug("found file: " + str(full_path))
				self.conns.append(full_path)
				found = True
		self.logger.info("found " + str(len(self.conns)) + " conns")
		self.logger.debug("conns: " + str(self.conns))
		if not found :
			self.logger.error("NO CONN FILES FOUND!")
			raise Exception("NO CONN FILES FOUND!")

	def  find_tasks(self) :
		"wytnij fragment definicji"
		regions = self.view.find_all("tasks_to_generate([\s|\S])+end_of_tasks_to_generate")
		self.logger.info("found " + str(len(regions)) + " tasks to process")
		return regions

	def find_groups(self, task_region):
		"znajdź fragmenty o wspólnych ścierzkach globalnych"
		groups = []
		group_regions = self.find_in_region(task_region, "//\s[\w|/|\[\]]+[^}]*\}")
		self.logger.info("found " + str(len(group_regions)) + " groups")
		for gr in group_regions :
			groups.append(self.CreateGroup(self.view.substr(gr)))
		return groups
		# print(len(regions))
		# print(self.view.substr(regions[0]))

	
	def parse_one(self, reg, files):
		"funkcja która w plikach w liście files znajduje matche do reg"
		outcome = dict();
		for fl in files:
			with open(fl, 'r') as f:
				for line in f:
					res = reg.search(line)
					# 1: adres bitowy, 2: #word, 3: #bit, 4:#leaf, 5 [nn], 6=nn
					if res: 
						if res.group(5) : 
							idx=int(res.group(6))
						else: 			
							idx=0
						id={'#':1,'w':2,'b':3}
						outcome[idx]=dict([(k,res.group(n)) for (k,n) in id.items()])
						outcome[idx]['idx']=idx
		return outcome


	def CreateGroup(self, chunk):
		"opracuj poszczególne deklaracje"
		reg_match = var_path_section.search(chunk.split('\n')[0])
		g = VarGroup( reg_match.group(0))
		self.logger.debug("group g.path=" + str(g.path))
		for (nl,line) in enumerate(chunk.split("\n")) :
			reg_match = var_parse.search(line)
			if reg_match :
				v = Variable()
				v.name = reg_match.group(1)
				v.path = reg_match.group(2)
				total_path = str(os.path.normpath(g.path + '/' + v.path)).replace("\\", "/")
				self.logger.debug("variable " + v.name + " total_path=" + str(total_path))
				pat = re.compile(conn_line_start + total_path + conn_line_end) 
				match = self.parse_one(pat, self.conns)
				if len(match) > 0 :					
					v.n_start = min(match.keys())
					v.n_end   = max(match.keys())
					v.one_bit = (v.n_start == v.n_end)					
					v.addr = match[v.n_start]['#']
					v.word = match[v.n_start]['w']
					v.bit  = match[v.n_start]['b']
					#(region, "(\[[0-9|:]*\]\s*)?\w+;\s*//\s*[\w|\.|/]+[\[|\]]*") :
					v.failed = False
					self.logger.debug(v.name + " : " + str(v.n_start) + "," + str(v.n_end) + "," + str(v.addr))
				else :
					self.logger.error("NOTHING FOUND IN CONNS FOR " + v.name + " : " + str(total_path) )
				g.variables.append(v)	
		return g



	def run(self, edit):
		print(separator)
		self.conns = []
		self.find_conns()
		tasks = self.find_tasks()
		#print("tasks len: ", len(tasks))		
		for task in tasks :  #zamienic na for i, e in reversed(list(enumerate(task))):
			# print(self.view.substr(task))
			groups = self.find_groups(task)
			#self.view.insert(edit, task.end(), "\n //AUTO GENERATED PART \n")
			for gr in groups :
				print("GROUP path=", gr.path )
				for v in gr.variables :
					print("var ", v.path,", name=",v.name,", ", "failed" if v.failed else "succ.")
					#self.view.insert(edit, task.end(), createVarFunction("//inside", v.name))
			#self.view.insert(edit, task.end(), "\n //END_OF AUTO GENERATED PART \n") 



		# pat = re.compile('([0-9]+)\s([0-9]+)\s([0-9]+)\s.*([0-9]+)\s.*' + "io_frw_i/hydra/hydra2_0/start_addr" + '\[([0-9])+\]') 
		# print('([0-9]+)\s([0-9]+)\s([0-9]+)\s.*([0-9]+)\s.*' + "io_frw_i/hydra/hydra2_0/start_addr" + '\[([0-9])+\]')
		# match = self.parse_one(pat, self.conns)
		# print(match)

		# regs = self.find_tasks() # self.find_in_region(self.find_tasks()[0], "(?:\[[0-9|:]+\]*\s*)?\w+;\s*\/\/\s*([\w|\.|/]+)[\[|\]]*")
		# #"(\[[0-9|:]*\]\s*)?\w+;\s*//\s*[\w|\.|/]+[\[|\]]*")
		# print(len(regs))
		# i = 0
		# for r in regs :
		# 	i += 1
		# 	s = self.view.substr(r);
		# 	print(i, s)
		# 	for line in s.split('\n') :
		# 		print("line: ", line)
		# 		found = var_path_section.search(line)
		# 		if found :
		# 			print("MATCH")
		# 			print(found.group(0))
#generates a separated space for function
def createVarFunction(inside, varName) :
    s = ""
    s += "// function for variable " + varName + "\n"
    s += inside + "\n"
    s += "// end_of_function for variable " + varName + "\n"
    return s