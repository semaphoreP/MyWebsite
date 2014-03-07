import numpy as np
import matplotlib.pylab as plt
import time
from threading import Thread, Lock, Condition, Semaphore

###################
### Ay120 Lab 3 ###
# Data Iteration  #
### Jason Wang  ###
###################

fig = plt.figure()
data = np.zeros([200,300])

#### Best way to iterate over data? ####

### Simple for loop over x and y ###
# note that numpy arrays index y first 
start = time.time()
for y in range(np.size(data,0)): #iterate over y which is the '0th' dimension
	for x in range(np.size(data,1)): #iterate over x which is the '1st' dimension
		data[y,x] = x**2+y**2 # manipulate data
print "For loop (y's then x's): %f" %(time.time()-start)

#clear the data
data[:,:] = 0 #this sets all data points to zero

#let's try doing x first, be careful with indicies
start = time.time()
for x in range(np.size(data,1)): 
	for y in range(np.size(data,0)):
		data[y,x] = x**2+y**2
print "For loop (x's then y's): %f" %(time.time()-start)	

### Numpy operations are way faster than for loops, use them for speed! ###

#need to index into your array? numpy can create maps of x and y index
#be careful with meshgrid in that it takes in the x indicies before the y indicies
x,y = np.meshgrid(np.arange(np.size(data,1)), np.arange(np.size(data,0)))

ax1 = fig.add_subplot(221)
ax2 = fig.add_subplot(222)
ax3 = fig.add_subplot(223)
ax4 = fig.add_subplot(224)

#here's what the x and y maps look like
ax1.imshow(x)
ax1.set_title("x map")
ax2.imshow(y)
ax2.set_title("y map")

#let's compare how fast it is for numpy to loop throuhgh all the data
start = time.time()
data = x**2 + y **2
print "Using a numpy operation: %f" %(time.time()-start)

ax3.imshow(data)

# Here are some ways to access indicies in numpy 
data2 = np.zeros([200,300])

#you can use your x/y maps and numpy.where to modify only certian regions
valid = np.where((x**2+y**2 > 1000) & (x**2+y**2 < 10000))
data2[valid] = 1

#access rows and columns in numpy
data2[150,:] = 1 #sets all x values with y=150 equal to 1
data2[:, 200:225] = 1 #sets all y values with x=[220,225) equal to 1

ax4.imshow(data2)

plt.tight_layout()
plt.show()

#want to iterate over two lists?, use numpy.broadcase to iterate over both at the same time
list1 = np.arange(20)
list2 = np.arange(20,40)

#now we have a list of tuples with each tuple having an element from each original list
doublelist = list(np.broadcast(list1,list2)) 

for tuple in doublelist:
	print tuple


### If you really have to do a for loop, which is faster? ###
### Here two different methods will race
### Iter1 will not use any numpy commands and just loop over the indicies manually
### Iter2 will use a numpy interator to go through the valus
### Iter1 starts from the end and works backwards to the start, and iter2 starts from the beginning
### The both stop when they hit each other
plt.figure()
data = np.zeros([200,300])
plt.imshow(data)
plt.show()

wait_sema = Semaphore(0)

class Iter1(Thread):
	def __init__(self, arr):
		Thread.__init__(self)
		self.dat = arr
		self.w1 = np.size(self.dat,0)
		self.w2 = np.size(self.dat,1)
		
	def run(self):
		for i in range(self.w1)[::-1]:
			for j in range(self.w2)[::-1]:
				if (self.dat[i,j] != 0):
					wait_sema.release()
					return
				else:
					self.dat[i,j] = 1
		wait_sema.release()
		
class Iter2(Thread):
	def __init__(self, arr):
		Thread.__init__(self)
		self.dat = arr
		self.iter = np.ndenumerate(self.dat)

	def run(self):
		for (i,j), value in self.iter:
			if value != 0:
				wait_sema.release()
				return
			self.dat[i,j] = 2
		wait_sema.release()
		
t1 = Iter1(data)
t2 = Iter2(data)
t1.start()
t2.start()
wait_sema.acquire()
wait_sema.acquire()

img = plt.imshow(data,vmin=0,vmax=2)
plt.colorbar()
plt.show()
