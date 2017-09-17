import requests
from requests_oauthlib import OAuth1
import json
from osgeo import ogr
import config

track = "macet, padat, kriminal, mencurigakan, korupsi, hujan, jakarta"
par = {"track":track}
res = "https://stream.twitter.com/1.1/statuses/filter.json"

gridShapefile = "tessellation.shp"

#load grid shapefile into memory
ds = ogr.Open(gridShapefile)
memDriver = ogr.GetDriverByName('MEMORY')
memDs = memDriver.CreateDataSource('grid')
memDs.CopyLayer(ds.GetLayer(0), 'twitter')
gridLayer = memDs.GetLayer('twitter')

#Specify with your own consumerKey, consumerSecret, token, and accessTokenSecret in as variables in config.py
auth = OAuth1(config.consumerKey, config.consumerSecret, config.token, config.accessTokenSecret)
r = requests.get(res, params=par, auth=auth, stream=True)

for line in r.iter_lines():
    geoTweet = None
    lon = None
    lat = None
    try:
    	geoTweet = json.loads(line)
    	lon = geoTweet['coordinates']['coordinates'][0]
    	lat = geoTweet['coordinates']['coordinates'][1]
    	#print json.dumps(geoTweet, indent=2)
        #print "\n\n\n\n"
        
        geomFilter = ogr.Geometry(ogr.wkbPoint)
        geomFilter.AddPoint(lon, lat)
        gridLayer.SetSpatialFilter(geomFilter)
        gridFeature = gridLayer.next()
        if gridFeature is None:
        	continue
        gridFID = gridFeature.GetFID()
        gridID = gridFeature.GetField("GRID_ID")
        print str(gridFID) + ", "+gridID+"+1"
        #print json.dumps(jl, indent=2)
        #print json.dumps(linejson, indent=2)
    except:
    	#print "."
    	continue

ds = None
memDs = None