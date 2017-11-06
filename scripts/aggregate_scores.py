#!/usr/bin/env python3

import glob
import sys
import pandas as pd
import fiona
import os
import string
import pickle

def ProcScores(geotype, sups, fileglob):
  data      = []
  fileglob  = string.Template(fileglob).substitute(os.environ)
  filenames = glob.glob(fileglob)
  for filename in filenames:
    scores = open(filename,"r").readlines()
    scores = [s.strip()[:-1].split("~") for s in scores]
    scores = [[p.split("=") for p in s] for s in scores]
    scores = [{p[0]:p[1] for p in s} for s in scores]
    for sco in scores:
      sco['NEIGHBOURS'] = list(map(int,sco['NEIGHBOURS'].split(',')))
      if 'PARENTS' in sco:
        sco['PARENTS']  = list(map(int,str(sco['PARENTS']).split(',')))
        sco['PARENTPR'] = list(map(float,str(sco['PARENTPR']).split(',')))
      else:
        print('Unit {0} has no parent!'.format(sco['GEOID10']))
        sco['PARENTS']  = []
        sco['PARENTPR'] = []
    for sco in scores:
      for i,p in enumerate(sco['PARENTS']):
        data.append({
          'parent':   sups[p]['properties']['GEOID10'],
          'external': sco['EXTCHILD'] == 'T',
          'per':      sco['PARENTPR'][i],
          'child':    sco['GEOID10'],
          'geotype':  geotype
        })
  df = pd.DataFrame(data)
  return df


if len(sys.argv)!=5:
  print("Syntax: {0} <Parents File> <Tract Scores> <Block Group Scores> <Block Scores>".format(sys.argv[0]))
  sys.exit(-1)

print("Loading superunits...")
sup_filename = sys.argv[1]
sup_fiona    = fiona.open(sup_filename)
sup_prj      = sup_fiona.crs
sups         = [x for x in sup_fiona]


dftract = ProcScores('tract',      sups, sys.argv[2])
dfbg    = ProcScores('blockgroup', sups, sys.argv[3])
dfblock = ProcScores('block',      sups, sys.argv[4])

df = pd.concat([dftract, dfbg, dfblock], ignore_index=True)

pickle.dump(df, open( "discrete_geom_2013score_ag.pickle", "wb" ) )

df50         = df.loc[df['per']>0.5]
df50         = df50.groupby(["parent","geotype","external"]).agg({'child':'count'}).reset_index()
df50         = df50.pivot_table(index=['parent','geotype'], columns='external')
df50.columns = df50.columns.droplevel().rename(None)
df50         = df50.reset_index().fillna("null")

df10         = df.loc[df['per']>0.1]
df10         = df10.groupby(["parent","geotype","external"]).agg({'child':'count'}).reset_index()
df10         = df10.pivot_table(index=['parent','geotype'], columns='external')
df10.columns = df10.columns.droplevel().rename(None)
df10         = df10.reset_index().fillna("null")

df10 = pd.melt(df10, id_vars=['parent', 'geotype'])
df50 = pd.melt(df50, id_vars=['parent', 'geotype'])

df10 = df10.rename(columns={True: "Boundary10", False: "Interior10"})
df50 = df50.rename(columns={True: "Boundary50", False: "Interior50"})

#Merge into df10 for output
df10['Interior50'] = df50['Interior50']
df10['Boundary50'] = df50['Boundary50']

df10.to_csv("results/dg2013_scores.csv", sep=",", index=None)
