
- Install required packages pybind11, gdal, pyproj, json, shapely, tqdm
- Install the provided python package by 
	- "pip install ."
- Run python ImageMC.py with the configuration file imageMC.json as:
```json
{
    "Comment 1": "Below is for imageMC.py",
    "Input Images":["Sentinel-1-0000000000-0000065536.tif","Sentinel-1-0000000000-0000000000.tif","Sentinel-1-0000000000-0000032768.tif"],
    "Input path": "D:\\workspace\\data\\images",
    "Output path": "D:\\workspace\\data\\images",
    "cell size x": 10,
    "cell size y": 10,
    "Output name":"sar_clp.tif",
    "Clip polygon": "D:\\workspace\\data\\images\\clp_polygon.shp",
    "noData": -9999
}
```

- Run python imageMC.py with the configuration file imageMC.json as
```json
{
    "Comment 1": "Below is for imageMC.py",
    "Input Images":["jrc_water.tif"],
    "Input path": "D:\\workspace\\data\\images",
    "Output path": "D:\\workspace\\data\\images",
    "cell size x": 10,
    "cell size y": 10,
    "Output name":"jrc_water_clp.tif",
    "Clip polygon": "D:\\workspace\\data\\images\\clp_polygon.shp",
    "noData": -9999
}
```

- Run regiongrow.py with the configuration file regiongrow.json as
```json
{
"Workspace": "C:\\Users\\leiwang\\workspace\\images",
"seed image": "jrc_water_clp.tif",
"grow image": "sar_clp.tif",
"out image": "sar_perment_water.tif",
"threshold": -13.92
}
```

- Run region_split.py with the configuration file region_split.json as:
```json
{
    "Workspace": "C:\\Users\\leiwang\\workspace\\images",
    "input image": "sar_perment_water.tif",
    "output polygon": "regions.shp",
    "threshold": 0.2,
    "tile size (m)": 2000,
    "levels": 4
}
```

- Run multigamma.py with json:
```python
{
    "Workspace": "C:\\Users\\leiwang\\workspace\\images",
    "input image" : "sar_clp.tif",
    "regions" :"regions.shp",
    "point_shapefile_path" :"region_centroid.shp",
    "init" : "18 31 1 2"
}  
```
