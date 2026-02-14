import os
from io import BytesIO
import requests
import json
import urllib.request
from owslib.wms import WebMapService
import lxml.etree as xmltree

# ------------------------------
# NAMESPACES & PATHS
# ------------------------------
WMTS_NAMESPACE = "{http://www.opengis.net/wmts/1.0}"
OWS_NAMESPACE = "{http://www.opengis.net/ows/1.1}"
XLINK_NAMESPACE = "{http://www.w3.org/1999/xlink}"

# Where the JSON files should go
LAYERS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "layers"))
os.makedirs(LAYERS_DIR, exist_ok=True)

# WMTS capabilities URL
WMTS_URL = 'http://gibs.earthdata.nasa.gov/wmts/epsg4326/best/wmts.cgi?SERVICE=WMTS&REQUEST=GetCapabilities'

# ------------------------------
# FETCH WMTS CAPABILITIES
# ------------------------------
response = requests.get(WMTS_URL)
wmts_tree = xmltree.fromstring(response.content)

all_layers = []
layer_info = {}

# ------------------------------
# PARSE CAPABILITIES
# ------------------------------
for child in wmts_tree.iter():
    for layer in child.findall(f"./{WMTS_NAMESPACE}Layer"):
        if f"{WMTS_NAMESPACE}Layer" == layer.tag:
            layer_data = {}
            layer_identifier = layer.find(f"{OWS_NAMESPACE}Identifier")
            if layer_identifier is not None:
                layer_name = layer_identifier.text
                all_layers.append(layer_name)
                layer_data['Layer'] = layer_name

                bounding_box_element = layer.find(f"{OWS_NAMESPACE}WGS84BoundingBox")
                if bounding_box_element is not None:
                    layer_data['BoundingBox'] = {
                        'crs': bounding_box_element.get('crs'),
                        'UpperCorner': bounding_box_element.find(f"{OWS_NAMESPACE}UpperCorner").text,
                        'LowerCorner': bounding_box_element.find(f"{OWS_NAMESPACE}LowerCorner").text
                    }

                tile_matrix_set_element = layer.find(f"{WMTS_NAMESPACE}TileMatrixSetLink")
                if tile_matrix_set_element is not None:
                    layer_data['TileMatrixSet'] = tile_matrix_set_element.find(f"{WMTS_NAMESPACE}TileMatrixSet").text

                time_extent_element = layer.find(f"{WMTS_NAMESPACE}Dimension")
                if time_extent_element is not None:
                    time_extent = []
                    time_values = time_extent_element.findall(f"{WMTS_NAMESPACE}Value")
                    if time_values is not None:
                        for value in time_values:
                            time_extent.append(value.text)
                        layer_data['TimeExtent'] = time_extent

                format_element = layer.find(f"{WMTS_NAMESPACE}Format")
                if format_element is not None:
                    layer_data['Format'] = format_element.text

                style_element = layer.find(f"{WMTS_NAMESPACE}Style")
                if style_element is not None:
                    style_identifier = style_element.find(f"{OWS_NAMESPACE}Identifier")
                    if style_identifier is not None:
                        layer_data['Style'] = style_identifier.text

                    legend_urls = style_element.findall(f"{WMTS_NAMESPACE}LegendURL")
                    for legend_url in legend_urls:
                        if legend_url.get(f"{XLINK_NAMESPACE}role") == 'http://earthdata.nasa.gov/gibs/legend-type/horizontal':
                            layer_data['HorizontalLegendHref'] = legend_url.get(f"{XLINK_NAMESPACE}href")

                resource_url_element = layer.find(f"{WMTS_NAMESPACE}ResourceURL")
                if resource_url_element is not None:
                    layer_data['Template'] = resource_url_element.get('template')

                for metadata_element in layer.findall(f"{OWS_NAMESPACE}Metadata"):
                    if "vector-metadata" in metadata_element.get(f"{XLINK_NAMESPACE}href"):
                        vector_metadata_url = metadata_element.get(f"{XLINK_NAMESPACE}href")
                        layer_data['VectorMetadata'] = vector_metadata_url

                        response = urllib.request.urlopen(vector_metadata_url)
                        data = json.loads(response.read())
                        layer_data['VectorProperties'] = data['mvt_properties']
                        break

                # Last Metadata xlink:href
                last_metadata_href = None
                for metadata_element in reversed(list(layer.findall(f"{OWS_NAMESPACE}Metadata"))):
                    last_metadata_href = metadata_element.get(f"{XLINK_NAMESPACE}href")
                    break
                if last_metadata_href:
                    layer_data['MetadataHref'] = last_metadata_href

                layer_info[layer_name] = layer_data

# ------------------------------
# SAVE JSON FILES TO LAYERS FOLDER
# ------------------------------
with open(os.path.join(LAYERS_DIR, 'layers_info.json'), 'w') as f:
    json.dump(layer_info, f, indent=4)

with open(os.path.join(LAYERS_DIR, 'all_layers.json'), 'w') as f:
    json.dump(all_layers, f, indent=4)
