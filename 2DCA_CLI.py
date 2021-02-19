import numpy as np

# a orthogonal neighborhood , is a Von Neumann neighborhood - 5 neighbors

# orthogonal and diagnol neighborhood, is a Moore neighborhood - 9 neighbors

# neighborhoods can also be defined with a range, standard range is 1

#conways game of life is a Moore neighborhood, range 1, with rule 2,3/3

#rule 2,3/3 means Live if 2 or 3 neighbors, generate if 3 neighbors, die otherwise

'''
How Data is Structured
I would like to avoid a 3d dimensional array for obvious reasons, I will abstract the board into a unidimensional array,
and store an array of these arrays indexed by time

an index I has the potential following neighbors 
 	(i-1)	left			(i+1)	right
 	(i-3)	top right		(i+3)	bot left
 	(i-4)	top				(i+4)	bot
 	(i-5)	top left		(i+5)	bot right
 
'''
#@param - num_rows - of CA board
#@param - num_cols - of CA board
#@param - index - an index into the unidimensional board array in range (0,num_rows*num_cols)
#@return - a list of the neighboring indexes
def get_neighbors(num_rows,num_columns,index):
	(w,h,i) = (num_columns,num_rows,index)
	neighbors = []
	#N
	if not (i // w ==0):
		neighbors.append(i-w)
	#NE
	if not (i // w == 0) and not (i % w == w-1) :
		neighbors.append(i-w+1)
	#E
	if not (i % w == w-1):
		neighbors.append(i+1)
	#SE
	if not (i // w == h-1) and not (i % w == w-1):
		neighbors.append(i+w+1)
	#S
	if not (i // w == h-1):
		neighbors.append(i+w)

	#SW
	if not (i // w == h-1) and not (i % w == 0):
		neighbors.append(i+w-1)
	#W
	if not (i % w == 0):
		neighbors.append(i-1)
	#NW
	if not (i // w == 0) and not (i % w == 0):
		neighbors.append(i-w-1)

	return neighbors

#takes a matrix of cells and calculates what each cell will be in the next generation
#based off of the rule provided
#@param cells -  1D-Vector representing the board
#@param num_rows - of CA board
#@param num_cols - of CA board
#@param rule - a 2- tuple of list of sustain states, and list generative states, based
#on quantity of live neighbors
#@return - the next generation of the cells
def update_state(cells,num_rows,num_columns,rule):
	(sus_state,gen_state) = rule
	new_cells = np.zeros(len(cells))
	for i in range(len(cells)):
		state = cells[i]	#alive or dead
		#find the state of the neighborhood
		neighbors = get_neighbors(num_rows,num_columns,i)
		live_neighbor_count = 0
		for n in neighbors:
			live_neighbor_count += cells[n]	# state is 0 or 1, adding sumin the values is quick

		new_state = 0 #dead
		#if alive and neighbor count is a sustainable state, remain alive
		if (state == 1 and sus_state.count(live_neighbor_count) > 0 ):
			new_state = 1
		#if dead and neighbor count is a generative state , become alive
		elif (state == 0 and gen_state.count(live_neighbor_count)>0):
			new_state = 1
		#stay or become dead
		else:
			new_state = 0
		new_cells[i] = new_state
	return new_cells

#returns a 2D array of cells indexed by generation
def generate_automata(num_rows,num_columns,rule,iterations,initial_state):
	generations = [[]]
	generations[0] = initial_state
	for i in range(iterations):
		new_generation = update_state(generations[i],num_rows,num_columns,rule)
		generations.append(new_generation)
	return generations


#Board Dimensions
num_rows = 9
num_columns = 9

iters = 5
sus = [2,3]
gen = [3]
rule = (sus,gen)

#initial state row of 3 cells
initial = np.zeros((num_rows*num_columns))
mid = (num_rows*num_columns)//2
initial[mid-1]=1 
initial[mid]=1
initial[mid+1]=1



gens = generate_automata(num_rows,num_columns,rule,iters,initial)
for g in gens:
	print(np.reshape(g,(num_rows,num_columns)))

	



