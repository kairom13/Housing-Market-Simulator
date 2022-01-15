# Housing-Market-Simulator
A simple simulation of how the housing market can work

Objects:
- Occupant
  - Budget: How much money they’re willing to pay for a new house
  - House: Link to the house they live in
    - Can be null
- House
  - Value: How much money the house is worth
    - When a house is bought, the value of the house is set at what ever the buyer's budget was
  - Occupant: Link to the person that lives here
- Market
  - Buyers: The people who are trying to buy a house
    - Can only be occupants
    - Can only buy a house if no current house
  - Sellers: The people who are trying to sell a house
    - Can only be houses

Process
1. Generate a random set of people and houses
- Choose distribution of budgets and house values
- Designate some people as homeless
- Designate some houses as vacant
2.	Each tick:
- Choose some people who want to sell
  - Choose a few who will not want to buy again (and will leave the person pool)
- Choose some people who want to buy
- Iterate through sellers, from most valuable to least
  - For each seller, sell to buyer with the highest budget
  - Once transaction is completed, remove buyer from market, add seller to buyer’s market
    - Randomly choose budget b/w 90% and 125% of original house value
Settings
- Rate of new construction
  - How often a brand-new house is created
  - Add to seller’s market
  - Randomly generated value
- Distribution of value for new construction
  - The distribution of prices that new houses are sold at
  - i.e. based on rent controls, random, buyer demand, etc
- Sell Rate
  - How often existing houses are put on the market
- Immigration Rate
  - How often new buyers appear in the market
- Emigration Rate
  - How often occupants leave the market
