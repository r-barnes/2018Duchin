#!/usr/bin/env python3

import csv
import fiona
import functools
import glob
import numpy as np
import os
import pandas as pd
import pickle
import string
import sys

fips = {'01':'AL','02':'AK','04':'AZ','05':'AR','06':'CA','08':'CO','09':'CT','10':'DE','11':'DC','12':'FL','13':'GA','15':'HI','16':'ID','17':'IL','18':'IN','19':'IA','20':'KS','21':'KY','22':'LA','23':'ME','24':'MD','25':'MA','26':'MI','27':'MN','28':'MS','29':'MO','30':'MT','31':'NE','32':'NV','33':'NH','34':'NJ','35':'NM','36':'NY','37':'NC','38':'ND','39':'OH','40':'OK','41':'OR','42':'PA','44':'RI','45':'SC','46':'SD','47':'TN','48':'TX','49':'UT','50':'VT','51':'VA','53':'WA','54':'WV','55':'WI','56':'WY','60':'AS','66':'GU','69':'MP','72':'PR','74':'UM','78':'VI'}

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


if len(sys.argv)!=7:
  print("Syntax: {0} <Parents File> <Tract Scores> <Block Group Scores> <Block Scores> <Population Data> <Output File>".format(sys.argv[0]))
  sys.exit(-1)

superunits_file = os.path.expandvars(sys.argv[1])
tract_glob      = os.path.expandvars(sys.argv[2])
blockgroup_glob = os.path.expandvars(sys.argv[3])
block_glob      = os.path.expandvars(sys.argv[4])
population_data = os.path.expandvars(sys.argv[5])
output_file     = os.path.expandvars(sys.argv[6])

print("Loading superunits...")
sup_filename = superunits_file
sup_fiona    = fiona.open(sup_filename)
sup_prj      = sup_fiona.crs
sups         = [x for x in sup_fiona]

if not os.path.exists("aggregate-score-geographic-data.pickle"):
  print("Loading tract data...")
  dftract = ProcScores('tract',      sups, tract_glob)

  if blockgroup_glob!='-':
    print("Loading block group data...")
    dfbg    = ProcScores('blockgroup', sups, blockgroup_glob)
  else:
    dfbg = pd.DataFrame()

  if block_glob!='-':
    print("Loading block data...")
    dfblock = ProcScores('block',      sups, block_glob)
  else:
    dfblock = pd.DataFrame()

  df = pd.concat([dftract, dfbg, dfblock], ignore_index=True)

  df = df.rename(columns={'external':'Int_or_Ext'})
  df['Int_or_Ext'] = df['Int_or_Ext'].replace(True,  'Boundary')
  df['Int_or_Ext'] = df['Int_or_Ext'].replace(False, 'Interior')

  pickle.dump(df, open( "aggregate-score-geographic-data.pickle", "wb" ) )
else:
  print("Loading pickled data 'aggregate-score-geographic-data.pickle'...")
  df = pickle.load(open("aggregate-score-geographic-data.pickle", "rb"))

raise Exception("test")

#Load population data
popdata = pd.read_csv(population_data, sep=' ', low_memory=False, header=0, dtype={'BLOCKID10': str, 'POP10': np.int32})
popdata = popdata.rename(columns={'BLOCKID10': 'blockid', 'POP10': 'population'})

popdata['tractid']  = popdata['blockid'].apply(lambda x: x[0:11])
popdata['blkgrpid'] = popdata['blockid'].apply(lambda x: x[0:12])

blockpop  = popdata[['blockid', 'population']]
blkgrppop = popdata.groupby('blkgrpid').sum().reset_index()
tractpop  = popdata.groupby('tractid').sum().reset_index()

blockpop  = blockpop.rename (columns={'blockid':  'geoid'})
blkgrppop = blkgrppop.rename(columns={'blkgrpid': 'geoid'})
tractpop  = tractpop.rename (columns={'tractid':  'geoid'})

popdata = pd.concat([blockpop,blkgrppop,tractpop], ignore_index=True)

merged = pd.merge(df, popdata, left_on='child', right_on='geoid', how='left')
del merged['geoid']

merged['WeightedPop'] = merged['per']*merged['population']
merged['WeightedPop'] = merged['WeightedPop'].fillna(value=0)

df = merged




df50         = df.loc[df['per']>0.5]
df50         = df50.groupby(["parent","geotype","Int_or_Ext"]).agg({'child':'count', 'WeightedPop':'sum'}).reset_index()
df50         = df50.rename(columns={'child': 'Count'})
df50         = df50.pivot_table(index=['parent','geotype'], columns='Int_or_Ext')
df50.columns = ['_'.join((col[1], col[0])) for col in df50.columns]
df50         = df50.reset_index().fillna("null")
df50         = df50.pivot_table(index=['parent'], columns='geotype')
df50.columns = ['_'.join((col[1].title(), col[0]))+"_50" for col in df50.columns]
df50         = df50.reset_index().fillna("null")

df10         = df.loc[df['per']>0.1]
df10         = df10.groupby(["parent","geotype","Int_or_Ext"]).agg({'child':'count', 'WeightedPop':'sum'}).reset_index()
df10         = df10.rename(columns={'child': 'Count'})
df10         = df10.pivot_table(index=['parent','geotype'], columns='Int_or_Ext')
df10.columns = ['_'.join((col[1], col[0])) for col in df10.columns]
df10         = df10.reset_index().fillna("null")
df10         = df10.pivot_table(index=['parent'], columns='geotype')
df10.columns = ['_'.join((col[1].title(), col[0]))+"_10" for col in df10.columns]
df10         = df10.reset_index().fillna("null")


dfout = pd.merge(df10,df50,on="parent")
dfout = dfout.rename(columns={'parent':'DistrictID'})

dfout['DistrictName'] = dfout['DistrictID'].apply(lambda x: fips[x[0:2]] + ' District ' + x[2:])

with open(output_file, "w") as fout:
  fout.write(
"""#Title:     Interior and Exterior subunit counts per U.S. Congressional District
#Date:      {date}
#Contact:   Richard Barnes (richard.barnes@berkeley.edu)
#Email:     richard.barnes@berkeley.edu
#Creators:  Richard Barnes (with help from Alejandro Velez-Arce)
#Generator: Generated using "a044bfda210a4e3e5fe1392957fca5ca1c3bfd3f" or later from "https://github.com/r-barnes/2018Duchin"
#Note:      Subunits are included if their area of intersection with a superunit exceeds a 50% or 10% threshold (see column names)
#Note:      Geographic Boundary Data drawn from the US Census Tiger/LINE data.
""".format(date=datetime.datetime.now().isoformat())
)
  #Reorder columns
  dfout.to_csv(fout, sep=",", index=None, quoting=csv.QUOTE_ALL)
