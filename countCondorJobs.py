#/usr/bin/env python
import glob, os, sys
import math
import numpy as np
import varsList

def variable_occurence(count_arr, seed):
  seed_str = "{:0{}b}".format(seed,len(count_arr))
  for count, variable in enumerate(seed_str):
    if variable == "1": count_arr[count] += 1
  return count_arr

seedDirectory = os.listdir(os.getcwd() + "/condor_log/")
seedOutDirectory = [seedStr for seedStr in seedDirectory if ".out" in seedStr]
seedLogDirectory = [seedStr for seedStr in seedDirectory if ".log" in seedStr]

numVars = int(seedOutDirectory[0].split("vars_")[0].split("Keras_")[1])
count_arr = np.zeros(numVars)

total_count = 0
finished_count = 0
failed_count = 0

# count total number of jobs submitted
for seedStr in seedDirectory:
  if ".job" in seedStr: total_count += 1

# counts finished jobs and counts variable frequency in seed generation
print("Jobs with .out files that do not have a ROC-integral:")
for seedOut in seedOutDirectory:
  job_success = False
  for line in open(os.getcwd() + "/condor_log/" + seedOut).readlines():
    if "ROC-integral" in line:
      finished_count += 1
      job_success = True
  if job_success == False: 
    print(seedOut)
    failed_count += 1
    
print("Jobs that were removed by scheduler:")
for seedLog in seedLogDirectory:
  seedOut = seedLog.split(".log")[0] + ".out"
  if seedOut not in seedOutDirectory:
    print(seedOut)
    failed_count += 1

for seedName in seedDirectory:
  if "Subseed" not in seedName and ".job" in seedName:
    seed = int(seedName.split("_Seed_")[1].split(".job")[0])
    count_arr = variable_occurence(count_arr,seed)
    
# display variable frequency 
print("{:<3} {:<32} {:<6}".format("#","Variable Name","Count"))
for i in range(numVars):
  print("{:<3} {:<32} {:<6}".format(str(i)+".",varsList.varList["BigComb"][i][0],int(count_arr[i])))

# display job status
print("Finished condor jobs: {} / {}, {:.2f}%".format(
  finished_count, total_count, 100. * float(finished_count) / float(total_count)
  )
)

print("Failed condor jobs: {} / {}, {:.2f}%".format(
  failed_count, total_count, 100. * float(failed_count) / float(total_count)
  )
)
