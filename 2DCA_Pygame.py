import numpy as np
import pygame
import argparse
import pickle 	#pickle allows me to save python objects
import timeit

BLACK = (0,0,0)
WHITE = (255,255,255)


##############
#NOTES ON CA'S
##############

# a orthogonal neighborhood , is a Von Neumann neighborhood - 5 neighbors
# orthogonal and diagnol neighborhood, is a Moore neighborhood - 9 neighbors
# neighborhoods can also be defined with a range, standard range is 1

#conways game of life is a Moore neighborhood, range 1, with rule 2,3/3
#rule 2,3/3 means Live if 2 or 3 neighbors, generate if 3 neighbors, die otherwise

################################
#TODO'S / NEW FEATURES
################################

#TODO FIGURE OUT HOW USE PICKLE EFFICIENTLY TO 
#AVOID RECALCULATING CELLULAR AUTOMATA
#THIS CALCULATION IS A HUGE OVERHEAD IF THE BOARD IS VERY LARGE

#TODO ADD COLORING OPTIONS TO MAKE THE VISUALS MORE PRETTY
#INCLUDING BACKGROUND, ALIVE AND, DISTANCE FROM ORIGIN GRADIENT

##############################
#CELLULAR AUTOMATA CALCULATIONS
##############################

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

#takes a matrix of cells respresented numerically and calculates what each cell will be in the next generation
#@param cells -  1D-Vector representing the board
#@param num_rows - of CA board
#@param num_cols - of CA board
#@param rule - a 2- tuple of list of sustain states, and list generative states, based on quantity of live neighbors
#@return - the next generation of the cells
def update_state(cells,num_rows,num_columns,rule):
	(sus_state,gen_state) = rule
	new_cells = np.zeros(len(cells))
	for i in range(len(cells)):
		state = cells[i]	
		#find the state of the neighborhood
		neighbors = get_neighbors(num_rows,num_columns,i)
		live_neighbor_count = 0
		for n in neighbors:
			live_neighbor_count += cells[n]	

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


#@param num_rows - of CA board
#@param num_cols - of CA board
#@param rule - a 2- tuple of list of sustain states, and list generative states
#@param iterations - number of generations to solve for
#@param initial_state - a 1D array representing the 2D board of cells represented as a binary matrix
#@returns a 2D array of cells represented numerically indexed by generation
def generate_automata(num_rows,num_columns,rule,iterations,initial_state):
	generations = [[]]
	generations[0] = initial_state
	for i in range(iterations):
		new_generation = update_state(generations[i],num_rows,num_columns,rule)
		generations.append(new_generation)
	return generations


################################
#GUI 
################################

#A Cell is a subclass of Rect, that has a color an a state associated with it
#@param x - an integer location
#@param y - an integer location
#@param cell size - an integer
#@param state - {0|1} : {alive|dead}
class Cell(pygame.Rect):
	__state = None
	__color = BLACK	

	def __init__(self,x0,y0,size,state):
		#Pygame.Rect( x ,y , width, height)
		pygame.Rect.__init__(self,x0,y0,size,size)
		self.__state = state

		stateColors = {0 : WHITE,
               		   1 : BLACK,
		}
		self.__color = stateColors[state]

	def setState(self,new_state):
		self.__state = s0
	def getState(self):
		return self.__state
	def getColor(self):
		return self.__color


