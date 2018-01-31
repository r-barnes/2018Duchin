#!/usr/bin/env python3

import csv
import glob
import sys
import pandas as pd
import fiona
import functools
import os
import string
import pickle

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


if len(sys.argv)!=5:
  print("Syntax: {0} <Parents File> <Tract Scores> <Block Group Scores> <Block Scores>".format(sys.argv[0]))
  sys.exit(-1)

print("Loading superunits...")
sup_filename = sys.argv[1]
sup_fiona    = fiona.open(sup_filename)
sup_prj      = sup_fiona.crs
sups         = [x for x in sup_fiona]


dftract = ProcScores('tract',      sups, sys.argv[2])

if sys.argv[3]!='-':
  dfbg    = ProcScores('blockgroup', sups, sys.argv[3])
else:
  dfbg = pd.DataFrame()

if sys.argv[4]!='-':
  dfblock = ProcScores('block',      sups, sys.argv[4])
else:
  dfblock = pd.DataFrame()

df = pd.concat([dftract, dfbg, dfblock], ignore_index=True)

#pickle.dump(df, open( "discrete_geom_2013score_ag.pickle", "wb" ) )

df50         = df.loc[df['per']>0.5]
df50         = df50.groupby(["parent","geotype","external"]).agg({'child':'count'}).reset_index()
df50         = df50.pivot_table(index=['parent','geotype'], columns='external')
df50.columns = df50.columns.droplevel().rename(None)
df50         = df50.reset_index().fillna("null")
df50         = df50.rename(columns={True: "Boundary50", False: "Interior50"})

df10         = df.loc[df['per']>0.1]
df10         = df10.groupby(["parent","geotype","external"]).agg({'child':'count'}).reset_index()
df10         = df10.pivot_table(index=['parent','geotype'], columns='external')
df10.columns = df10.columns.droplevel().rename(None)
df10         = df10.reset_index().fillna("null")
df10         = df10.rename(columns={True: "Boundary10", False: "Interior10"})

#Merge into df10 for output
df10['Interior50'] = df50['Interior50']
df10['Boundary50'] = df50['Boundary50']

df10 = df10.rename(columns={'parent':'DistrictID'})

# df10 = pd.melt(df10, id_vars=['parent', 'geotype'])
# df50 = pd.melt(df50, id_vars=['parent', 'geotype'])

dfint10 = df10[['DistrictID','geotype','Interior10']]
dfint10 = dfint10.pivot(index='DistrictID', columns='geotype', values='Interior10')
dfint10 = dfint10.rename(columns={'tract':'TractInterior10', 'block':'BlockInterior10', 'blockgroup':'BGInterior10'})
dfint10.index.name = 'DistrictID'
dfint10.reset_index(inplace=True)

dfext10 = df10[['DistrictID','geotype','Boundary10']]
dfext10 = dfext10.pivot(index='DistrictID', columns='geotype', values='Boundary10')
dfext10 = dfext10.rename(columns={'tract':'TractBoundary10', 'block':'BlockBoundary10', 'blockgroup':'BGBoundary10'})
dfext10.index.name = 'DistrictID'
dfext10.reset_index(inplace=True)

dfint50 = df10[['DistrictID','geotype','Interior50']]
dfint50 = dfint50.pivot(index='DistrictID', columns='geotype', values='Interior50')
dfint50 = dfint50.rename(columns={'tract':'TractInterior50', 'block':'BlockInterior50', 'blockgroup':'BGInterior50'})
dfint50.index.name = 'DistrictID'
dfint50.reset_index(inplace=True)

dfext50 = df10[['DistrictID','geotype','Boundary50']]
dfext50 = dfext50.pivot(index='DistrictID', columns='geotype', values='Boundary50')
dfext50 = dfext50.rename(columns={'tract':'TractBoundary50', 'block':'BlockBoundary50', 'blockgroup':'BGBoundary50'})
dfext50.index.name = 'DistrictID'
dfext50.reset_index(inplace=True)

df_final = functools.reduce(lambda left,right: pd.merge(left,right,on='DistrictID'), [dfint10,dfext10,dfint50,dfext50])

df_final['DistrictName'] = df_final['DistrictID'].apply(lambda x: fips[x[0:2]] + ' District ' + x[2:])

#Reorder columns
columns = ['DistrictID', 'DistrictName', 'TractInterior10','TractBoundary10','TractInterior50','TractBoundary50','BGInterior10','BGBoundary10','BGInterior50','BGBoundary50','BlockInterior10','BlockBoundary10','BlockInterior50','BlockBoundary50']
df_final = df_final[columns]


df_final.to_csv("20180131-moon-output.csv", sep=",", index=None, columns=columns, quoting=csv.QUOTE_ALL)
