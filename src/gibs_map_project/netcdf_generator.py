import os
import shutil
from flask import Flask, request
from flask_cors import CORS
import requests
import pandas as pd
import xml.etree.ElementTree as ET
from PIL import Image
from netCDF4 import Dataset
import xarray as xr
from owslib.wms import WebMapService
from tqdm import tqdm

DATA_DIRECTORY = '../../data/'
DATE_FORMAT = '%Y-%m-%d'

app = Flask(__name__)
CORS(app)

def download_xml(metadata_href):
    try:
        response = requests.get(metadata_href)
        if response.status_code == 200:
            filename = os.path.basename(metadata_href)
            with open(os.path.join(DATA_DIRECTORY, filename), 'wb') as f:
                f.write(response.content)
            return filename
        else:
            print(f"Failed to download XML from {metadata_href}")
            return None
    except Exception as e:
        print(f"Error downloading XML from {metadata_href}: {e}")
        return None

@app.route('/save_data', methods=['OPTIONS'])
def handle_options():
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST',
        'Access-Control-Allow-Headers': 'Content-Type'
    }
    return ('', 204, headers)


@app.route('/save_data', methods=['POST'])
def save_data():
    data = request.json

    layer = data.get('layer')
    start_date = data.get('startDate')
    end_date = data.get('endDate')
    lonmin = float(data.get('lonmin'))
    latmin = float(data.get('latmin'))
    lonmax = float(data.get('lonmax'))
    latmax = float(data.get('latmax'))
    metadata_href = data.get('metadataHref')  

    print(layer)
    print(start_date)
    print(end_date)
    print(lonmin)
    print(latmin)
    print(lonmax)
    print(latmax)
    print(metadata_href)
    xml_filename = download_xml(metadata_href)

    if xml_filename is None:
        return 'Failed to download XML file', 500

    wms = WebMapService('https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi?', version='1.1.1')

    time_range = pd.date_range(start=start_date, end=end_date, freq='D')

    pbar_images = tqdm(total=len(time_range), desc='Downloading images')

    for time_value in time_range:
        time_str = time_value.strftime(DATE_FORMAT)
        
        img = wms.getmap(layers=[layer],
                         srs='epsg:4326',
                         bbox=(lonmin,latmin,lonmax,latmax),
                         size=(2000*1,2000*1),
                         time=time_str,
                         format='image/png',
                         transparent=True)
        
        filename = f'image_{layer}_{time_str}.png'
        with open(DATA_DIRECTORY + "/images/" + filename, 'wb') as file:
            file.write(img.read())
        pbar_images.update(1)  

    pbar_images.close()  

    xml_path = os.path.join(DATA_DIRECTORY, xml_filename)
    tree = ET.parse(xml_path)
    root = tree.getroot()

    title = None
    units = "no unit available"

    color_map_elements = root.findall('.//ColorMap')

    if len(color_map_elements) >= 2:
        second_color_map_element = color_map_elements[1]
        title = second_color_map_element.attrib.get('title')
        units = second_color_map_element.attrib.get('units', "no unit available")

    print("Title:", title)
    print("Units:", units)

    # Mapping RGB values to ColorMapEntry values
    color_map = {}
    for entry in root.findall('.//ColorMapEntry'):
        rgb = tuple(map(int, entry.attrib['rgb'].split(',')))
        if entry.attrib.get('nodata') == 'true':
            continue  
        value_str = entry.attrib.get('value')
        if value_str is not None:
            value_range = value_str.strip('[]()').split(',')
            if len(value_range) == 1:
                value = float(value_range[0])
            else:
                # Handle cases with positive or negative infinity
                if value_range[0] == '-INF':
                    value = float(value_range[1])
                elif value_range[1] == '+INF':
                    value = float(value_range[0])
                else:
                    value = (float(value_range[0]) + float(value_range[1])) / 2
            color_map[rgb] = value
        else:
            color_map[rgb] = None

    df_list = []

    bounding_box = (lonmin,latmin,lonmax,latmax)

    image_dir = DATA_DIRECTORY + "images"  

    pbar_processing = tqdm(total=len(os.listdir(image_dir)), desc='Processing images')

    for filename in os.listdir(image_dir):
        if filename.endswith(".png"):
            # Read the downloaded image
            image_path = os.path.join(image_dir, filename)
            image = Image.open(image_path)
            pixels = image.load()
            width, height = image.size

            date_str = filename.split('_')[-1].split('.')[0]  # Extract the date part

            pixel_size_x = (bounding_box[2] - bounding_box[0]) / width
            pixel_size_y = (bounding_box[3] - bounding_box[1]) / height

            data = []

            for y in range(height):
                for x in range(width):
                    rgb = pixels[x, y][:3]  # Extract RGB values
                    if rgb in color_map:
                        value = color_map[rgb]
                        longitude = bounding_box[0] + (x * pixel_size_x)
                        latitude = bounding_box[3] - (y * pixel_size_y)
                        data.append({'latitude': latitude, 'longitude': longitude, 'time': date_str + ' 00:00:00', 'value': value})
            
            # Convert data to DataFrame and append to list
            df_list.append(pd.DataFrame(data))
            pbar_processing.update(1)  

    pbar_processing.close()  

    # Concatenate all DataFrames in the list
    df = pd.concat(df_list, ignore_index=True)

    nc_filename = DATA_DIRECTORY + "output.nc"
    ds = xr.Dataset.from_dataframe(df.set_index(['latitude', 'longitude', 'time']))
    
    ds['value'].attrs['units'] = units
    ds['value'].attrs['long_name'] = title
    
    ds.to_netcdf(nc_filename)
    print("===================================")
    print("|NetCDF file created successfully.|")
    print("===================================")

    if os.path.exists(os.path.join(DATA_DIRECTORY, xml_filename)):
        os.remove(os.path.join(DATA_DIRECTORY, xml_filename))

    images_dir = os.path.join(DATA_DIRECTORY, "images")
    for filename in os.listdir(images_dir):
        file_path = os.path.join(images_dir, filename)
        if os.path.isfile(file_path) and filename.endswith(".png"):
            os.remove(file_path)

    return 'Data processed and saved successfully'

if __name__ == '__main__':
    app.run(debug=True, port=5000)
