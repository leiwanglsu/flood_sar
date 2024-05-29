"""
region growing from seeds and controlled by a threshold value

"""

from osgeo import gdal
import json
import os
from skimage import data
from skimage.segmentation import random_walker
from skimage.exposure import rescale_intensity
import pyproj
import numpy as np
def pixel_to_geocoords (geotransform, col, row):
    """
    Transform pixel/line (col/row) coordinates to georeferenced coordinates (x/y).
    :param geotransform: GDAL GeoTransform array
    :param col: Column (x) index of the pixel
    :param row: Row (y) index of the pixel
    :return: Tuple of georeferenced coordinates (x, y)
    """
    originX = geotransform[0]
    pixelWidth = geotransform[1]
    rotationX = geotransform[2]
    originY = geotransform[3]
    rotationY = geotransform[4]
    pixelHeight = geotransform[5]

    x = originX + col * pixelWidth + row * rotationX
    y = originY + col * rotationY + row * pixelHeight

    return x, y
def xy2rowcol(geotransform, x, y):
    """
    Transform georeferenced coordinates (x, y) to pixel/line (col, row) coordinates.
    :param geotransform: GDAL GeoTransform array
    :param x: Georeferenced x coordinate
    :param y: Georeferenced y coordinate
    :return: Tuple of pixel coordinates (col, row)
    """
    originX = geotransform[0]
    pixelWidth = geotransform[1]
    rotationX = geotransform[2]
    originY = geotransform[3]
    rotationY = geotransform[4]
    pixelHeight = geotransform[5]

    col = int((x - originX) / pixelWidth)
    row = int((y - originY) / pixelHeight)

    return col, row



def transform_coordinates(x, y, src_proj, dst_proj):
    """
    Transform coordinates from source projection to destination projection.
    :param x: x coordinate
    :param y: y coordinate
    :param src_proj: source projection (CRS)
    :param dst_proj: destination projection (CRS)
    :return: Tuple of transformed coordinates (x, y)
    """
    transformer = pyproj.Transformer.from_crs(src_proj, dst_proj, always_xy=True)
    x_trans, y_trans = transformer.transform(x, y)
    return x_trans, y_trans




def main():
    launch_json = "parameters.json"

    json_file_path = launch_json

    # Read the JSON file
    
    with open(json_file_path, 'r') as file:
        args = json.load(file)
        
    seed_image = args['seed image']
    grow_image = args['grow image']
    out_image = args['out image']
    threshold = args['threshold']
    
    # read the seed image
    
    seed_image = gdal.Open(seed_image)
    grow_image = gdal.Open(grow_image)
    seed_geotransform = seed_image.GetGeoTransform()
    seed_prj = seed_image.GetProjection() 
    grow_geotransform = grow_image.GetGeoTransform()
    grow_prj = grow_image.GetProjection()
    if seed_prj != grow_prj:
        print(f"Projecting image from {seed_prj} to {grow_prj}")
        gdal.Warp(args['seed image']+"prj.tif", args["seed image"], dstSRS=grow_prj)
        seed_image = gdal.Open(args['seed image']+"prj.tif")
        seed_geotransform = seed_image.GetGeoTransform()
        seed_prj = seed_image.GetProjection() 
    seed_data =  seed_image.GetRasterBand(1).ReadAsArray()

    # Find the coordinates of seed points (where pixel value is 1)
    seed_points = np.column_stack(np.where(seed_data == 1))

    rows = seed_points[:, 0]
    cols = seed_points[:, 1]
    x_coords = seed_geotransform[0] + cols * seed_geotransform[1] + rows * seed_geotransform[2]
    y_coords = seed_geotransform[3] + cols * seed_geotransform[4] + rows * seed_geotransform[5]
    
    #find the row,col of the seeds in the grow image

    originX = grow_geotransform[0]
    pixelWidth = grow_geotransform[1]
    rotationX = grow_geotransform[2]
    originY = grow_geotransform[3]
    rotationY = grow_geotransform[4]
    pixelHeight = grow_geotransform[5]
    seed_points[:,0] = int((x_coords - originX) / pixelWidth)
    col = int((x - originX) / pixelWidth)
    row = int((y - originY) / pixelHeight)
    growData = grow_image.GetRasterBand(1).ReadAsArray()
    seed_image.close()
    grow_image.close()
# Initialize markers for the seed points
    markers = np.zeros(growData.shape, dtype=np.int32)
    # Set the marker for each seed point
    for i, (x, y) in enumerate(seed_points, start=1):
        markers[y, x] = i
    print("Markers initialized")

    # Perform the random walker segmentation
    print("Performing random walk")
    labels = random_walker(growData, markers, beta=threshold)
    cols = growData.shape[1]
    rows = growData.shape[0]
    print("\nWriting to raster")
    # Create the output GeoTIFF file
    if os.path.exists(out_image):
        os.remove(out_image)
    driver = gdal.GetDriverByName('GTiff')
    outds = driver.Create(out_image, cols, rows, 1, gdal.GDT_Byte)

    # Set geotransform and projection
    outds.SetGeoTransform(grow_geotransform)
    outds.SetProjection(grow_prj)
    out_band = outds.GetRasterBand(1)
    out_band.WriteArray(labels)    
    outds.close()
    
    
if __name__ == '__main__':
    main()