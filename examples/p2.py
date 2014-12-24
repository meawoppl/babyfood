# Failed attempt at penrose tiling
# MRG 07/2014
import numpy as np

# 5 vectors pointing toward the points of a pentagon
dimensions = 5
starters = np.linspace(0, 2 * np.pi, dimensions + 1)[:-1]
bVectors = np.array([(np.cos(t), np.sin(t)) for t in starters])
phi = (1 + np.sqrt(5)) / 2
shifts = np.array((-1, 1, -1.5, 0.65, 0.85))
translation = bVectors * shifts[:, np.newaxis]

print(translation)
samples = 1000
span = 10
# A uniform grid of points b/t -10 to 10 in 1000 step
xs, ys = np.mgrid[-span:span:samples * 1j, -span:span:samples * 1j]

# A place to accumulate the computed values
bGrid = np.zeros((samples, samples, dimensions))

# Plotting etc
from pylab import cool, figure, imshow, savefig, show

for i in range(dimensions):
    bGrid[:, :, i] = ((bVectors[i, 0] * xs + translation[i, 0]) +
                      (bVectors[i, 1] * ys + translation[i, 1]))

flattened = np.sum(np.dot(np.round(bGrid), axis=2)

figure(figsize=(12, 12))
imshow(flattened)
cool()
savefig("attempt.png")
show()
