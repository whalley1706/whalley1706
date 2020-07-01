
# coding: utf-8

# # Encapsulation

# OK so what do we want our __MODULE__ and its classes to be able to do:
#     - INTIIALISE BASED ON A NUMBER OF PARENTS ALONE
#     - GENERATE CHILDREN BASED ON AVERAGE CHILDREN PER PARENT, WITH VARIABLE STATS METHODS
#     - APPLY THE ABOVE ITERATIVELY
#     - GENERATE CORRELATED DATA FROM PRE-EXISTING DATA
#     - CLUSTERING DATASETS

# In[1]:


from abc import ABC,abstractmethod # for abstract classes and methods
import numpy as np # numpy arrays are in matrices are like in matlab
import pandas as pd # pandas dataframes like Tables in Matlab
#import scipy.stats as stats # need this for distributions
import matplotlib.pyplot as plt #for graphs 
import math
import random

random.seed( 10 ) # this should be a property of the class, no?


# In[2]:


print(random.random) # so its repeatable.


# In[3]:


#nest_counter = 0
class Hpattern:
    def __init__(self,mean_no_of_children,dist):
        self.Mean_no_of_children = mean_no_of_children
        self.Dist = dist
    
class fakeHeirarchy_abstract(ABC):

    def __init__(self, no_of_topLevelParents,mean_no_of_children, dist):
        self.No_of_topLevelParents = no_of_topLevelParents #create top level parents
        self.Mean_no_of_children = mean_no_of_children
        # default seed value. User can overwrite but don't think matters at creation sufficiently
        self._seed = 123
        random.seed(self._seed) # get and set required?
    def generateChildren(self,Parents,mean_no_of_children,dist):
        pass # one level a time
    def heirarchy(self,toplevelParents,levels,Hpattern):
        pass #check levels <= Hpattern, issue a warn if so. Init Hpattern if not entered
    
    


# In[4]:


