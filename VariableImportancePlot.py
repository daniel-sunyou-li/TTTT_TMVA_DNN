#!/usr/bin/env python
import matplotlib.pyplot as plt
import os


bit_string = "000010"

file_path = os.getcwd() + "/dataset/" + bit_string + "/"

importance_list = []
variable_list = []

start_reading = False

with open(file_path + "VarImportanceCalculation.txt") as file:
  for line in file.readlines():
    if start_reading == True:
      content = line.split(",")
      importance_list.append(content[0])
      variable_list.append(content[1])
    if "Variable" in line: start_reading = True

plt.close()
plt.plot(importance_list)
xTicks = []
xTicks.append((value*0.1)-0.5 for value in range(0,1))
plt.xticks(xTicks, variable_lsit)
plt.savefig(file_path + "VarImportancePlot.png")
