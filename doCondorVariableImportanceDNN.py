#!/usr/bin/env python

import os, sys
import varsList
import random

nTrees = '100'
varListKeys = ['BigComb']
runDir = os.getcwd()
condorDir = runDir + '/condor_log/'
os.system('mkdir -p ' + condorDir)

count = 0

method = 'Keras'
mDepth = '2'

varList = varsList.varList['BigComb']
seed = len(varList)*len(varList)
binary_str = '1' * len(varList)

for index in range(0, seed):
  SeedN = random.randint(0,int(binary_str,2)) # upper limit is decimal equivalent to binary of all 1s of length len(varList)
  outf_key = 'Seed_' + str(SeedN)
  fileName = method + '_' + 'BigComb' + '_' + str(len(varList)) + 'vars_mDepth' + mDepth + '_' + outf_key
  dict = {
    'RUNDIR':runDir,
    'METHOD':method,
    'vListKey':'BigComb',
    'nTrees':nTrees,
    'mDepth':mDepth,
    'SeedN':SeedN,
    'FILENAME':fileName
    }
  jdfName = condorDir + '%(FILENAME)s.job'%dict
  print(jdfName)
  jdf = open(jdfName, 'w')
  jdf.write(
"""universe = vanilla
Executable = %(RUNDIR)s/doCondorVariableImportanceWrapper.sh
Should_Transfer_Files = YES
WhenToTransferOutput = ON_EXIT
request_memory = 3072
Output = %(FILENAME)s.out
Error = %(FILENAME)s.err
Log = %(FILENAME)s.log
Notification = Never
Arguments = %(RUNDIR)s %(METHOD)s %(vListKey)s %(SeedN)s %(nTrees)s %(mDepth)s
Queue 1"""%dict)
  jdf.close()
  os.chdir('%s/'%(condorDir))
  os.system('condor_submit %(FILENAME)s.job'%dict)
  os.system('sleep 0.5')
  os.chdir('%s'%(runDir))
  count += 1 # iterate the job count
  print(count, 'jobs submitted.')
  
  for num in range(0, len(varList)):
    if(SeedN & (1 << num)):
      SubSeedN = SeedN & ~(1<<num)
      outf_key = 'Seed_' + str(SeedN) + '_Subseed_' + str(SubSeedN)
      fileName = method + '_' + 'BigComb' + '_' + str(len(varList)) + 'vars_mDepth' + mDepth + '_' + outf_key
      dict_sub = {
        'RUNDIR':runDir,
        'METHOD':method,
        'vListKey':'BigComb',
        'nTrees':nTrees,
        'mDepth':mDepth,
        'SeedN':SeedN,
        'FILENAME':fileName,
        'SubSeedN':SubSeedN
      }
      jdfName = condorDir + '%(FILENAME)s.job'%dict_sub
      print(jdfName)
      jdf = open(jdfName,'w')
      jdf.write(
"""universe = vanilla
Executable = %(RUNDIR)s/doCondorVariableImportanceWrapper.sh
Should_Transfer_Files = YES
WhenToTransferOutput = ON_EXIT
request_memory = 3072
Output = %(FILENAME)s.out
Error = %(FILENAME)s.err
Log = %(FILENAME)s.log
Notification = Never
Arguments = %(RUNDIR)s %(METHOD)s %(vListKey)s %(SubSeedN)s %(nTrees)s %(mDepth)s
Queue 1"""%dict_sub)
      jdf.close()
      os.chdir('%s/'%(condorDir))
      os.system('condor_submit %(FILENAME)s.job'%dict_sub)
      os.system('sleep 0.5')
      os.chdir('%s'%(runDir))
      print(count,'jobs submitted.') 
