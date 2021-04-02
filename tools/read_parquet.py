import pandas as pd
import os
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument( "-f", "--folder", required = True )
args = parser.parse_args()

df = pd.read_parquet( args.folder )

print( df[0:1] )
