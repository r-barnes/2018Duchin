#!/usr/bin/env python3

import csv
import sys
import pandas as pd
import os

def TeXImage(name):
  if os.path.exists(name):
    return "\\raisebox{{-0.5\height}}{{\\includegraphics[width=0.32\\columnwidth]{{{name}}}}}".format(name=name)
  else:
    return "Missing"

#\\parbox{{3.5cm}}{{\\centering Intentionally \\\\ Omitted}}
discrete_entry = """
\\begin{{minipage}}{{\columnwidth}}
\\begin{{tabular}}{{lccc}}
{imaget1} & {imaget2} & {imaget3} \\\\
{imageb1} & {imageb2} & {imageb3} \\\\
\\end{{tabular}}
\\imtitle{{{dname}}}
\\end{{minipage}}
"""

fips = {"01":"Alabama", "02":"Alaska", "04":"Arizona", "05":"Arkansas", "06":"California", "08":"Colorado", "09":"Connecticut", "10":"Delaware", "11":"District of Columbia", "12":"Florida", "13":"Georgia", "15":"Hawaii", "16":"Idaho", "17":"Illinois", "18":"Indiana", "19":"Iowa", "20":"Kansas", "21":"Kentucky", "22":"Louisiana", "23":"Maine", "24":"Maryland", "25":"Massachusetts", "26":"Michigan", "27":"Minnesota", "28":"Mississippi", "29":"Missouri", "30":"Montana", "31":"Nebraska", "32":"Nevada", "33":"New Hampshire", "34":"New Jersey", "35":"New Mexico", "36":"New York", "37":"North Carolina", "38":"North Dakota", "39":"Ohio", "40":"Oklahoma", "41":"Oregon", "42":"Pennsylvania", "44":"Rhode Island", "45":"South Carolina", "46":"South Dakota", "47":"Tennessee", "48":"Texas", "49":"Utah", "50":"Vermont", "51":"Virginia", "53":"Washington", "54":"West Virginia", "55":"Wisconsin", "56":"Wyoming", "60":"American Samoa", "66":"Guam", "69":"Commonwealth of the Northern Mariana Islands", "72":"Puerto Rico", "78":"U.S. Virgin Islands"}


df500        = pd.read_table('results/scores500.csv', sep='\s+')
df5          = pd.read_table('results/scores5.csv', sep='\s+')
df20         = pd.read_table('results/scores20.csv', sep='\s+')
df500['res'] = '0'
df5['res']   = '1'
df20['res']  = '2'

df            = df500.append(df5).append(df20)
df['GEOID']   = df['GEOID'].astype(str).str.pad(4,fillchar='0')
df['STATEFP'] = df['STATEFP'].astype(str).str.pad(2,fillchar='0')
df.sort_values(['GEOID','res'])

print("Printing discrete...")
fout = open('book/dg_entries.tex', 'w')


oldstate = None
for name, group in df.groupby(['GEOID']):
  geoid        = name
  statefp      = group.iloc[[0]]['STATEFP'].values[0]
  if oldstate!=statefp:
    this_state = fips[statefp]
    oldstate   = statefp
    fout.write('\\bchap{{{0}}}'.format(this_state))
  geoid = group.iloc[[0]]['GEOID'].values[0]
  fout.write(discrete_entry.format(
    geoid   = geoid,
    dname   = '{0} {1}'.format(this_state, group.iloc[[0]]['CD114FP'].values[0]),
    imaget1 = TeXImage('tract-{geoid}-full_shrunk.png'.format(geoid=geoid)),
    imaget2 = TeXImage('blockgroup-{geoid}-full_shrunk.png'.format(geoid=geoid)),
    imaget3 = TeXImage('block-{geoid}-full_shrunk.png'.format(geoid=geoid)),
    imageb1 = TeXImage('tract-{geoid}-net_shrunk.png'.format(geoid=geoid)),
    imageb2 = TeXImage('blockgroup-{geoid}-net_shrunk.png'.format(geoid=geoid)),
    imageb3 = TeXImage('block-{geoid}-net_shrunk.png'.format(geoid=geoid))
  ))
fout.close()
del fout