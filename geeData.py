"""
This script help user obtain jrc and sentinel-1 images from Google Earth Engine by user specified extent and time.
Images will be uploaded by Google to user's Google drive. 
Authentication is need 

"""
import ee
import os,json
from gee_s1 import TerrainCorrection,refined_lee
from multiprocessing import Process

def main():


    try:
        ee.Initialize()
        
    except Exception as e:
        print(e)
        ee.Authenticate()
        ee.Initialize()

    # Getting the parameters from json
    base_name, _ = os.path.splitext(__file__)
    launch_json = base_name + '.json'
    json_file_path = launch_json

    # Read the JSON file
    try:
        with open(json_file_path, 'r') as file:
            args = json.load(file)
            workspace = args["Workspace"]
            extent_gcs = args['extent gcs[x1,y1,x2,y2]']
            url_jrc = args["url jrc"] #give an empty url if the image is not needed
            jrc_band = args['jrc band']
            url_s1 = args['url Sentinel-1'] #give an empty url if the image is not needed
            s1_band = args['Sentinel-1 band']
            s1_date = args["Sentinel-1 date[yyyy-mm-dd,yyyy-mm--dd]"].split(",")
            crs = args['Coordinate system'] #e.g. 'EPSG:32119'
    except Exception as e:
        print(e)    
        return
    numbers = extent_gcs.split(',')

    # Assign the extracted numbers to variables
    x1, y1, x2, y2 = map(float, numbers)
    bbox = ee.Geometry.BBox(x1,y1,x2,y2)
    
    # send the task for jrc on gee for processing. Establish a watching thread to update the status until the task is completed
    procs= []
    if(url_jrc != ""):
        try:
            datasetJRC = ee.Image(url_jrc).select(jrc_band)
            
            task = ee.batch.Export.image.toDrive(
                image= datasetJRC,
                description= 'JCRwaterpixels',
                region= bbox,
                folder= 'AnyFolder',
                scale= 30,
                fileFormat= 'GeoTIFF',
                maxPixels= 3784216672400,
                crs= crs
                )
            task.start()
            jrcWatcher = Process(target=Watcher,args=(task,))
            jrcWatcher.start()
            procs.append(jrcWatcher)
        except Exception as e:
            print(e)
    if(url_s1 != ""):

        s1Img = ee.ImageCollection(url_s1).select([s1_band,"angle"]) \
            .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV')) \
            .filter(ee.Filter.eq('instrumentMode', 'IW')) \
            .filterBounds(bbox) \
            .filterDate(s1_date[0],s1_date[1]).first()
        s1ImgT = TerrainCorrection(s1Img)
        s1ImgLee = refined_lee(s1ImgT.select(s1_band))
        taskS1 = ee.batch.Export.image.toDrive(
            image= s1ImgLee,
            description= 'S1_Lee_filter',
            region= bbox,
            folder= 'AnyFolder',
            scale= 10,
            fileFormat= 'GeoTIFF',
            maxPixels= 3784216672400,
            crs= crs
            )
        taskS1.start()
        s1Watcher = Process(target=Watcher,args=(taskS1,))
        s1Watcher.start()
        procs.append(s1Watcher)

    for proc in procs:
        proc.join()
def Watcher(task):
    import time
    """
    Watching the gee tasks until it completes
    
    """       
    ee.Initialize()
     
    while task.active():
        print(f'Polling for task (id: {task.id} with status of {task.status()['state']}')
        time.sleep(10)
    status = task.status()
    state = status['state']
    if state == 'COMPLETED':
            print('Task completed successfully')
            print(f"Image is ready from {task.status()['destination_uris'][0]}")

    elif state == 'FAILED':
        print(f"Task failed with error: {status['error_message']}")
    elif state in ['READY', 'RUNNING']:
        print(f"Task is still {state.lower()}. Waiting...")
    else:
        print(f"Task in unexpected state: {state}")
    return

if __name__ == "__main__":
    main()