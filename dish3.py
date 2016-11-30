import random
import heapq



class Dish:
    def __init__(self, ticker, width=100, height=100):
        self.ticker, self.width, self.height = ticker, width, height
        self.ticker.dish = self
        self.fieldList = {}  #slownik laczacy nazwy pol z obiektem pole
        for x in range(1, self.width+1):
            for y in range(1, self.height+1):
                self.add_field(x,y)
    def __str__(self):
        i = 0
        out = ""
        for key in self.fieldList:
                out = out + "(" + self.fieldList[key].__str__() +")"
                i += 1
        return out
        
    def add_field(self,x,y):
        key = (x,y)
        newField = Field(self, key)
        self.fieldList[key] = newField

    def get_fields(self, key):
        return self.fieldList[key]

    def get_neighbors(self, field):
        list_of_neighbors = []
        list_of_keys = []
        list_of_keys = [(x2, y2) for x2 in range(field.key[0] - 1, field.key[0] + 2)
                             for y2 in range(field.key[1] - 1, field.key[1] + 2)
                             if (0 < field.key[0] <= self.width and
                                                  0 < field.key[1] <= self.height and
                                                  (field.key[0] != x2 or field.key[1] != y2) and
                                                  (0 < x2 <= self.width) and
                                                  (0 < y2 <= self.height))]
                                                
        for key in list_of_keys:
            list_of_neighbors.append(self.fieldList[key])
        return list_of_neighbors 
        

class Field:
    def __init__(self, dish, key):
        self.dish, self.key = dish, key
        self.content = []
    
    def __str__(self):
        a= " "
        for i in self.content:
            a += i.__str__() + " "
        return a
        
    def index(self, element):
        return self.content.index(element)
    
    def neighbors(self):
        return self.dish.get_neighbors(self)
    
    def random_neigh(self):
        return random.choice(self.neighbors())
    
    def push(self, obj):
        self.content.append(obj)
        obj.field = self
        try:
            under = self.content[-2]
            under_class = under.__class__.__name__
            if obj.interactions.has_key(under_class) == True:
                obj.interactions[under_class](under)
            elif under.interactions.has_key(obj.__class__.__name__) == True:
                under.interactions[obj.__class__.__name__](obj)
        except IndexError:
            pass
    
    def remove(self, obj):
        if obj in self.content:
            self.content.remove(obj)
    
class On_field(object):
    def my_index(self):
        i = self.field.index(self)
        return int(i)    
        
    def die(self):
        if self.field != None:
            self.field.remove(self)
        self.dead = True
    
    def __str__(self):
        return self.__class__.__name__ + str(self.numerek)
    

class Bacteria(On_field):
    
    def live(self):
        print self.numerek
        if self.dead != True:
            r=random.random()
            res = 0
            if self.sick_actions != None:
                a = self.sick_actions
            else:
                a = self.actions
                if res == 0:                
                    for scheme in a:
                        if scheme[0] >= r:
                            f = scheme[1]
                            f()
                            res += 1
                        else:
                            print("nothing interesting")
            self.end_move()

    def end_move(self):
        self.field.dish.ticker.schedule_turn(self.cycle, self.live)
        
    def divide(self, f= None):
        if self.vir_vis == None:
            c = self.__class__(self.numerek+0.1)
            f = self.field
            f.push(c)
            f.dish.ticker.schedule_turn(c.cycle, c.live)
            self.p2 = 0.1
            print("divided!")
                    
    def eat_a(self, anti):
        self.a_count += 1
        anti = self.field.content[self.my_index()-1]
        anti.die()
        print("I ate antibiotic, bleee :(")

    def get_sick(self, vir):
        vir.infect(self)
    
    def cure(self):
        self.sick_actions = None
        
    def count(self):
        self.vir.counting += 1
        if self.vir.counting == 5:
            self.field = self.vir.field
            self.vir.explode()
            self.die()
    
    def move(self, why=None):
        if self.vir_vis == None:
            f = self.field.random_neigh()
            self.field.remove(self)
            f.push(self)
        
class Bac_Mun(Bacteria):
    cycle = 1
    
    def __init__(self, numerek):
        self.numerek = numerek
        self.field = None
        self.p2 = 0.2
        self.counter = 0
        self.dead = False
        self.a_count = 0
        self.n_count = 0
        self.vir_vis = None
        self.virus = None
        self.sick_actions = None
        self.actions=[[0.1, self.move], [self.p2, self.divide]]
        self.interactions = {"Antibiotic": self.eat_a, "Nourishment": self.eat_n, "Bac_Mun": self.jump}
        self.infected_act2 = [[1, self.count]]
                   
    def eat_n(self, n):
        self.n =+ 1
        if self.p2 < 1:
            self.p2 += 0.1
        mniam = self.field.content[self.my_index()-1]
        mniam.die()
        print("I ate foodz, yum yum :3")
        
    def jump(self, why):
        if self.my_index() > why.my_index():
            print self.counter
            if self.counter > 2: 
                self.die()
            else:
                self.counter += 1
                self.move() 

                        
