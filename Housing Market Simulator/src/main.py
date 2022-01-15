'''
Created on Jan 15, 2022

@author: kairom13
'''

from custom_objects import Simulation
import pandas as pd

def main():
    settings = {'Initial': {'Number of Dwellings': '1500,200', ## Mean, standard deviation for choosing number of dwellings to start with
                            'Number of Households': '1500,200' ## Mean, standard deviation for choosing number of households to start with
                            },
                'Per Tick': {'New Construction Rate': '10,2', ## Mean, standard deviation for choosing number of dwellings to build per tick
                             'Sell Rate': .1, ## Probability that a household decides to put their dwelling on the market
                             'Immigration Rate': '200,30', ## Mean, standard deviation for choosing number of new buyers in the market
                             'Emigration Rate': .25 ## Probability that current buyer decides to leave the market
                             }}
    
    simulation = Simulation(settings)
    
    for i in range(50):
        print(i)
        simulation.runTick(i)
        
    pd.DataFrame.from_dict(simulation.tickStats).to_csv('summaryStats.csv')
    pd.DataFrame.from_dict(simulation.householdStats).to_csv('householdStats.csv')

    print('Code Executed')
if __name__ == '__main__':
    main()