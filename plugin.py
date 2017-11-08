
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
		self.conns = dict()
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
				if len(reg_match.groups()) > 1 :
					file_type = reg_match.group(2)  
				else : 
					file_type = None
				self.logger.debug("found " + str(file_type) + " file: " + str(full_path))
				self.conns[full_path] = str(file_type)
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

	def  find_tasks_generator(self) :
		"wytnij fragment definicji"
		i = 1
		region = self.view.find("tasks_to_generate([\s|\S])+end_of_tasks_to_generate", 0)
		while region :
			self.logger.info("found task to process #" + str(i))
			yield region
			region = self.view.find("tasks_to_generate([\s|\S])+end_of_tasks_to_generate", region.end() + 1)


	def find_groups(self, task_region):
		"znajdź fragmenty o wspólnych ścierzkach globalnych"
		groups = []
		group_regions = self.find_in_region(task_region, "//\s[\w|/|\[\]]+[^}]*\}")
		self.logger.info("found " + str(len(group_regions)) + " groups")
		for gr in group_regions :
			groups.append(self.CreateGroup(self.view.substr(gr)))
		return groups

	
	def parse_one(self, reg, files):
		"funkcja która w plikach w liście files znajduje matche do reg"
		outcome = dict();
		found_flags={}
		for fl in files:
			with open(fl, 'r') as f:
				for line in f:
					res = reg.search(line)
					# 1: adres bitowy, 2: #word, 3: #bit, 4:#leaf, 5 [nn], 6=nn
					if res: 
						idx=0
						if res.group(5) : 
							idx=int(res.group(6))
						outcome[int(res.group(1))] = idx
						#self.logger.info("found " + str(res.groups()) +" file:"+fl)
						found_flags[fl]=True
		if len(found_flags) >1:
			raise Exception("Found leaf in both read and write files")
		if len(found_flags) ==0:
			return (outcome, None)
		file_name=list(found_flags.keys())[0]			
		return (outcome, files[file_name])


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
				try:
					(match, ft) = self.parse_one(pat, self.conns)
				except Exception as e:
					if str(e) == "Found leaf in both read and write files" :
						raise Exception("Variable " + v.name + " found in both read and write files!") from e
				if len(match) > 0 :					
					# self.logger.debug("found match for " + v.name + " \n" + str(match))
					v.map = match
					v.n_start = int(min(match.values()))
					v.n_end   = int(max(match.values()))
					v.one_bit = (v.n_start == v.n_end)					
					v.write = (ft == 'write')
					v.failed = False
					self.logger.info(v.name + " : " + str(v.n_start) + "," + str(v.n_end) + "," + str(v.addr))
				else :
					self.logger.error("NOTHING FOUND IN CONNS FOR " + v.name + " : " + str(total_path) )
				g.variables.append(v)	
		return g



	def run(self, edit):
		print(separator)
		self.conns = dict()
		self.find_conns()
		#print("tasks len: ", len(tasks))	
		tasks_generator = self.find_tasks_generator()	
		while True :
			task = next(tasks_generator, None) 
			if task == None : 
				break
			groups = self.find_groups(task)
			self.logger.info("found " + str(len(groups)) + " groups")
			#self.view.insert(edit, task.end(), "\n //AUTO GENERATED PART \n")
			for gr in groups :
				# print("GROUP path=", gr.path )
				self.updateAddr(edit, gr, task)
			(read, write) = self.transformToWordMap(groups)
			# print(read)
			# print(write)
					



	def updateAddr(self, edit, group, task) :
		self.logger.info("updating scopes for " + group.path)
		for var in group.variables :
			if not var.failed :
				if not var.one_bit:
					self.logger.info("updating scope for " + var.name)
					var_region = self.find_in_region(task, var.name)[0]
					line_region = self.view.line(var_region)
					scope_region = self.find_in_region(line_region, "\[[0-9]*:?[0-9]*\]")[0]
					self.logger.debug("found scope_region for " + var.name + " r: " + self.view.substr(scope_region) + " " + str(scope_region))
					self.view.replace(edit, scope_region, "[" + str(var.n_end - var.n_start) + ":" + str(var.n_start) + "]")
				else :
					self.logger.info("ommiting " + var.name + " because its one_bit")
			else :
				self.logger.error(var.name + " failed. no scope to update")

	def findWords(self, group):
		words_write = dict()
		words_read = dict()
		for gr in groups :
			for var in gr.variables :
				if var.write :
					if words_write[var.word] :
						words_write[var.word].append(var)
					else :
						words_write[var.word] = [var]
				else :
					if words_read[var.word] :
						words_read[var.word].append(var)
					else :
						words_read[var.word] = [var]
		return (words_write, words_read)

	def transformToWordMap(self, groups) :
		read = dict()
		write = dict()
		for g in groups :
			for v in g.variables :
				if (not v.failed) and (not v.one_bit) :
					print(v.name, v.failed)
					dictionary = write if v.write else read
					stop = int(max(v.map.keys())/32) + 1
					start = int(min(v.map.keys())/32)
					for word_num in range(start, stop) :
						lis = list(filter(lambda x : int(x[0]/32) == word_num, v.map.items() ))
						if word_num in dictionary :
							dictionary[word_num].append((v.name, lis))
						else :
							dictionary[word_num] = [(v.name, lis)]
		return (read, write)

		





#generates a separated space for function
def createVarFunction(inside, word_num) :
    s = ""
    s += "// function for word #" + word_num + "\n"
    s += inside + "\n"
    s += "// end_of_function for variable " + varName + "\n"
    return s