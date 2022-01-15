'''
Created on Jan 15, 2022

@author: kairom13
'''

import uuid
import numpy as np

class MarketObject():
    def __init__(self, objectType):
        self.id = uuid.uuid4().hex[:8]
        self.objectType = objectType
        
        self.value = -1
        self.associatedObject = None
        
    def setAssociatedObject(self, obj):
        self.associatedObject = obj
        
    def removeAssociatedObject(self):
        self.associatedObject = None
        
    def setValue(self, value):
        self.value = int(value)
        
class Market():
    def __init__(self, side):
        self.side = side
        self.participants = []
        
    ## Occupants particpate as buyers
    ## Houses participate as sellers
    def addParticipant(self, obj):
        if self.side == 'Buy' and obj.objectType == 'Dwelling':
            print('Dwelling ' + str(obj.id) + ' is not allowed to participate in the buy market')
        elif self.side == 'Sell' and obj.objectType == 'Household':
            print('Household ' + str(obj.id) + ' is not allowed to participate in the sell market')
        else:
            self.participants.append(obj)

        self.participants.sort(key=lambda x: x.value, reverse = True)
            
    def removeParticipant(self, obj):
        self.participants.remove(obj)
            
class Simulation():
    def __init__(self, settings):
        self.initial = settings['Initial']
        self.perTick = settings['Per Tick']
        
        self.rng = np.random.default_rng()
        
        self.shape = 5.
        self.scale = 50.
        
        self.offMarketDwelling = {}
        
        self.sellMarket = Market('Sell')
        self.buyMarket = Market('Buy')

        numDwellingsMu, numDwellingsSigma = self.getMuAndSigma(self.initial['Number of Dwellings'])
        numDwellings = int(self.rng.normal(numDwellingsMu, numDwellingsSigma))
        
        self.generateObjects(numDwellings, 'Dwelling')
        
        numHouseholdsMu, numHouseholdsSigma = self.getMuAndSigma(self.initial['Number of Households'])
        numHouseholds = int(self.rng.normal(numHouseholdsMu, numHouseholdsSigma))
        
        self.generateObjects(numHouseholds, 'Household')
        
        self.tickStats = {'Off Market Dwellings': [],
                          'Market Households': [],
                          'Market Dwellings': [],
                          'Dwellings Sold': [],
                          'Dwellings not Sold': [],
                          'Households not Housed': [],
                          'Immigrants': [],
                          'Emigrants': [],
                          'New Buyers': [],
                          'New Sellers': [],
                          'New Construction': []}
        
        self.householdStats = {'Round': [], ## The "date"
                               'Household ID': [], ## The unique identifier of the household
                               'Dwelling': [], ## The dwelling they currently own, null if None
                               'Budget': [], ## Their budget if they are looking to buy
                               'Round Outcome': []}  ## [Content, No Buy, No Sell, Bought, Sold]
    
        
    def getMuAndSigma(self, string):
        if ',' not in string:
            print(str(string) + ' is not a valid string for getting mu and sigma')
        return int(string[:string.find(',')]), int(string[string.find(',')+1:])
    
    def generateObjects(self, numObjects, objectType):
        objectValues = self.rng.gamma(self.shape, self.scale, numObjects)
        
        for o in objectValues:
            marketObject = MarketObject(objectType)
            marketObject.setValue(o)
            
            if objectType == 'Dwelling':
                self.sellMarket.addParticipant(marketObject)
            elif objectType == 'Household':
                self.buyMarket.addParticipant(marketObject)
            else:
                print(str(objectType) + ' is not a valid type of market object')
    
        # count, bins, ignored = plt.hist(houseValues, 50, density=True)
        # y = bins**(shape-1)*(np.exp(-bins/scale) /  
        #                      (sps.gamma(shape)*scale**shape))
        # plt.plot(bins, y, linewidth=2, color='r')  
        # plt.show()
        
    def runTick(self, tickNum):
        tickStats = {'Off Market Dwellings': len(self.offMarketDwelling),
                     'Market Households': 0,
                     'Market Dwellings': 0,
                     'Dwellings Sold': 0,
                     'Dwellings not Sold': 0,
                     'Households not Housed': 0,
                     'Immigrants': 0,
                     'Emigrants': 0,
                     'New Buyers': 0,
                     'New Sellers': 0,
                     'New Construction': 0}
        
        self.faciliateSales(tickStats, tickNum)
        
        self.prepareNextTick(tickStats, tickNum)
        
        # print('------ Statistics --------')
        # print(str(tickStats['Market Dwellings']) + ' dwellings were on the market')
        # print(str(tickStats['Market Households']) + ' households were looking to buy a dwelling')
        # print(str(tickStats['Dwellings Sold']) + ' dwellings were sold')
        # print(str(tickStats['Dwellings not Sold']) + ' dwellings were not sold')
        # #for s in self.sellMarket.participants:
        #     #print('\t' + str(s.id) + ' was not sold for $' + str(s.value))
        #
        # print(str(tickStats['Households not Housed']) + ' buyers were not successful')
        # #for b in self.buyMarket.participants:
        #     #print('\t' + str(b.id) + ' could not find a house for $' + str(b.value))
        #
        # print(str(tickStats['New Buyers']) + ' households just sold their dwelling and will look for a new dwelling to buy')
        # print(str(tickStats['New Sellers']) + ' households are deciding to sell their dwelling')
        # print(str(tickStats['New Construction']) + ' new dwellings were built')
        #
        # newBuyers = tickStats['Households not Housed'] + tickStats['Immigrants'] + tickStats['New Buyers'] - tickStats['Emigrants']
        # newSellers = tickStats['Dwellings not Sold'] + tickStats['New Construction'] + tickStats['New Sellers']
        # print(str(newBuyers) + ' households will be looking to buy a dwelling next round')
        # print(str(newSellers) + ' dwellings will be looking to be sold next round\n')
        
        for key, value in tickStats.items():
            self.tickStats[key].append(value)

            
    def faciliateSales(self, tickStats, tickNum):
        sales = {}
        newBuyers = []
        
        saleIndex = 1
        
        tickStats['Market Dwellings'] = len(self.sellMarket.participants)
        tickStats['Market Households'] = len(self.buyMarket.participants)
        
        for s in self.sellMarket.participants: ## Iterate through houses to sell, from most to least valuable
            for b in self.buyMarket.participants: ## Iterate through buyers, from highest to lowest bid
                if b.value > s.value: # If the buyer's bid is higher than the price, buy the house (will always be highest bid)
                    if s.associatedObject is None:
                        sellerID = 'NEW'
                    else:
                        sellerID = s.associatedObject.id
                        newBuyers.append(s.associatedObject)
                        
                    sales.update({saleIndex: {'Dwelling': s,
                                              'Buyer': b.id,
                                              'Seller': sellerID,
                                              'Price': b.value}})
                    
                    self.householdStats['Round'].append(tickNum)
                    self.householdStats['Household ID'].append(b.id)
                    if b.associatedObject is None:
                        self.householdStats['Dwelling'].append(str('None'))
                    else:
                        self.householdStats['Dwelling'].append(str(b.associatedObject.id))
                    self.householdStats['Budget'].append(b.value)
                    self.householdStats['Round Outcome'].append('Bought from ' + str(sellerID))
                    
                    

                    b.setAssociatedObject(s)
                    s.removeAssociatedObject()
                    s.setAssociatedObject(b)
                    self.buyMarket.removeParticipant(b)
                    
                    saleIndex += 1
                    break
                
        tickStats['Dwellings Sold'] = len(sales)
        for s, sale in sales.items():
            self.sellMarket.removeParticipant(sale['Dwelling'])
            self.offMarketDwelling.update({sale['Dwelling'].id: sale['Dwelling']})
            
            #print('\t' + str(sale['Dwelling'].id) + ' was sold to ' + str(sale['Buyer']) + ' by ' + str(sale['Seller']) + ' for $' + str(sale['Price']) + '; originally $' + str(sale['Dwelling'].value))
            sale['Dwelling'].setValue(sale['Price'])
        
        tickStats['Dwellings not Sold'] = len(self.sellMarket.participants)
        tickStats['Households not Housed'] = len(self.buyMarket.participants)

            
        for nb in newBuyers:
            self.buyMarket.addParticipant(nb)
            tickStats['New Buyers'] += 1

            self.householdStats['Round'].append(tickNum)
            self.householdStats['Household ID'].append(nb.id)
            self.householdStats['Dwelling'].append(str(nb.associatedObject.id))
            self.householdStats['Budget'].append(nb.value)
            self.householdStats['Round Outcome'].append('Sold')
            
    def prepareNextTick(self, tickStats, tickNum):
        newConstMu, newConstSigma = self.getMuAndSigma(self.perTick['New Construction Rate'])
        newConstruction = int(self.rng.normal(newConstMu, newConstSigma))
        
        for c in range(newConstruction):
            marketObject = MarketObject('Dwelling')
            marketObject.setValue(self.rng.gamma(self.shape, self.scale, 1))
            
            self.sellMarket.addParticipant(marketObject)
            tickStats['New Construction'] += 1
            
        immigrantMu, immigrantSigma = self.getMuAndSigma(self.perTick['Immigration Rate'])
        immigrants = int(self.rng.normal(immigrantMu, immigrantSigma))
        
        for i in range(immigrants):
            marketObject = MarketObject('Household')
            marketObject.setValue(self.rng.gamma(self.shape, self.scale, 1))
            
            self.buyMarket.addParticipant(marketObject)
            tickStats['Immigrants'] += 1
            
        movedSeller = []
        for s, newSeller in self.offMarketDwelling.items():
            if self.rng.random() < self.perTick['Sell Rate']:
                self.sellMarket.addParticipant(newSeller)
                movedSeller.append(s)
                
                tickStats['New Sellers'] += 1
                
        for m in movedSeller:
            self.offMarketDwelling.pop(m)
                
        for emigrant in self.buyMarket.participants:
            if self.rng.random() < self.perTick['Emigration Rate']:
                self.buyMarket.removeParticipant(emigrant)
                
                tickStats['Emigrants'] += 1
                
        
