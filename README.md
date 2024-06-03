## Preparation
- Install required packages pybind11, gdal, pyproj, json, shapely, tqdm
- Install the provided python package by 
	- "pip install ."
##  Run the scripts
- Run the following python scripts with correct configuration .json files. 
- ImageMC.py: prepare images by mosaicing, reprojection, and clipping
- regiongrow.py: use region grow to generate seeds from jrc water occurrence images
- region_split.py: multiresolution region splitting for bimodal gamma fitting
- multigamma.py: multivariate gamma function fitting (implemented for bimodal)
- filter.py: filter the threshold values to remove outliers
- idw2flood.py: interpolate the threshold values and thresholding the sar image for binary classification
- Operation steps:
- Run ImageMC.py with the configuration file imageMC.json as:
```json
{
	"Workspace": "C:\\Users\\leiwang\\workspace\\images",
    "Input Images":["Sentinel-1-0000000000-0000065536.tif","Sentinel-1-0000000000-0000000000.tif","Sentinel-1-0000000000-0000032768.tif"],
    "cell size x": 10,
    "cell size y": 10,
    "Output name":"sar_clp.tif",
    "Clip polygon": "clp_polygon.shp",
    "noData": -9999
}
```

- Run imageMC.py with the configuration file imageMC.json as
```json
{
	"Workspace": "C:\\Users\\leiwang\\workspace\\images",
	"Input Images":["jrc_water.tif"],
    "cell size x": 10,
    "cell size y": 10,
    "Output name":"jrc_water_clp.tif",
    "Clip polygon": "clp_polygon.shp",
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
```json
{
    "Workspace": "C:\\Users\\leiwang\\workspace\\images",
    "input image" : "sar_clp.tif",
    "regions" :"regions.shp",
    "point_shapefile_path" :"region_centroid.shp",
    "init" : "18 31 1 2"
}  
```
- python filter.py with json:
```json
{
    "Workspace": "C:\\Users\\leiwang\\workspace\\images",
    "shapefile_path" : "region_centroid.shp",
    "output_path" : "threshold.shp",
    "where clause": "(BC > 0.55 and (threshold > -20 and threshold <  ) or (BC < 0.55 and (threshold > -10 and threshold < )"
}
```
- python idw2flood.py with json:
```json
{
    "Workspace": "C:\\Users\\leiwang\\workspace\\images",
    "Point Features": "threshold.shp",
    "field name" : "threshold",
    "Raster": "sar_clp.tif",
    "Output binary raster": "bin_flood.tif",
    "power": 2

}

```
