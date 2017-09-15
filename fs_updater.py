import json
import requests

class FeatureServiceLayer():
    """" Well.. should have used the ArcGIS Python API.. """
    url = None
    def __init__(self, url):
        """ URL to the Feature Service"""
        self.url = url

    def UpdateFeatures(self, lists, buf=25):
        """ @param lists: lists of Feature json"""
        i = 0
        loopcount = int(len(lists)/buf)
        print "Updating features..."
        while i <= loopcount:
            sublist = lists[i*buf:(i+1)*buf]
            data = requests.post(self.url+"/updateFeatures", params={"features":json.dumps(sublist), "f":"json"})
            try:
                #print json.dumps(json.loads(data.text), indent=2)
                print "{:.2f}%".format((i)*100.0/loopcount)
            except:
                print data.text
            #print json.dumps(sublist, indent=2)
            #print ""
            i+=1
             

if __name__ == "__main__":
    fs = FeatureServiceLayer("https://services8.arcgis.com/TWq7UjmDRPE14lEV/arcgis/rest/services/tessellation_jakarta/FeatureServer/0")
    features = [{"attributes":{"FID":9, "TOTAL":90}},
                {"attributes":{"FID":7, "TOTAL":7}}]
    #print json.dumps(f, indent=2)
    fs.UpdateFeatures(features)




