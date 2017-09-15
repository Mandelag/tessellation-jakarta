import fs_updater
import time
import json
import sys
import requests
from fs_updater import FeatureServiceLayer
from osgeo import osr
from osgeo import ogr

def getFeatureByLocation(layer, lon, lat):
    point = ogr.Geometry(ogr.wkbPoint)
    point.AddPoint(lon, lat)
    layer.SetSpatialFilter(point)
    for f in layer:
        return f

cts = lambda: int(round(time.time())) 
qlueUrl = "http://services.qlue.id/qluein_marker_v2.php"
gridShapefile = "tessellation.shp" 
featureServiceLayer = "https://services8.arcgis.com/TWq7UjmDRPE14lEV/arcgis/rest/services/tessellation_jakarta/FeatureServer/0"


print "Downloading qlue data at " + qlueUrl
st = cts()
jdata = None
qlueData = requests.get(qlueUrl)
try:
    jdata = json.loads(qlueData.text)
except:
    print qlueData
    sys.exit(0)
et = cts()
print "Done in %d s."%(et-st)

#load local qlue data
#print "Reading qlue data..."
#jdata = None
#with open("data2.json") as data:
#    jdata = json.load(data)

memDriver = ogr.GetDriverByName("MEMORY")
memDs = memDriver.CreateDataSource("memData")
srs = osr.SpatialReference()
srs.ImportFromEPSG(4326)
qlueLayer = memDs.CreateLayer("qlue", srs, ogr.wkbPoint)


#load the tesselation data
ds = ogr.Open(gridShapefile)
tes = ds.GetLayer(0)

qlueLayer.StartTransaction()
for entry in jdata:
    lat = entry["profile"]["location"]["lat"]
    lon = entry["profile"]["location"]["lng"]
    #tipe = entry["type"] # not supported yet.
    geom = ogr.Geometry(ogr.wkbPoint)
    geom.AddPoint(lon,lat)
    f = ogr.Feature(qlueLayer.GetLayerDefn())
    f.SetGeometry(geom)
    qlueLayer.CreateFeature(f)
    f = None
qlueLayer.CommitTransaction()

result = {}

print "Count points in polygon.."
stime = cts()
for i in range(len(tes)):
    # reset the id and the total to zero
    feature = tes.GetFeature(i)
    grid_id = feature.GetField('GRID_ID')
    geom = feature.GetGeometryRef()
    result[grid_id] = [i,0]
    qlueLayer.SetSpatialFilter(geom)
    count = len(qlueLayer)
    result[grid_id][1] = count
    feature = None
etime = cts()
print "Done in "+str(etime-stime) + "s."

tojson = lambda (x,y): {"attributes":{"FID":y[0], "TOTAL":y[1]}}
listjson = map(tojson, result.iteritems())  
#print json.dumps(listjson)
fs = FeatureServiceLayer(featureServiceLayer)
#print json.dumps(f, indent=2)
print "Updating feature server.."
fs.UpdateFeatures(listjson)
print "Done"

# save as csv file.
#with open('result2.csv', 'w') as output:
#    output.write('OBJ_ID,GRID_ID,TOTAL\n')
#    for key, value in result.iteritems():
#        output.write(str(value[0])+','+key+','+str(value[1])+'\n')
#        #print value

#close the data source
ds = None
memDs = None