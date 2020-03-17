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

def count_job(condorPath,seedOut,seedLog,seedOutDirectory,failed_count,finished_count):
  if seedOut in seedOutDirectory:
    job_success = False
    for line in open(os.getcwd() + "/condor_log/" + seedOut).readlines():
      if "ROC-integral" in line:
        job_success = True
        finished_count += 1
        return failed_count, finished_count
    if job_success == False:
      failed_count += 1
      print("{} failed to compute ROC-integral.".format(seedOut))
      return failed_count, finished_count
  else:
    condor_done = False
    for line in open(condorPath + seedLog).readlines():
      if "005 (" or "009 (" in line: condor_done = True
      if "006 (" or "000 (" or "001 (" in line: condor_done = False
    if condor_done == False: return failed_count, finished_count
    else:
      failed_count += 1
      print("{} failed to run.".format(seedLog))
      return failed_count, finished_count

def count_jobs(condorPath,seedJobDirectory,seedOutDirectory,seedLogDirectory):
  failed_count = 0
  finished_count = 0
  for seedJob in seedJobDirectory:
    seed = seedJob.split(".job")[0]
    seedOut = seed + ".out"
    seedLog = seed + ".log"
    if seedLog not in seedLogDirectory:
      os.system("rm ./condor_log/{}".format(seedJob))
    else:
      failed_count, finished_count = count_job(condorPath,seedOut,seedLog,seedOutDirectory,failed_count,finished_count)
  return failed_count, finished_count
    
seedDirectory = os.listdir(os.getcwd() + "/../condor_log/")
seedOutDirectory = [seedStr for seedStr in seedDirectory if ".out" in seedStr]
seedLogDirectory = [seedStr for seedStr in seedDirectory if ".log" in seedStr]
seedJobDirectory = [seedStr for seedStr in seedDirectory if ".job" in seedStr]

numVars = int(seedOutDirectory[0].split("vars_")[0].split("Keras_")[1])
count_arr = np.zeros(numVars)

total_count = sum(".job" in seedStr for seedStr in seedDirectory)
failed_count, finished_count = count_jobs(os.getcwd()+"/../condor_log/",seedJobDirectory,seedOutDirectory,seedLogDirectory)

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
