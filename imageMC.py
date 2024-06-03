"""
Mosaic and clip the images ready for the next steps of flood delineation processes
Projection is done if necessary

"""

from osgeo import gdal
import json
import os

def mosaic_images(output_path, input_files):
    vrt_options = gdal.BuildVRTOptions(resampleAlg='bilinear', addAlpha=True)
    vrt = gdal.BuildVRT('/vsimem/mosaic.vrt', input_files, options=vrt_options)
    gdal.Translate(output_path, vrt)
    vrt = None  # Close the VRT

def reproject_image(input_path, output_path, target_srs):
    warp_options = gdal.WarpOptions(dstSRS=target_srs, resampleAlg='bilinear')
    gdal.Warp(output_path, input_path, options=warp_options)

def clip_image(input_path, output_path, cutline_path):
    warp_options = gdal.WarpOptions(cutlineDSName=cutline_path, cropToCutline=True, dstAlpha=True)
    gdal.Warp(output_path, input_path, options=warp_options)
    
def main():
    launch_json =  "imageMC.json"

    json_file_path = launch_json

    # Read the JSON file
    
    with open(json_file_path, 'r') as file:
        args = json.load(file)


#turn on GDAL exceptions to avoid deprecation warning
    gdal.UseExceptions()
    ogr.UseExceptions()
    path = args["Input path"]
    outputName = args["Output name"]
    inputImages = args["Input Images"]
    output_raster_path = os.path.join(args["Output path"],outputName)
    clp_polygon = args["Clip polygon"]
    x_res = args['cell size x']
    y_res = args['cell size y']
    noData = args['noData']
    input_raster_paths = [os.path.join(path,imagename) for imagename in inputImages]
        # Define the gdal.Warp options for clipping
    warp_options = gdal.WarpOptions(
        format='GTiff',            # Output format
        cutlineDSName=clp_polygon,  # Shapefile to use for clipping
        cropToCutline=True,       # Crop the raster to the extent of the cutline
        dstNodata=noData,           # NoData value for the output raster
        xRes=x_res, 
        yRes=y_res
        
    )
    input_rasters = [gdal.Open(raster) for raster in input_raster_paths] 

    # Use gdal.Warp to mosaic the rasters
    gdal.Warp(output_raster_path, input_rasters, options=warp_options)
    for raster in input_rasters:
        raster = None
        
    print(f"Mosaic and clip completed. Output raster saved as {output_raster_path}")
    
if __name__ == '__main__':
    main()
    