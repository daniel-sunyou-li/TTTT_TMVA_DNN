#!/usr/bin/python

import sys, math
from ROOT import *

def is_equal(a,b):
  try:
    return a.upper() == b.upper()
  except AttributeError:
    return a == b

def contains(a,b):
  try:
    return b.upper() in a.upper()
  except AttributeError:
    return b in a
		
# category methods

def skip_nominal(cat): 
# not entirely sure what this is for
  if (cat[3]=="1" or cat[3]=="2p") and not (cat[1]=="0" and cat[2]=="0"): return True
  elif (cat[1]=="1p") and (cat[2]=="1p" or cat[3]=="1p") and (cat[5]=="4"): return True
  else: return False

def skip(cat):
  if (cat[1]=="0p" and cat[2]=="0p" and cat[3]=="0p"): return False
  if (cat[1]!="0p" and cat[2]=="0p" and cat[3]=="0p"): return False
  if (cat[1]=="0p" and cat[2]!="0p" and cat[3]=="0p"): return False
  if (cat[1]=="0p" and cat[2]=="0p" and cat[3]!="0p"): return False
  return True

# histogram methods

def poisson_norm_by_bin_width(tgae,hist):
# redefine the binning
  confLevel = 0.6827 # 1 sigma
  alpha = 1. - confLevel
  for i in range(tgae.GetN()):
    width = float(hist.GetBinWidth(i+1))
    X = tgae.GetX()[i]
    N = tgae.GetY()[i]
    L = 0
    if N != 0: L = Math.gamma_quantile(alpha/2., N, 1.0)
    U = Math.gamma_quantile_c(alpha/2., N+1, 1.0)
    tgae.SetPoint(i, X, N/width)
    tgae.SetPointEYlow(i, (N-L)/width)
    tgae.SetPointEYhigh(i, (U-N)/width)

def poisson_errors(tgae):
  confLevel = 0.6827
  alpha = 1. - confLevel
  for i in range(0, tgae.GetN()):
    N = tgae.GetY()[i]
    L = 0
    if N != 0: L = Math.gamma_quantile(alpha/2., N, 1.)
    U = Math.gamma_quantile_c(alpha/2., N+1, 1.)
    tgae.SetPointEYlow(i, N-L)
    tgae.SetPointEYhigh(i, U-N)
        
def norm_by_bin_width(h):
  h.SetBinContent(0,0)
  h.SetBinContent(h.GetNbinsX()+1, 0)
  h.SetBinError(0,0)
  h.SetBinError(h.GetNbinsX()+1, 0)
    
  for bin in range(1,h.GetNbinsX()+1):
    width = h.GetBinWidth(bin)
    content = h.GetBinContent(bin)
    error = h.GetBinError(bin)
        
    h.SetBinContent(bin, content/width)
    h.SetBinError(bin, error/width)
        
def negative_bin_correction(hist):
  norm0 = hist.Integral()
  if hist.GetNbinsY() > 1:
    for xBin in range(hist.GetNbinsX() + 2):
      for yBin in range(hist.GetNbinsY() + 2):
        if hist.GetBinContent(xBin,yBin,0):
          hist.SetBinContent(xBin,yBin,0)
          hist.SetBinError(xBin,yBin,0)
  else:
    for i in range(hist.GetNbinsX() + 2):
      if hist.GetBinContent(i) < 0:
        hist.SetBinContent(i,0)
        hist.SetBinError(i,0)
  if hist.Integral() != 0 and norm0 > 0: hist.Scale( norm0/hist.Integral() )
    
