#!/usr/bin/python

import os, sys, json datetime, itertools
import utils, varsList
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument( "-s", "--step",   required = True,       help = "Single Lep Analyzer step to submit" )
parser.add_argument( "-c", "--config", required = True,       help = ".json configuration file to use" )
parser.add_argument( "-t", "--test",   action = "store_true", help = "Run a unit test on a single category" )
args = parser.parse_args()