class Bac_Meg(Bacteria):
    def __init__(self, numerek):
        self.numerek = numerek
        self.field = None
        self.dead = False
        self.sick_actions = None
        self.actions = [[0.01, self.move]]
        self.bac_eaten = 0
        self.a_count = 0
        self.infected_act = [[0.1, self.move], [0.4, self.cure]]
        self.infected_act2 = [[1, self.count]]
        self.cycle = 3
        self.virus = None
        self.vir_vis = None
        self.interactions = {"Antibiotic": self.eat_a, "Bac_Mun": self.eat_bac, "Bac_Meg": self.move, "Vir_Meg" : self.get_sick}
    
    def move(self, why=None):
        if self.vir_vis == None:
            list_of_neigh = self.field.neighbors()
            have_bac = []
            dont_have = []
            have = 0
            for f in list_of_neigh:
                for c in f.content:
                    if c.__class__.__name__ == "Bac_Mun":
                        have += 1
                if have != 0:
                    have_bac.append(f)
                else:
                    dont_have.append(f)
            r = random.randint(1, 3)
            if r > 1 and len(have_bac) != 0:
                f=random.choice(have_bac)
            else:
                f= random.choice(dont_have)                  
            self.field.remove(self)
            f.push(self)
            if self.dead == False:
                if self.vir_meg != None:
                    r = random.randint(1,10)
                    if r <= 4:
                        self.virus.capsyd()

    def eat_bac(self, bac):
        try:
            if self.field.content[self.my_index() + 1] == bac:                
                print("I ate bacteria")
                self.bac_eaten += 1
                if self.bac_eaten == 5:
                    self.divide()
                    self.bac_eaten = 0
                self.move()
        except IndexError:
            pass      
        
    def eat_a(self, anti):
        r = random.randint(1, 10)
        if r <= 5:
            self.a_count += 1
            anti.die()
            print("I ate antibiotic, bleee :(")

class Virus(On_field):
    def capsyd(self):
        new_vir = self.__class__(self.numerek+0.1)
        self.bac.field.push(new_vir)
        
class Vir_Meg(Virus):
    def __init__(self,numerek):
        self.numerek = numerek
        self.field = None
        self.bac = None
       # self.infected_act = [[0.1, Bac_Meg.move], [0.3, Bac_Meg.cure]]  nie umiem tego tak zrobic, aby przekazywac dobrze argumenty
        self.interactions = {"Bac_Meg" : self.infect}
               
    def infect(self, bac):
        print("i infect you!")
        if bac.virus == None:
            bac.sick_actions = bac.infected_act
            bac.virus = self
            self.field.remove(self)
    
class Vir_Vis(Virus):
    def __init__(self,numerek):
        self.numerek = numerek
        self.field = None
        self.bac = None
        self.interactions = {"Bac_Meg" : self.infect, "Bac_Mun": self.infect}    
                   
    def infect(self, bac):
        print("Vir_Vis infect you!")
        if bac.virus == None:
            bac.sick_actions = bac.infected_act2
            bac.virus = self
            self.field.remove(self)
    
    def explode(self):
        c = 0
        while c != 18:
            for n in self.field.neighbors():
                self.capsyd(n)
                c += 1   
            
class Food(On_field):
    interactions = {}
    dead = False
       
    def my_field(self, field):
        self.field = field
        
class Nourishment(Food):
    def __str__(self):
        return "n"       
         
class Antibiotic(Food):
    def __str__(self):
        return "a"

class Ticker:
    def __init__(self):
        self.ticks = 0
        self.schedule = []
        self.how_long = 1000
        self.dish = None
        
    def schedule_turn(self, when, action, l=[]):
        heapq.heappush(self.schedule, (self.ticks+when, action, l))

    def next_turn(self):
        now = heapq.heappop(self.schedule)
        self.ticks = now[0]
        action = now[1]
        l = now[2]
        action(*l)
        print(self.ticks)

    def start(self, how_long):
        self.how_long = how_long
        while self.ticks < how_long and len(self.schedule) != 0:
            self.next_turn()
        else:
            print("End of the simulation")

ticker = Ticker()
d = Dish(ticker, 10,10)
for key in d.fieldList:
    d.fieldList[key].push(Nourishment())        
for key in d.fieldList:
    d.fieldList[key].push(Antibiotic())

        
for i in range(1, 6):
    x = random.randint(1, d.width)
    y = random.randint(1, d.height)
    b = Bac_Mun(i)
    c = Bac_Meg(i)
    v = Vir_Meg(i)
    v2 = Vir_Vis(i)
    d.fieldList[(x,y)].push(b)
    d.fieldList[(x,y)].push(c)
    d.fieldList[(y,x)].push(v)  
    d.fieldList[(x,y)].push(v)
    d.fieldList[(x,y)].push(v2)
    
    ticker.schedule_turn(0, b.live)
    ticker.schedule_turn(0, c.live) 

pre = d.__str__() 
ticker.start(10)

for key in d.fieldList: #print infected bacteria
    for el in d.fieldList[key].content:
        if hasattr(el, "virus") or hasattr(el, "vir_vis"):
            if el.virus != None or el.vir_vis != None:
                print("I'm infected" + el.__str__())
print("\nDish before: \n")  # dish before
print pre
print("\nDish after: \n") #dish after
print d