def overflow_bin_correction(hist):
  nBinsX = hist.GetXaxis().GetNbins()
  nBinsY = hist.GetYaxis().GetNbins()
  if nBinsY > 1: # 2D histogram
    for xBin in range(0, nBinsX + 2):
      content = hist.GetBinContent(xBin,nBinsY) + hist.GetBinContent(xBin,nBinsY + 1)
      error = math.sqrt( hist.GetBinError(xBin, nBinsY)**2 + hist.GetBinError(xBin, nBinsY + 1)**2 ) 
      hist.SetBinContent(xBin, nBinsY, error)
      hist.SetBinError(xBin, nBinsY, error)
      hist.SetBinContent(xBin, nBinsY+1, 0)
      hist.SetBinError(xBin, nBinsY+1, 0)
    for yBin in range(0, nBinsY + 2 ):
      content = hist.GetBinContent(nBinsX,yBin) + hist.GetBinContent(nBinsX+1,yBin)
      error = math.sqrt(hist.GetBinError(nBinsX,yBin)**2+hist.GetBinError(nBinsX+1,yBin)**2)
      hist.SetBinContent(nBinsX,yBin,content)
      hist.SetBinError(nBinsX,yBin,error)
      hist.SetBinContent(nBinsX+1,yBin,0)
      hist.SetBinError(nBinsX+1,yBin,0)
  else: # 1D histogram
    content=hist.GetBinContent(nBinsX)+hist.GetBinContent(nBinsX+1)
    error=math.sqrt(hist.GetBinError(nBinsX)**2+hist.GetBinError(nBinsX+1)**2)
    hist.SetBinContent(nBinsX,content)
    hist.SetBinError(nBinsX,error)
    hist.SetBinContent(nBinsX+1,0)
    hist.SetBinError(nBinsX+1,0)
        
def underflow_bin_correction(hist):
  nBinsX=hist.GetXaxis().GetNbins()
  nBinsY=hist.GetYaxis().GetNbins()
  if nBinsY>1: #2D histogram
    for xBin in range(0,nBinsX+2):
      content=hist.GetBinContent(xBin,1)+hist.GetBinContent(xBin,0)
      error = math.sqrt(hist.GetBinError(xBin,1)**2+hist.GetBinError(xBin,0)**2)
      hist.SetBinContent(xBin,1,content)
      hist.SetBinError(xBin,1,error)
      hist.SetBinContent(xBin,0,0)
      hist.SetBinError(xBin,0,0)
    for yBin in range(0,nBinsY+2):
      content=hist.GetBinContent(1,yBin)+hist.GetBinContent(0,yBin)
      error=math.sqrt(hist.GetBinError(1,yBin)**2+hist.GetBinError(0,yBin)**2)
      h.SetBinContent(1,yBin,content)
      hist.SetBinError(1,yBin,error)
      hist.SetBinContent(0,yBin,0)
      hist.SetBinError(0,yBin,0)
  else: #1D histogram
    content=hist.GetBinContent(1)+hist.GetBinContent(0)
    error=math.sqrt(hist.GetBinError(1)**2+hist.GetBinError(0)**2)
    hist.SetBinContent(1,content)
    hist.SetBinError(1,error)
    hist.SetBinContent(0,0)
    hist.SetBinError(0,0)
    
# print table methods

def round_sig(x, sig):
  if x == 0: return 0
  
  result = round(x, sig - int(math.floor(math.log10(x))) - 1)
  if ceil(math.log10(x)) >= sig: result = int(result)
  return result
    
def format(number):
  return str(number)
    
def getMaxWidth(table, index):
  #Get the maximum width of the given column index
  max=0
  for row in table:
    try:
      n=len(format(row[index]))
      if n>max: max=n
    except: pass
  return max
    
def print_table(table,out=sys.stdout):
  """Prints out a table of data, padded for alignment
  @param out: Output stream (file-like object)
  @param table: The table to print. A list of lists.
  Each row must have the same number of columns. """
  col_paddings = []

  maxColumns=0
  for row in table:
    if len(row)>maxColumns: maxColumns=len(row)

  for i in range(maxColumns):
    col_paddings.append(getMaxWidth(table, i))
        
  for row in table:
  # left col
    if row[0]=='break': row[0]='-'*(sum(col_paddings)+(2*len(col_paddings)))
    print >> out, format(row[0]).ljust(col_paddings[0] + 1),
  # rest of the cols
    for i in range(1, len(row)):
      col = format(row[i]).ljust(col_paddings[i] + 2)
      print >> out, col,
    print >> out
