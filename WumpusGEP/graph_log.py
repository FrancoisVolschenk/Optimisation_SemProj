"""
Author: F Volschenk - 219030964
This file contains code used to plot the graph of population fitness over time
"""

from matplotlib import pyplot as plt
from matplotlib.lines import lineStyles

# Obtain the data that was collected during training
data = []
with open("train_log.txt", "r") as fp:
    data = fp.read().split()

# Process the data from the log file
score = []
winners = []
bests = []
for d in data:
    score.append(float(d.split("_")[1]))
    winners.append(float(d.split("_")[2]))
    bests.append(float(d.split("_")[3]))

# Plot the data 
generations = range(len(score))
plt.figure(1)
plt.plot(generations, score, label="Overall Fitness")
plt.xlabel("Generation")
plt.ylabel("Fitness")
plt.legend()
# save the image to disk
plt.savefig("overall_fitness_over_time.jpg")

plt.figure(2)
plt.plot(generations, winners, label="Winners")
plt.xlabel("Generation")
plt.ylabel("Winners")
plt.legend()
# save the image to disk
plt.savefig("winners_over_time.jpg")

plt.figure(3)
plt.plot(generations, bests, label="Gen Bests")
plt.xlabel("Generation")
plt.ylabel("Bests")
plt.legend()
# save the image to disk
plt.savefig("bests_over_time.jpg")


plt.show()