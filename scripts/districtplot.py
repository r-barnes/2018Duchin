#!/usr/bin/env python3
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
import matplotlib.lines as mlines
from descartes import PolygonPatch
import fiona
import shapely
from shapely.geometry import Polygon, MultiPolygon, shape
import sys
import matplotlib.patches as mpatches
import matplotlib.collections as mcollections
import os

def PlotNetwork(ax,subs,sup):
  for c in sup['properties']['CHILDREN']:
    for n in subs[c]['properties']['NEIGHBOURS']:
      if not n in sup['properties']['CHILDREN']:
        continue
      l = mlines.Line2D(
        [ subs[c]['properties']['CENTROIDX'], subs[n]['properties']['CENTROIDX'] ],
        [ subs[c]['properties']['CENTROIDY'], subs[n]['properties']['CENTROIDY'] ],
        marker    = ".",
        linewidth = 1,
        color     = "brown"
      )
      ax.add_line(l)
  #circles = []
  #inv     = ax.transData.inverted()
  #transed = inv.transform([(0, 0), (4,0)])
  #radius  = abs(transed[0][0]-transed[1][0])
  #for c in sup['properties']['CHILDREN']:
  #  cen    = (subs[c]['properties']['CENTROIDX'], subs[c]['properties']['CENTROIDY'])
  #  circles.append( mpatches.Circle(cen, radius=radius, color='red') )
  #ax.add_collection(mcollections.PatchCollection(circles))

def PlotDistricts(subs,sup,fileprefix):
  minx = 9e99
  miny = 9e99
  maxx = -9e99
  maxy = -9e99

  for c in sup['properties']['CHILDREN']:
    tminx, tminy, tmaxx, tmaxy = subs[c]['geometry'].bounds
    minx = min(minx,tminx)
    miny = min(miny,tminy)
    maxx = max(maxx,tmaxx)
    maxy = max(maxy,tmaxy)

  tminx, tminy, tmaxx, tmaxy = sup['geometry'].bounds
  minx = min(minx,tminx)
  miny = min(miny,tminy)
  maxx = max(maxx,tmaxx)
  maxy = max(maxy,tmaxy) 

  #Plot the network and the units
  fig  = plt.figure()
  ax   = fig.add_subplot(1,1,1, aspect='equal')
  w, h = maxx - minx, maxy - miny
  ax.set_xlim(minx - 0.0 * w, maxx + 0.0 * w)
  ax.set_ylim(miny - 0.0 * h, maxy + 0.0 * h)
  ax.set_aspect(1)
  ax.axis('off')
  for c in sup['properties']['CHILDREN']:
    patches = [PolygonPatch(p, ec="white", fc="#2BC7FF", alpha=1., zorder=1, fill=True) for p in subs[c]['geometry']]
    ax.add_collection(PatchCollection(patches, match_original=True))
  PlotNetwork(ax, subs, sup) 
  patches = [PolygonPatch(p, ec='black', alpha=1., zorder=1, fill=False, linewidth=2) for p in sup['geometry']]
  ax.add_collection(PatchCollection(patches, match_original=True))  
  plt.savefig(fileprefix + "-full.png", alpha=True, dpi=300, bbox_inches='tight')
  plt.clf()
  plt.cla()
  plt.close()

  #Plot just the network
  fig  = plt.figure()
  ax   = fig.add_subplot(1,1,1, aspect='equal')
  w, h = maxx - minx, maxy - miny
  ax.set_xlim(minx - 0.0 * w, maxx + 0.0 * w)
  ax.set_ylim(miny - 0.0 * h, maxy + 0.0 * h)
  ax.set_aspect(1)
  ax.axis('off')
  PlotNetwork(ax, subs, sup) 
  plt.savefig(fileprefix + "-net.png", alpha=True, dpi=300, bbox_inches='tight')
  plt.clf()
  plt.cla()
  plt.close()



if len(sys.argv)!=5:
  print("Syntax: {0} <Subunit Shapefile> <Superunit Shapefile> <Score file> <Output Prefix>".format(sys.argv[0]))
  sys.exit(-1)

outputprefix = sys.argv[4]

#Load data from shapefile
print("Loading subunits...")
sub_filename = sys.argv[1]
sub_fiona    = fiona.open(sub_filename)
sub_prj      = sub_fiona.crs
subs         = [x for x in sub_fiona]
for sub in subs:
  sub['geometry'] = shapely.geometry.shape(sub['geometry'])
  sub['geometry'] = MultiPolygon([sub['geometry']]) if isinstance(sub['geometry'],Polygon) else sub['geometry']

print("Loading superunits...")
sup_filename = sys.argv[2]
sup_fiona    = fiona.open(sup_filename)
sup_prj      = sup_fiona.crs
sups         = [x for x in sup_fiona]
for sup in sups:
  sup['geometry'] = shapely.geometry.shape(sup['geometry'])
  sup['geometry'] = MultiPolygon([sup['geometry']]) if isinstance(sup['geometry'],Polygon) else sup['geometry']


print("Loading scores...")
score_filename = sys.argv[3]
scores = open(score_filename,"r").readlines()
scores = [s.strip()[:-1].split("~") for s in scores]
scores = [[p.split("=") for p in s] for s in scores]
scores = [{p[0]:p[1] for p in s} for s in scores]

for sup in sups:
  sup['properties']['CHILDREN'] = []

for i, sub in enumerate(subs):
  sub['properties']               = scores[i]
  sub['properties']['NEIGHBOURS'] = list(map(int,sub['properties']['NEIGHBOURS'].split(',')))
  try:
    sub['properties']['PARENTS']    = map(int,str(sub['properties']['PARENTS']).split(','))
    for p in sub['properties']['PARENTS']:
      sups[p]['properties']['CHILDREN'].append(i)
  except: #TODO: This probably means there's a bug in the input data, though it seems to only affect blocks, and only a few of them.
    print("Block {0} had no parents!".format(i))
    continue


for i, sup in enumerate(sups):
  print("Plotting {0} of {1}".format(i, len(sups)))
  if len(sup['properties']['CHILDREN'])>0 and not os.path.exists(outputprefix + "-{0}-full.png".format(sup['properties']['GEOID10'])):
    PlotDistricts(subs, sup, outputprefix + "-{0}".format(sup['properties']['GEOID10']))