class fakeHeirarchy_concrete(fakeHeirarchy_abstract):
    
    def __init__(self, no_of_topLevelParents, mean_no_of_children=3,dist='exp'):
        
        fakeHeirarchy_abstract.__init__(self, no_of_topLevelParents,mean_no_of_children,dist)
        #super().__init__(self, no_of_topLevelParents)
        
        
        def extractAfter(input,amount): #like the matlab equivalent or =RIGHT excel
            return input[-amount:] #neg index means start at the end. Colon means go to the end.

        order = np.ceil(math.log(no_of_topLevelParents,10)).astype(int)
        datum = np.power(10,order+1)
        #ensure num is atleast 10x largest num simon needs (hence order check)
        a = datum+np.arange(1,no_of_topLevelParents+1) # if they index at 1
        b = 'x'*no_of_topLevelParents

        concat_func = lambda x,y: x + "|" + extractAfter(str(y),order+1) # piped as Simon likes em easily retrived this way

        L = list(map(concat_func,b,a)) # list the map function
                
        if dist == 'exp':
            no_of_kids = np.floor(np.random.exponential(mean_no_of_children,no_of_topLevelParents))    
        elif dist == 'lognormal':
            no_of_kids = np.floor(np.random.lognormal(mean_no_of_children, no_of_topLevelParents)) 
        else:
            no_of_kids = np.floor(np.random.uniform(mean_no_of_children,no_of_topLevelParents))
        
        no_of_kids = no_of_kids.astype(int)
        #data =  pd.DataFrame(data=[L,no_of_kids],columns=list(["TopLevelParents","AboutToSpawn..."]))
        data =  pd.DataFrame(no_of_kids,L,columns=list(["AboutToSpawn..."]))#improve as per above
        self.DefaultParents = L
        self.Top_Level_Info = data
        self.Top_Level_Primitives = data[data['AboutToSpawn...']==0] #capture who doesn't have children at each heiracy level 
        self._nest_counter = 0
        #self.defaultkids?
    def generateChildren(self,parents='default',exact_kids=_,mean_no_of_children=3,dist='exp'):
        
        if parents=='default':
            L = self.DefaultParents
        else:
            L = parents
        no_of_parents = len(L)
        if exact_kids!=_ and len(exact_kids)==len(L):
            no_of_kids = exact_kids
            print('Parents & Children match successfully.')
        elif exact_kids!=_:
            #print('Parents & Children do not match in length.')
            raise Exception("Parents & Children do not match in length.")
        elif exact_kids==_ and self._nest_counter ==0:
            exact_kids = self.Top_Level_Info['AboutToSpawn...']
       
        
        
    
        no_of_kids = np.floor(np.random.exponential(mean_no_of_children,no_of_parents))
        no_of_kids = no_of_kids.astype(int)
        
        newParents = np.repeat(L,no_of_kids) #repeat the parents to the the new size to use in a table as ref for children
        data =  pd.DataFrame(no_of_kids,L,columns=list(["AboutToSpawn..."]))
        
        idx = np.arange(no_of_parents) + 1# if they index at 1
        no_of_siblings = np.repeat(no_of_kids-1,no_of_kids)
        no_of_siblings = no_of_siblings[no_of_siblings>-1]
        uidx = np.unique(newParents,return_index=True)
        spawners = no_of_kids[no_of_kids>0]
        L_spawners = data[no_of_kids>0]

        u_precede = spawners-1 # we do this to ensure counting up sequentially per parent,starting at 1 each time
        u_precede = np.roll(u_precede,1)
        u_precede[0]=0 # special cases. this one won't apply to uidx either (first element)
        u_precede[-1]=0
        uidx=uidx[1].astype(int) # just want the indices 
        
        create_suffix = np.ones(len(newParents))
        #np.pop(u_precede) #listsonly
        #np.pop(uidx)
        def arrayPop(y):
           #last, y = y[-1], y[:-1] #this would be full opo functionality
           #return last,y
            y =  y[1:] #technically reverse pop. ignore popped val (first not last)
            return y
        u_precede = arrayPop(u_precede)
        uidx = arrayPop(np.transpose(uidx))

        create_suffix[uidx] = -(u_precede)
        
        create_suffix = np.cumsum(create_suffix) #so it should start counting at 1 each Parent
        

        concat_func = lambda x,y: x + "|" + str(y)

        children = list(map(concat_func,newParents,create_suffix)) # if we used 'idx' instead of 'create_suffix' it would count 1:end without starting again at 1 for each parent
        self._nest_counter = self._nest_counter+1
        dataout=[newParents,no_of_siblings,children]
        dataout=np.transpose(dataout)
        a = ['newParents','no_of_sibling','children']
        b =str(self._nest_counter)*len(a)
        concat_func = lambda x,y: x + "|" + (y) # piped as Simon likes em easily retrived this way

        headings = list(map(concat_func,b,a)) # list the map function
        self.DefaultParents = children
        self.output = pd.DataFrame(data=dataout,columns=headings)
        
    def heirarchy(self,toplevelParents,levels,Hpattern):
        #check levels <= Hpattern, issue a warn if so. Init Hpattern if not entered
        pass
        #loop through heirarchy - for i = 1:10


# # Ok, lets now quickly test our class

# These commands force package to reimport if we've updated it. Make more sense when we run tests in separate scripts
# https://medium.com/@chrieke/jupyter-tips-and-tricks-994fdddb2057

# In[5]:


get_ipython().run_line_magic('load_ext', 'autoreload')
get_ipython().run_line_magic('autoreload', '2')


# In[6]:


obj = fakeHeirarchy_concrete(10)
print(obj.Top_Level_Info)
print(obj.Top_Level_Primitives)


# In[7]:


# Driver code 
print( issubclass(fakeHeirarchy_concrete, fakeHeirarchy_abstract)) 
print( isinstance(obj, fakeHeirarchy_abstract)) 


# In[8]:


obj.generateChildren()
print(obj.output)


# Lets go again

# In[9]:


obj.generateChildren()
print(obj.output)


# In[10]:


get_ipython().run_line_magic('debug', '')

