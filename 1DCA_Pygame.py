import pygame
import numpy as np
import argparse

BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)



#FOR SMOOTH ANIMATION, SPEED MUST DIVIDE CELL SIZE
#OR ELSE THE GENERATION CAN'T BE STACKED EDGE TO EDGE

#THE USER WILL PROVIDE
#1.SCREEN DIMENSION (WIDTH , HEIGHT)
#2.CELL SIZE 
#3.AND CA RULES

#THE CALL to  MAKE GRID WILL HANDLE HOW MANY SQUARES WILL FIT
#GIVEN THE REQUESTED DIMENSIONS AND CELL SIZE
#THEREFORE THE DIMS AND CELL SIZE WILL BE STATIC

#@param - the current generations state
#@return - the new generations state
def updateState(state_ref,rule):
	#we don't want to change the previous generation
	#so we are passing a reference and then copying that value
	state = np.copy(state_ref)
	transition = np.zeros(state.size)
	for i in range(state.size):
		#left boundary case
		if i==0:
			stateStr = "0"+str(state[i])+str(state[i+1])
		#right boundary case
		elif i == state.size-1: 
			stateStr = str(state[i-1])+str(state[i])+"0"
		#normal case
		else:
			stateStr = ""+str(state[i-1])+str(state[i])+str(state[i+1])
			#convert the binary string to an integer
			#secondary argument calls for base 2 conversion
		transition[i] = int(stateStr,2)
		
	#since I am indexing the bit as if the lowest is the first state,
	# i need to reverse the rules when I read them in 
	#in conway the highest bit refers to the first state
	for j in range(transition.size-1):
		ind = int(transition[j])
		state[j]=rule[ind]
	return state


#@param - num_cells - the length of the row
#@param - initial_state - a binary vector of the initial state
#@param - rule - a binary vector representation of the rule
#@param - num_iters - how generations will be calculated
def generateAutomata(num_cells,initial_state,rule,num_iter):
	#create a matrix of num_iter rows by num_cells
	Cell_Generations = np.zeros((num_iter,num_cells),dtype=int)
	#set the default state
	Cell_Generations[0] = initial_state
	#run the generations
	for i in range(num_iter-1):
		Cell_Generations[i+1]=updateState(Cell_Generations[i],rule)
	return Cell_Generations



