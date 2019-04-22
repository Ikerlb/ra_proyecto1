import random
import itertools
import os
import time
 

class Minesweeper:
	def __init__(self,w,h,m):
		self.w=w
		self.h=h
		self.m=m

		#we will use this representation to avoid much dirtier code.
		#i also think this will simplify usage

		#holds position of mines
		self.mines=self.random_mines()
		#(i,j)->k such that grid[i,j] has k adjacent mines
		self.numbers=self.populate()
		self.uncovered=set()
		self.probed=set()

	def random_mines(self):
		mines=set()
		w=self.w
		h=self.h
		m=self.m
		while len(mines)<m:
			x=random.randint(0,w-1)
			y=random.randint(0,h-1)
			mines.add((x,y))
		return mines

	#(i,j)->k such that grid[i,j] has k adjacent mines
	def populate(self):
		w=self.w
		h=self.h
		mines=self.mines
		numbers={}
		for mine in mines:
			x=mine[0]
			y=mine[1]
			for i in range(-1,2):
				for j in range(-1,2):
					if x+i>=0 and x+i<w and y+j>=0 and y+j<h and (x+i,y+j)!=(x,y) and not((x+i,y+j) in mines):
						if not (x+i,y+j) in numbers:
							numbers[(x+i,y+j)]=1
						else:
							numbers[(x+i,y+j)]+=1
		return numbers

	def neighbors(self,x,y):
		w=self.w
		h=self.h
		adj=set()
		for i in range(-1,2):
			for j in range(-1,2):
				if x+i>=0 and x+i<w and y+j>=0 and y+j<h and (x+i,y+j)!=(x,y):
					adj.add((x+i,y+j))
		return adj

	def effective_neighbors(self,x,y):
		return {n for n in self.neighbors(x,y) if (not n in self.uncovered) and (not n in self.probed)}

	# def effective_label(self,x,y):
	# 	l=0
	# 	if (x,y) in numbers:
	# 		l=self.numbers[(x,y)]-len({n for n in self.neighbors(x,y) if n in self.probed})
	# 	return l
	def effective_label(self,x,y):
		return self.numbers[(x,y)]-len({n for n in self.neighbors(x,y) if n in self.probed}) if (x,y) in self.numbers else 0

	def set_mines(self,mines):
		self.mines=mines
		self.m=len(mines)
		self.numbers=self.populate()

	#horrible code to display grid with numbers on the top and side for easier debugging
	def print_configuration(self):
		grid=""
		for r in range(len(str(self.w-1))):
			grid+=(" "*(len(str(self.h-1))+2))+"".join(map(lambda x:str(x)[r] if r<len(str(x)) else " ",[i for i in range(self.w)]))+"\n"
		grid+=(" "*(len(str(self.h-1))+1))+"┏"+"━"*(self.w)+"┓\n"

		for j in range(self.h):
			grid+=str(j)+' '*(len(str(self.h-1))-len(str(j)))+" ┃"
			for i in range(self.w):
				if (i,j) in self.mines:
					grid+="x"
				elif (i,j) in self.numbers:
					grid+=str(self.numbers[(i,j)])
				else:
					grid+="‧"
			grid+="┃\n"
		grid+=(" "*(len(str(self.h-1))+1))+"┗"+"━"*(self.w)+"┛\n"
		print(grid)


	def show_progress(self):
		grid=""
		for r in range(len(str(self.w-1))):
			grid+=(" "*(len(str(self.h-1))+2))+"".join(map(lambda x:str(x)[r] if r<len(str(x)) else " ",[i for i in range(self.w)]))+"\n"
		grid+=(" "*(len(str(self.h-1))+1))+"┏"+"━"*(self.w)+"┓\n"

		for j in range(self.h):
			grid+=str(j)+' '*(len(str(self.h-1))-len(str(j)))+" ┃"
			for i in range(self.w):
				if (i,j) in self.uncovered:
					if (i,j) in self.numbers:
						grid+=str(self.numbers[(i,j)])
					else:
						grid+="‧"
				elif (i,j) in self.probed:
					grid+="⚑"
				else:
					grid+="#"
			grid+="┃\n"
		grid+=(" "*(len(str(self.h-1))+1))+"┗"+"━"*(self.w)+"┛\n"
		print(grid)


	def play(self):
		print("Instrucciones para jugar:")
		print("Para descubrir una casilla: D x,y")
		print("Para marcar una posible mina (poner una bandera) M x,y")
		print("Para desmarcar una bandera UM x,y")
		while self.probed!=self.mines:
			self.show_progress()
			move=input("Ingresa tu movimiento:\n")
			if move=="exit":
				return
			coor=tuple(map(int,move.split(" ")[1].split(",")))
			if move.split(" ")[0]=="D":
				if coor in self.mines: 
					print("MINA!")
					return
				else:
					if coor not in self.numbers:
						prev=set()
						q={coor}
						while prev!=q:
							prev=q.copy()
							for sq in prev:
								q|={n for n in self.effective_neighbors(sq[0],sq[1]) if n not in self.numbers}
						for sq in q.copy():
							q|=self.effective_neighbors(sq[0],sq[1])
						self.uncovered|=q
					else:
						self.uncovered.add(coor)
			elif move.split(" ")[0]=="M":
				if (self.m>0):
					self.probed.add(coor)
					self.m-=1
			elif move.split(" ")[0]=="UM":
				if coor in self.probed:
					self.probed.remove(coor)
					self.m+=1
			else:
				print("Error interpretando texto ingresado, intenta de nuevo")
		self.show_progress()
		print("Felicidades! Has ganado!")

	def uncovered_squares(self):
		return {(i,j) for i in range(self.w) for j in range(self.h) if (i,j) not in self.probed and (i,j) not in self.uncovered}

	# def clauses(self):
	# 	s=[]
	# 	for c in self.uncovered:
	# 		(x,y)=c
	# 		combinations=list(itertools.combinations(self.effective_neighbors(x,y),self.effective_label(x,y)))
	# 		for c in combinations:
	# 			clause=[]
	# 			c=set(c)
	# 			for n in c:
	# 				clause.append("~M"+str(n[0])+","+str(n[1]))
	# 			for n in self.effective_neighbors(x,y)-c:
	# 				s.append(clause[:]+["~M"+str(n[0])+","+str(n[1])])
	# 		last=["M"+str(n[0])+","+str(n[1]) for n in self.effective_neighbors(x,y)]
	# 		s.append(last)
	# 	return s

	def square_clauses(self,x,y):
		k=self.effective_label(x,y)
		en=self.effective_neighbors(x,y)
		s=set()
		if k==0:
			s|={frozenset(["~M"+str(coor[0])+","+str(coor[1])]) for coor in en}
		if len(en)==k:
			s|={frozenset(["M"+str(coor[0])+","+str(coor[1])]) for coor in en}
		else:
			l=list(map(set,itertools.combinations(en,len(en)-k+1)))
			u=list(map(set,itertools.combinations(en,k+1)))
			#s=[{"M"+str(coor[0])+","+str(coor[1]) for coor in c} for c in l]
			#s_=[{"~M"+str(coor[0])+","+str(coor[1]) for coor in c} for c in l]
			s|={frozenset(["M"+str(coor[0])+","+str(coor[1]) for coor in c]) for c in l}
			s|={frozenset(["~M"+str(coor[0])+","+str(coor[1]) for coor in c]) for c in u}
		return s

	def mine_clauses(self):
		m=len(self.mines)-len(self.probed)
		N=self.uncovered_squares()

		l=list(map(set,itertools.combinations(N,len(N)-m+1)))
		u=list(map(set,itertools.combinations(N,m+1)))
		s={frozenset(["M"+str(coor[0])+","+str(coor[1]) for coor in c]) for c in l}
		s_={frozenset(["~M"+str(coor[0])+","+str(coor[1]) for coor in c]) for c in u}
		return s|s_

	def clauses(self):
		s=set()
		for u in self.uncovered:
			s|=self.square_clauses(u[0],u[1])
		s|=self.mine_clauses()
		return s

	def suggest_next_move(self):
		cnf=self.clauses()
		unit_clauses=[list(c) for c in cnf if len(c)==1]
		if unit_clauses:
			for c in unit_clauses:
				if c[0][0]=='~':
					print("Explore",c[0][2:])
				else:
					print("Mark",c[0][1:],"as mine")
		else:
			flag=False
			for coor in self.uncovered_squares():
				if is_unsat(cnf|{frozenset(["M"+str(coor[0])+","+str(coor[1])])},'minesweeper.cnf','minesweeper_out.cnf'):
					print("Explore",",".join(map(str,coor)))
					return
				elif is_unsat(cnf|{frozenset(["~M"+str(coor[0])+","+str(coor[1])])},'minesweeper.cnf','minesweeper_out.cnf'):
					print("Mark",",".join(map(str,coor)),"as mine")
					return
			print("Explore random covered square")



def clauses_to_cnf(s):
	ls={l.replace('~',"") for c in s for l in c}
	ol=sorted(list(ls))
	enum=enumerate(ol,1)
	d={k:v for (v,k) in enum}
	cnf="p cnf {} {}\n".format(len(d),len(s))
	for c in s:
		row=""
		for l in c:
			if l[0]=='~':
				row+='-'+str(d[l[1:]])
			else:
				row+=str(d[l])
			row+=" "
		row+="0\n"
		cnf+=row
	for k in d.keys():
		cnf+="c {} -> {}\n".format(k,d[k])
	return cnf

def is_unsat(s,filename,outputname):
	with open(filename,"w") as f:
		print(len(s))
		for c in s:
			print(" or ".join(c))
		content=clauses_to_cnf(s)
		f.write(content)
		f.close()
		os.system('minisat {} {}'.format(filename,outputname))
		time.sleep(1)
		with open(outputname,"r") as out:
			if out.read().split('\n')[0] == 'UNSAT':
				return True
	return False









