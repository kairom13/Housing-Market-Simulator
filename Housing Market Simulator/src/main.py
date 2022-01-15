'''
Created on Jan 15, 2022

@author: kairom13
'''

import uuid
import numpy as np
import matplotlib.pyplot as plt
import scipy.special as sps  

rng = np.random.default_rng()

class Occupant():
    def __init__(self):
        self.id = uuid.uuid4().hex[:8]
        self.objectType = 'Occupant'
        
        self.value = -1
        self.house = None
        
    def buyHouse(self, houseObject):
        self.house = houseObject
        self.house.setOccupant(self)
        
    def sellHouse(self):
        self.house = None
        
    def setBudget(self, budget):
        self.value = int(budget[0])
        
class House():
    def __init__(self, value):
        self.id = uuid.uuid4().hex[:8]
        self.objectType = 'House'
        
        self.value = int(value)
        self.occupant = None
        
    def setOccupant(self, occupantObject):
        self.occupant = occupantObject
        
    def removeOccupant(self):
        self.occupant = None
        
    def updatePrice(self, newValue):
        self.value = newValue
        
class Market():
    def __init__(self, side):
        self.side = side
        self.participants = []
        
    ## Occupants particpate as buyers
    ## Houses participate as sellers
    def addParticipant(self, obj):
        if self.side == 'Buy' and obj.objectType == 'House':
            print('House ' + str(obj.id) + ' is not allowed to participate in the buy market')
        elif self.side == 'Sell' and obj.objectType == 'Occupant':
            print('Occupant ' + str(obj.id) + ' is not allowed to participate in the sell market')
        else:
            self.participants.append(obj)
            
        if self.side == 'Sell':
            self.participants.sort(key=lambda x: x.value, reverse = True)
            
    def removeParticipant(self, obj):
        self.participants.remove(obj)
            
class Simulation():
    def __init__(self):
        
        self.occupantList = {}
        self.houseList = {}
        
        self.sellMarket = Market('Sell')
        self.buyMarket = Market('Buy')
        
        self.generateObjects(rng.integers(low=1000, high=1500), .2, .2)
    
    
    def generateObjects(self, numHouses, vacancyRate, homelessRate):
        shape, scale = 5., 50.
        houseValues = np.random.default_rng().gamma(shape, scale, numHouses)
        
        for h in houseValues:
            house = House(h)
            
            if rng.random() > vacancyRate:
                occupant = Occupant()
                house.setOccupant(occupant)
                
                self.occupantList.update({occupant.id: occupant})
            else:
                self.sellMarket.addParticipant(house)
                
            self.houseList.update({house.id: house})
        
        numPeople = int(numHouses * 1 / (1-vacancyRate))
        
        for p in range(numPeople):
            if rng.random() < homelessRate:
                occupant = Occupant()
                occupant.setBudget(np.random.default_rng().gamma(shape, scale, 1))
    
                self.occupantList.update({occupant.id: occupant})
                
                self.buyMarket.addParticipant(occupant)
    
        # count, bins, ignored = plt.hist(houseValues, 50, density=True)
        # y = bins**(shape-1)*(np.exp(-bins/scale) /  
        #                      (sps.gamma(shape)*scale**shape))
        # plt.plot(bins, y, linewidth=2, color='r')  
        # plt.show()
        
    def runTick(self):
        sales = {}
        newBuyers = []
        
        saleIndex = 1
        
        print('There are ' + str(len(self.sellMarket.participants)) + ' houses on the market')
        print('There are ' + str(len(self.buyMarket.participants)) + ' potential buyers')
        
        for s in self.sellMarket.participants: ## Iterate through houses to sell, from most to least valuable
            for b in self.buyMarket.participants: ## Iterate through buyers, from highest to lowest bid
                if b.value > s.value: # If the buyer's bid is higher than the price, buy the house (will always be highest bid)
                    if s.occupant is None:
                        sellerID = 'NEW'
                    else:
                        sellerID = s.occupant.id
                        newBuyers.append(s)
                    sales.update({saleIndex: {'House': s,
                                              'Buyer': b.id,
                                              'Seller': sellerID,
                                              'Price': b.value}})

                    b.buyHouse(s)
                    s.removeOccupant()
                    self.buyMarket.removeParticipant(b)
                    
                    saleIndex += 1
                    break
                
        print('There were ' + str(len(sales)) + ' sales:')
        for s, sale in sales.items():
            self.sellMarket.removeParticipant(sale['House'])
            print('\t' + str(sale['House'].id) + ' was sold to ' + str(sale['Buyer']) + ' by ' + str(sale['Seller']) + ' for $' + str(sale['Price']) + '; originally $' + str(sale['House'].value))
            sale['House'].updatePrice(sale['Price'])
            
        print(str(len(self.sellMarket.participants)) + ' houses were not sold')
        for s in self.sellMarket.participants:
            print('\t' + str(s.id) + ' was not sold for $' + str(s.value))
            
        print(str(len(self.buyMarket.participants)) + ' buyers were not successful')
        for b in self.buyMarket.participants:
            print('\t' + str(b.id) + ' could not find a house for $' + str(b.value))
            
        print('There are ' + str(len(newBuyers)) + ' new buyers for the next round')
        for nb in newBuyers:
            self.buyMarket.addParticipant(nb)
            print('\t' + str(nb.id) + ' wants to buy a house for $' + str(nb.value))
            
            
        
        
def main():
    simulation = Simulation()
    
    for i in range(1):
        simulation.runTick()

if __name__ == '__main__':
    main()