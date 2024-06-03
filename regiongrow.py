import numpy as np
from osgeo import gdal
import region_grow
# compile the cpp program first: python setup.py build_ext --inplace

def read_image(filename):
    dataset = gdal.Open(filename, gdal.GA_ReadOnly)
    if not dataset:
        raise FileNotFoundError(f"Failed to open {filename}")
    band = dataset.GetRasterBand(1)
    image = band.ReadAsArray()
    return image, dataset

def write_image(filename, data, reference):
    driver = gdal.GetDriverByName("GTiff")
    out_dataset = driver.Create(filename, data.shape[1], data.shape[0], 1, gdal.GDT_Byte)
    if not out_dataset:
        raise RuntimeError(f"Failed to create {filename}")
    out_dataset.SetGeoTransform(reference.GetGeoTransform())
    out_dataset.SetProjection(reference.GetProjectionRef())
    out_band = out_dataset.GetRasterBand(1)
    out_band.WriteArray(data)
    out_band.FlushCache()

def main():
    import json,os
    launch_json = "regiongrow.json"

    json_file_path = launch_json

    # Read the JSON file
    try:
        with open(json_file_path, 'r') as file:
            args = json.load(file)
            workspace = args['Workspace']
            seed_image_path = os.path.join(workspace,args['seed image'])
            grow_image_path = os.path.join(workspace,args['grow image'])
            out_image_path = os.path.join(workspace,args['out image'])
            threshold = args['threshold']
    except Exception as e:
        print(e)
        print("Error reading from the regiongrow.json file")
        return
    seed_image, seed_dataset = read_image(seed_image_path)
    grow_image, grow_dataset = read_image(grow_image_path)
    
    output_image = np.zeros_like(grow_image, dtype=np.uint8)
    try:
        region_grow.region_grow(seed_image, grow_image, output_image, threshold)
    except Exception  as e:
        print(e)
    
    write_image(out_image_path, output_image, seed_dataset)

if __name__ == "__main__":
    main()
