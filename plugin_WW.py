import sublime
import sublime_plugin
import re

class RegexpSeriesCommand(sublime_plugin.TextCommand):

	def region_outer(self,rs1,rs2):
		"dla każdego r1 z rs1 znajdź zawarte w nim regiony r2 z rs2"
		return [list(filter(lambda r:r1.contains(r),rs2)) for r1 in rs1]

	def region_outer3(self,rs1,rs2,rs3):
		"dla każdego r1 z rs1 znajdź zawarte w nim regiony r2 z rs2"
		oo12=self.region_outer(rs1,rs2);
		f2=lambda lrs:list(map(self.region_outer(lrs,rs3)))
		return list(map())

	def find_decl(self):
		"znajdź linijkę deklaracji"
		return self.view.find_all("bit(\s+\[[0-9:]+])?\s+([\w]+);\s*//\s*([\w/\[\].]+)")

	def find_groups(self) :
		"znajdź grupę definicji"
		return self.view.find_all("//\s[\w|/|\[\]]+\s{[^}]*\}")
		
	def find_tasks(self) :
		"znajdź fragment definicyjny"
		return self.view.find_all("tasks_to_generate([\s|\S])+end_of_tasks_to_generate")

	def run(self, edit, extra=None):	    
		task_rs=self.find_tasks()
		print("tasks:",task_rs)
		groups_rs=self.find_groups()
		print("groups:",groups_rs)
		tg_rss=self.region_outer(task_rs,groups_rs)
		print(tg_rss[0])
		self.set_sels(tg_rss[0])

	def set_sels(self,regions):
		sel = self.view.sel()
		sel.clear()
		sel.add_all(regions)

	def find_conns(self):
		"znajdź nazwy plików conn"
		found = False
		regions = self.view.find_all("conn_file:")
		for r in regions :
			l = self.view.line(r)
			#print("find_conns found region: ", "b: ",  l.begin(), " e:", l.end(), " s:", l.size())
			#print(self.view.substr(l))
			reg_match = conn_file_name.match(self.view.substr(l))
			if reg_match : 
				pwd = os.path.dirname(os.path.abspath(__file__))
				full_path = str(pwd) + "\\" + reg_match.group(1)
				#print("filename:", full_path)
				self.conns.append(full_path)
				found = True
		print("conns: ",self.conns)
		if not found :
			print("NO CONN FILES FOUND!")


        
