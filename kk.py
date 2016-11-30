import matplotlib.pyplot as plt
import numpy as np

x = np.arange(10)

plt.plot(x, x, x, 2 * x, x, 3 * x, x, 4 * x)

plt.legend(['y = x', 'y = 2x', 'y = 3x', 'y = 4x'], loc='upper left')

plt.show()