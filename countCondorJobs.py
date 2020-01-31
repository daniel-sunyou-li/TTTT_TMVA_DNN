#/usr/bin/env python
import glob, os, sys
import math
import varsList

seedDirectory = os.listdir(os.getcwd() + "/condor_log/")
seedOutDirectory = [seedStr for seedStr in seedDirectory if ".out" in seedStr]

total_count = 0
for seedStr in seedDirectory:
  if ".job" in seedStr: total_count += 1
  
finished_count = 0

for seedOut in seedOutDirectory:
  for line in open(os.getcwd() + "/condor_log/" + seedOut).readlines():
    if "ROC-integral" in line:
      finished_count += 1
      
print("Finished condor jobs: {} / {}, {:.2f}%".format(
  finished_count, total_count, 100 * float(finished_count) / float(total_count)
  )
)
