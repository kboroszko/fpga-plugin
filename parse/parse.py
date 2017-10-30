import re


# funkcja która przyjmuje:
# słownik regs regexp -> nazwa zmiennej
# listę files w której są nazwy plików w których należy szukać
def parse_multiple(regs, files):
	outcome = dict()
	for fl in files :												#dla każdego pliku conn
		with open(fl, 'r') as f:
			for line in f:
				for key in regs :									#dla każdego regexpa
					res = key.search(line)
					if res: 										#jeśli znaleziono match
						if regs[key] in outcome : 					#jeśli już coś takiego znaleziono
							outcome[regs[key]]["n"] += 1 			#dodaj tylko liczbę bitów
						else:
							tmp = dict()
							tmp["addr"] = int(res.group(1)) 
							tmp["word"] = int(res.group(2))
							tmp["bit"] = int(res.group(3))
							tmp["leaf"] = int(res.group(4))
							tmp["n_end"] = int(res.group(5))           	#liczba bitów które znaleziono
							tmp["n_start"] = int(res.group(5))		#bit od ktorego sie zaczyna
							outcome[regs[key]] = tmp
	return outcome


def parse_one( reg, files):
	outcome = dict();
	print(files)
	count = 0
	for fl in files:
		with open(fl, 'r') as f:
			for line in f:
				res = reg.search(line)
				count += 1
				if res: 
					# for i in range(len(res.groups())) :
					# 	print(i, res.group(i))
					if "n_end" in outcome :
						outcome["n_end"] = int(res.group(5)[1:-1])           	#liczba bitów które znaleziono
					else :	
						outcome["addr"] = int(res.group(1)) 
						outcome["word"] = int(res.group(2))
						outcome["bit"] = int(res.group(3))
						outcome["leaf"] = int(res.group(4))
						if res.group(5) :
							outcome["n_end"] = int(res.group(5)[1:-1])           	#liczba bitów które znaleziono
							outcome["n_start"] = int(res.group(5)[1:-1])		#bit od ktorego sie zaczyna
	print("lines searched: ", count)
	return outcome


# def parse_one(reg, files):
# 	outcome = dict();
# 	print ("dupa")
# 	print(reg)
# 	print(files)
# 	for fl in files:
# 		with open(fl, 'r') as f:
# 			for line in f:
# 				res = reg.search(line)
# 				if res: 
# 					if "n_end" in outcome :
# 						outcome["n_end"] = int(res.group(5))           	#liczba bitów które znaleziono
# 					else :	
# 						outcome["addr"] = int(res.group(1)) 
# 						outcome["word"] = int(res.group(2))
# 						outcome["bit"] = int(res.group(3))
# 						outcome["leaf"] = int(res.group(4))
# 						outcome["n_end"] = int(res.group(5))           	#liczba bitów które znaleziono
# 						outcome["n_start"] = int(res.group(5))		#bit od ktorego sie zaczyna
# 	return outcome


# # test:
# path = 'io_frw_i/hydra/hydra2_0/inst/i_hydra_lux'
# var_name1 = 'start_addr'
# var_name2 = 'frame_skip'
# var_name3 = 'line_cntr/val'
# var_name4 = 'frame_cntr/val'
# phrase1 = re.compile('([0-9]+)\s([0-9]+)\s([0-9]+)\s.*([0-9]+)\s.*' + path + '/' + var_name1 + '\[([0-9])+\]')
# phrase2 = re.compile('([0-9]+)\s([0-9]+)\s([0-9]+)\s.*([0-9]+)\s.*' + path + '/' + var_name2 + '\[([0-9])+\]')
# phrase3 = re.compile('([0-9]+)\s([0-9]+)\s([0-9]+)\s.*([0-9]+)\s.*' + path + '/' + var_name3 + '\[([0-9])+\]')
# phrase4 = re.compile('([0-9]+)\s([0-9]+)\s([0-9]+)\s.*([0-9]+)\s.*' + path + '/' + var_name4 + '\[([0-9])+\]')


# # phrase = re.compile('.*hydra.*')
# files = ['conn0.txt', 'conn2.txt']
# regs = dict()
# regs[phrase1] = var_name1
# regs[phrase2] = var_name2
# regs[phrase3] = var_name3
# regs[phrase4] = var_name4

# import time 

# t = time.time()
# r = parse(regs, files)
# print('function took ', (time.time() - t)*1000, "ms")    #u mnie zajmuje 30ms

# print(r)