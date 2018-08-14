import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
       
percent = .1

def data_gen():
    a = -0.004 / percent  # adjusts stretch, min -100, max -0.004
    h = 500 * percent    # adjusts midpoint, max 500
    k = 1000 * percent   # adjusts height, max 1000
    gen_list = ([x, a * (x - h) ** 2 + k] for x in np.arange(0, 1050 * percent, 1))
    return gen_list
 
def init():
    ax.set_ylim(-50, 1000)
    ax.set_xlim(-50, 1000)
    return point

fig, ax = plt.subplots()
point, = ax.plot([0], [0], 'ro', markersize=15)
# point.set_data(0, 0)
splat, = ax.plot([0], [0], 'ro', markersize=30)
splat.set_data(-100, -100)

# ax.grid()
 
def run(data):
    x, y = data
    if x < 990 * percent:
        point.set_data(x, y)
        return point
    else:
        point.set_data(-100, -100)
        splat.set_data(x, y)
        return splat
 
ani = animation.FuncAnimation(fig, run, data_gen, init_func=init,interval=1, repeat=False)

plt.show()