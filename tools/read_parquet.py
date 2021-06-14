import pandas as pd
import os
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument( "-f", "--folder", required = True )
args = parser.parse_args()

df = pd.read_parquet( args.folder )

print( len(df.index) )
print( len( df.iloc[0].as_matrix()[:-1] ) )
print( df.iloc[0]["type"] )