#A Cell is a subclass of Rect, that has a color an a state associated with it
#@param x - an integer
#@param y - an integer
#@param cell size - an integer
#@param state - {0|1}
class Cell(pygame.Rect):
	#class private variables
	__state = None
	__color = BLACK		 #determined by state
	
	def __init__(self,x0,y0,size,state):
		#Pygame.Rect( x ,y , width, height)
		pygame.Rect.__init__(self,x0,y0,size,size)
		self.__state = state

		stateColors = {0 : WHITE,
                1 : BLACK,
                2 : RED,
                3 : GREEN,
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
#@param - size  - the size of each cell
#@poaram - generation - A list with the state of each cell
#@return -  a (list) row of cells 
def make_cells(x_off,y_off,num_c,size,generation):
	rowCells = []
	for i in range(num_c):
		rowCells.append(Cell(x_off+(i*size),y_off+(0),size,generation[i]))
	print(len(rowCells),"row length")
	return rowCells

#@param - a list of list e.g. (a matrix) of cells objects
#@param - surface - where the cells will be drawn to
def draw_cells(cells,surface):
	for row in cells:
		for c in row:
			#pygame.draw.rect(surface, color, rect)
			pygame.draw.rect(surface,c.getColor(),c)


#@param squares - a list of list of cells
#@param  dx - horiz translation 
#@param  dy - vertical translation
def move_cells(cells,dx,dy):
	for row in cells:
		for c in row:
			#move_ip moves the cell(a rect) itself
			#as opposed to returning a new square with an offset
			#which is done by move()
			c.move_ip(dx,dy)


#Takes in the users arguments for screen dimensions and cell size
#Calculates how many cells will fit and how to center them with offsets
#note for 1D automaton vertical offset is irrelevant
#@param - width ..
#@param - height ..
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


def handleUserIn():

	parser = argparse.ArgumentParser()
	parser.add_argument("-w","--width",help="Screen Width",default=400)
	parser.add_argument("-l","--height",help="Screen Height",default=400)
	parser.add_argument("-r", "--rule", help="Rule in Decimal",default=26)
	parser.add_argument("-c", "--cell_size", help="Size of the cell",default=20)
	parser.add_argument("-s","--scroll_speed",help="how fast the animation scrolls",default=1)
	parser.add_argument("-i", "--iterations", help="The number of Iterations",default=1000)
	args = parser.parse_args()

	args.width = int(args.width)
	args.height = int(args.height)
	args.cell_size = int(args.cell_size)
	args.scroll_speed = int(args.scroll_speed)
	args.iterations = int(args.iterations)
	
	#gracefully exit, if users requests are not possible
	if not (args.cell_size % args.scroll_speed == 0):
		print("Invalid Input /nscroll_speed must divide cell_size")
		quit()

	#otherwise transform rule into vector form

	#this convoluted 1 liner takes the decimal -> to int -> to binary ->to string to clip off the 0b prefix
	ruleBinString = str(bin(int(args.rule)))[2:]
	#the rule binary string need to be 8 bits, so if pad the string with missing 0's
	mbits = 8-len(ruleBinString)
	for i in range(mbits):
		ruleBinString = "0"+ruleBinString
	ruleBinString = ruleBinString[::-1]
	ruleBinVec = np.zeros(8)
	for i in range(len(ruleBinString)):
		ruleBinVec[i] = int(ruleBinString[i])
	args.rule = ruleBinVec


	#finally the groomed user arguments
	print( "Screen Dimensions {} x {}\nRule {}\nCell Size {}\nScroll Speed {}\nNumber of Iterations {}".format(
			args.width,
			args.height,
		    args.rule,
		    args.cell_size,
		    args.scroll_speed,
		    args.iterations
	    ))
	return (args.width,args.height,args.rule,args.cell_size,args.scroll_speed,args.iterations)




def main_loop():
	
	(screen_width,screen_height,rule,cell_size,scroll_speed,iters) = handleUserIn()
	(num_columns,num_rows,h_offset,v_offset) = makeGrid(screen_width,screen_height,cell_size)

	screen = pygame.display.set_mode((screen_width,screen_height))
	pygame.display.set_caption('Cellular Automata w/ Pygame')

	#generate initial state - here it is just the middle value filled in
	initial_state = []
	for i in range(num_columns):
		if (i==int(num_columns//2)):
			initial_state.append(1)
		else:
			initial_state.append(0)

	#solve the forward CA problem for iters
	generation_matrix = generateAutomata(num_columns,initial_state,rule,iters)
	#hold Cell Objects
	cell_matrix = []
	
	spawn_timer = 0	#decide when to spawn new generation
	gen = 0 #keep track of the current generation

	while 1:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()

		if (gen < iters):
		#drawing
			screen.fill(WHITE)
			draw_cells(cell_matrix,screen)
			pygame.display.update()
			clock.tick(120)
		#logic

			#spawn new generation
			if (spawn_timer % cell_size == 0):
				#spawn the cells below the screen by the length of one cell
				cell_matrix.append(make_cells(0,screen_height+cell_size,num_columns,cell_size,generation_matrix[gen]))
				gen+=1
			#kill generations outside the view window
			if (cell_matrix[0][0].y < 0):
				cell_matrix = cell_matrix[1::]


			spawn_timer += scroll_speed
			move_cells(cell_matrix,0,-scroll_speed)	#negative speed , because we want to float up

			#display the state of the system
			print("active generations",len(cell_matrix))



#PYGAME UTILITIES
pygame.init()
clock = pygame.time.Clock()
main_loop()
#deinitialize pygame

pygame.quit()
#exit the program
quit()