#@param - x_off - the x offset for centered display
#@param - y_off - the y offset for centered display
#@param - num_c - the number of cells per row
#@param - num_r - the number of cells per column
#@param - size  - the size of each cell
#@poaram - generation - A list with the state of each cell
#@return -  a (list) row of Cell Objects 
def make_cells(x_off,y_off,num_columns,num_rows,size,generation):
	(w,h) = (num_columns,num_rows)
	new_cells = []
	#iterate through the 1D array 
	for i in range(w*h):
		x = (i%h)*size
		y = (i//w)*size
		new_cells.append(Cell(x_off+x,y_off+y,size,generation[i]))
	return new_cells
#draws the given cells to the surface provided
#@param - cells - a 1D list of Cell objects that represents a 2D array of cells (the board)
#@param - surface - where the cells will be drawn to
def draw_cells(cells,surface):
	for c in cells:
		#pygame.draw.rect(surface, color, rect)
		pygame.draw.rect(surface,c.getColor(),c)


#Takes in the users arguments for screen dimensions and cell size
#Calculates how many cells will fit and how to center them with offsets
#@param - width of requested screen
#@param - height of requestd  screen
#@param - size - size of cell
#@return - a tuple of the grid (number of horizontal cells, vertical cells, horizontal offset, vertical offset)
def makeGrid(width,height,size):
	
	h_remainder = width%size
	if (h_remainder==0):
		num_h = int(width/size)
	else:
		num_h = width//size
	
	v_remainder = height%size
	if (v_remainder==0):
		num_v = int(height/size)
	else:
		num_v = height//size

	#padding if fit is not perfect
	h_offset = h_remainder//2
	v_offset = v_remainder//2

	print("Nums Rows ", num_v,"\nNum Columns ",num_h)
	return (num_h,num_v,h_offset,v_offset)

####################
#INITIAL CONDITIONS
#####################
def randomInit(num_rows,num_columns):
	return np.random.randint(0,2,(num_rows*num_columns))

def crossInit(num_rows,num_columns):
	initial = np.zeros(num_rows*num_columns)
	mid_c = (num_columns//2)
	mid_r = (num_rows//2)
	for i in range(num_columns):
		ind = (mid_r*num_columns) + i
		initial[ind]=1

	for j in range(num_rows):
		ind = mid_c + (j*num_columns)
		initial[ind]=1
	return initial

################
#USER OPTIONS
################

def handleUserIn():

	parser = argparse.ArgumentParser()
	parser.add_argument("-w","--width",help="Screen Width",default=400)
	parser.add_argument("-l","--height",help="Screen Height",default=400)
	#parser.add_argument("-r", "--rule", help="Rule in Decimal",default=26)
	parser.add_argument("-c", "--cell_size", help="Size of the cell",default=10)
	parser.add_argument("-p","--period",help="how fast the animatin occurs",default=15)
	parser.add_argument("-i", "--iterations", help="The number of Iterations",default=500)
	args = parser.parse_args()

	args.width = int(args.width)
	args.height = int(args.height)
	args.cell_size = int(args.cell_size)
	args.period = int(args.period)
	args.iterations = int(args.iterations)

	#finally the groomed user arguments
	print( "Screen Dimensions {} x {}\nCell Size {}\nPeriod {}\nNumber of Iterations {}".format(
			args.width,
			args.height,
		    args.cell_size,
		    args.period,
		    args.iterations
	    ))
	return (args.width,args.height,args.cell_size,args.period,args.iterations)


def main_loop():
	(screen_width,screen_height,cell_size,period,iters) = handleUserIn()

	#rule construction 
	sus = [2,3]
	gen = [3]
	rule = (sus,gen)

	(num_rows,num_columns,h_off,v_off) = makeGrid(screen_width,screen_height,cell_size)
	print(num_rows,num_columns)

	screen = pygame.display.set_mode((screen_width,screen_height))
	pygame.display.set_caption('2D Cellular Automata w/ Pygame')

	#Initial condition
	#initial = randomInit(num_rows,num_columns)
	initial = crossInit(num_rows,num_columns)


	match = False
	params = (num_rows,num_columns,rule,iters,initial)
	#check if this requested simulation has already been calculated
	'''
	CA_LIST = pickle.load(open("calculated_2d_automata.p","wb"))
	for CA in CA_LIST:
		ca_i = (params_i,cam_i)
		if (params_i == params):
			print("A match has been found")
	'''

	#solve the forward problem
	start = timeit.default_timer()
	generation_matrix = generate_automata(num_rows,num_columns,rule,iters,initial)
	stop1 = timeit.default_timer()
	print('Compute Time For the Forward Problem: ', stop1 - start)  

	#save the forward problem as a 2-tupe containing a tuple of the life inputs, and the resulting matrix
	ca_instance = ((num_rows,num_columns,rule,iters,initial), generation_matrix)

	pickle.dump(ca_instance,open("calculated_2d_automata.p","wb"))


	#construct all Cell Objects based on solution to the forward problem
	cell_matrix = []	# a list of   generations of Cells
	for gen in generation_matrix:
		cell_matrix.append(make_cells(h_off,v_off,num_columns,num_rows,cell_size,gen))

	stop2 = timeit.default_timer()
	print('Compute Time Construction of Cells: ', stop2 - stop1)  

	

	gen = 0 #keep track of the current generation
	tick = 0

	while 1:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()

		if (gen < iters):
			#drawing
			screen.fill(WHITE)
			draw_cells(cell_matrix[gen],screen)
			pygame.display.update()
			clock.tick(60)
			#logic
			if (tick%period==0):
				gen+=1
			tick += 1 



#PYGAME UTILITIES
pygame.init()
clock = pygame.time.Clock()
main_loop()
#deinitialize pygame
pygame.quit()
#exit the program
quit()



	



