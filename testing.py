import numpy as np
thisList = [0.070191,2.171684,1.104309,0.005645,10.000000]

for i,d in enumerate(thisList):
    y = thisList[d]
    x = np.random.normal(i + 1, 0.04, len(y))
    print(x,y)