import cgxinit
import cloudgenix
import sys
import time
import datetime


# create CGX object and authenticate
cgx, args = cgxinit.go()
jd = cloudgenix.jd
jd_detailed = cloudgenix.jd_detailed

# create a site dictionary
sites={}
for site in cgx.get.sites().cgx_content["items"]:
    sites[site["id"]] = site["name"]

#print cvs header
print("Site,Element,Time UTC,CPU")
# iterate over each element and fatch stats
for element in cgx.get.elements().cgx_content["items"]:
    # skip any non assigned elements
    if element["state"] != "bound":
        continue
    
    # extract data from element
    e_id = element["id"]
    site_name = sites[element["site_id"]]
    site_id = element["site_id"]

    #preapre the query
    currtime =  (datetime.datetime.utcnow()+ datetime.timedelta(days=-0,hours=-0)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    hourback =  (datetime.datetime.utcnow()+ datetime.timedelta(days=-0,hours=-args["hours"])).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    query = {                                                                               
        "start_time": hourback,
        "end_time": currtime,
        "interval": "1min",
        "filter": {
            "site": [site_id],
            "element": [e_id]
        },
        "metrics": [{"name": "CPUUsage", "unit": "percentage",  "statistics": ["average"]}],
        "view": {"individual": "element"}
    }
    #execute query
    # for each datapoint chech if threashold passed. If it does then print the value
    for data in cgx.post.metrics_monitor(data=query).cgx_content["metrics"][0]["series"][0]["data"][0]["datapoints"]:
        if data["value"]:
            if data["value"]  >= args["min"]:
                print("{site},{element},{time},{cpu}".format(
                    site=site_name,
                    element=element["name"],
                    time=data["time"],
                    cpu=data["value"]
                ))
