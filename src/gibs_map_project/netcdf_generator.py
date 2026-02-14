import os
from flask import Flask, request
from flask_cors import CORS
import requests
import pandas as pd
import xml.etree.ElementTree as ET
from PIL import Image
import xarray as xr
from owslib.wms import WebMapService
from tqdm import tqdm

# ------------------------------
# PATHS
# ------------------------------
DATA_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data"))
IMAGES_DIRECTORY = os.path.join(DATA_DIRECTORY, "images")
DATE_FORMAT = "%Y-%m-%d"

# Make sure image directory exists
os.makedirs(IMAGES_DIRECTORY, exist_ok=True)

# ------------------------------
# FLASK APP
# ------------------------------
app = Flask(__name__)
CORS(app)

# ------------------------------
# XML DOWNLOAD
# ------------------------------
def download_xml(metadata_href):
    try:
        response = requests.get(metadata_href)
        if response.status_code == 200:
            filename = os.path.basename(metadata_href)
            xml_path = os.path.join(DATA_DIRECTORY, filename)

            with open(xml_path, "wb") as f:
                f.write(response.content)

            return filename
        else:
            print(f"Failed to download XML from {metadata_href}")
            return None

    except Exception as e:
        print(f"Error downloading XML: {e}")
        return None


# ------------------------------
# CORS PRE-FLIGHT
# ------------------------------
@app.route("/save_data", methods=["OPTIONS"])
def handle_options():
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST",
        "Access-Control-Allow-Headers": "Content-Type",
    }
    return ("", 204, headers)


# ------------------------------
# MAIN PROCESSING ROUTE
# ------------------------------
@app.route("/save_data", methods=["POST"])
def save_data():
    data = request.json

    layer = data.get("layer")
    start_date = data.get("startDate")
    end_date = data.get("endDate")
    lonmin = float(data.get("lonmin"))
    latmin = float(data.get("latmin"))
    lonmax = float(data.get("lonmax"))
    latmax = float(data.get("latmax"))
    metadata_href = data.get("metadataHref")

    print(layer, start_date, end_date, lonmin, latmin, lonmax, latmax, metadata_href)

    # ------------------------------
    # DOWNLOAD XML
    # ------------------------------
    xml_filename = download_xml(metadata_href)
    if xml_filename is None:
        return "Failed to download XML", 500

    xml_path = os.path.join(DATA_DIRECTORY, xml_filename)

    # ------------------------------
    # GET WMS CLIENT
    # ------------------------------
    wms = WebMapService(
        "https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi?", version="1.1.1"
    )

    # ------------------------------
    # DOWNLOAD IMAGES
    # ------------------------------
    time_range = pd.date_range(start=start_date, end=end_date, freq="D")
    pbar_images = tqdm(total=len(time_range), desc="Downloading images")

    for time_value in time_range:
        time_str = time_value.strftime(DATE_FORMAT)

        img = wms.getmap(
            layers=[layer],
            srs="epsg:4326",
            bbox=(lonmin, latmin, lonmax, latmax),
            size=(2000, 2000),
            time=time_str,
            format="image/png",
            transparent=True,
        )

        filename = f"image_{layer}_{time_str}.png"
        image_path = os.path.join(IMAGES_DIRECTORY, filename)

        with open(image_path, "wb") as f:
            f.write(img.read())

        pbar_images.update(1)

    pbar_images.close()

    # ------------------------------
    # PARSE XML COLORMAP
    # ------------------------------
    tree = ET.parse(xml_path)
    root = tree.getroot()

    title = None
    units = "no unit available"

    color_map_elements = root.findall(".//ColorMap")
    if len(color_map_elements) >= 2:
        second_cm = color_map_elements[1]
        title = second_cm.attrib.get("title")
        units = second_cm.attrib.get("units", "no unit available")

    print("Title:", title)
    print("Units:", units)

    # Map RGB to value
    color_map = {}
    for entry in root.findall(".//ColorMapEntry"):
        rgb = tuple(map(int, entry.attrib["rgb"].split(",")))

        if entry.attrib.get("nodata") == "true":
            continue

        value_str = entry.attrib.get("value")
        if value_str:
            rng = value_str.strip("[]()").split(",")
            if len(rng) == 1:
                value = float(rng[0])
            else:
                if rng[0] == "-INF":
                    value = float(rng[1])
                elif rng[1] == "+INF":
                    value = float(rng[0])
                else:
                    value = (float(rng[0]) + float(rng[1])) / 2

            color_map[rgb] = value
        else:
            color_map[rgb] = None

    # ------------------------------
    # PROCESS IMAGES → DATAFRAME
    # ------------------------------
    df_list = []

    bounding_box = (lonmin, latmin, lonmax, latmax)
    image_files = [f for f in os.listdir(IMAGES_DIRECTORY) if f.endswith(".png")]
    pbar_proc = tqdm(total=len(image_files), desc="Processing images")

    for filename in image_files:
        image_path = os.path.join(IMAGES_DIRECTORY, filename)
        image = Image.open(image_path)
        pixels = image.load()
        width, height = image.size

        date_str = filename.split("_")[-1].split(".")[0]

        pixel_size_x = (lonmax - lonmin) / width
        pixel_size_y = (latmax - latmin) / height

        rows = []
        for y in range(height):
            for x in range(width):
                rgb = pixels[x, y][:3]
                if rgb in color_map:
                    value = color_map[rgb]
                    lon = lonmin + (x * pixel_size_x)
                    lat = latmax - (y * pixel_size_y)
                    rows.append(
                        {
                            "latitude": lat,
                            "longitude": lon,
                            "time": date_str + " 00:00:00",
                            "value": value,
                        }
                    )

        df_list.append(pd.DataFrame(rows))
        pbar_proc.update(1)

    pbar_proc.close()

    df = pd.concat(df_list, ignore_index=True)

    # ------------------------------
    # WRITE NETCDF
    # ------------------------------
    nc_path = os.path.join(DATA_DIRECTORY, "output.nc")
    ds = xr.Dataset.from_dataframe(df.set_index(["latitude", "longitude", "time"]))

    ds["value"].attrs["units"] = units
    ds["value"].attrs["long_name"] = title

    ds.to_netcdf(nc_path)

    print("====================================")
    print("| NetCDF file created successfully |")
    print("====================================")

    # ------------------------------
    # CLEANUP XML + IMAGES
    # ------------------------------
    if os.path.exists(xml_path):
        os.remove(xml_path)

    for f in image_files:
        os.remove(os.path.join(IMAGES_DIRECTORY, f))

    return "Data processed and saved successfully"


# ------------------------------
# FLASK ENTRY POINT
# ------------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)
