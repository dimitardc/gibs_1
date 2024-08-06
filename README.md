# NASA GIBS Research 🛰

Tags: Data Sourcing, Satellite Data, NASA
Codename: GIBS
Responsible: Dimitar Chonevski

## New Satellite Data Source - NASA Data exploration

### Hypothesis

We are currently using data from ESA and this data is in NetCDF format or CSV usually. This covers our satellite capabilities. We also download images from sentinel hub. We recently found that NASA has a lot of data available in their Global Imagery Browse Services (GIBS) and we want to explore this data to see if we can use it for our purposes. Our hypothesis is that these are images with some metadata attached, and we can use this data as well in our calculations, along with the ESA data.

### Goal

- We want to know WHAT data is available (Images or CSV or JSON or GeoTIFF or Something else)
- We want to know HOW can we access this NASA data
  - If the data needs extra processing to get values and numbers, we want to know HOW to do that
- We want to know WHAT relevant data is available
  - Rain, Temperature, Wind, Humidity, Lightning, Hail
  - Any data connected to floods
  - Any data connected to wildfires
  - Any data connected to droughts
  - Any data connected to vegetation

### Tasks

- [ ]  Research what GIBS is, what services they provide
  - [ ]  Document the findings
- [ ]  Research what open data can be accessed
  - [ ]  Find out all the ways the data can be accessed (Ex: Download, API)
  - [ ]  Find out how the data can be accessed
  - [ ]  Find an example data and download it
    - [ ]  If there is a chance to download it programmatically, write a script
  - [ ]  Document the findings
- [ ]  Find relevant data for Floods, Wildfires, Droughts, Vegetation
  - [ ]  Research all the data sets and make a list of all direct sources of data for the above mentioned disasters (Source that directly points to fires, or directly points to floods etc.)
  - [ ]  Research what is relevant data for the above mentioned disasters (Data that is connected to the disaster, but is not directly data for the disaster it self. Precipitation for flood for example or Air Pollution for wild fire)
  - [ ]  Make a list from the data sets on what relevant data is available for the above mentioned disasters
  - [ ]  ANY list of data sets should contain:
    - [ ]  Resolution (How precise is the data based on the area it covers. Example: 10km / 500m)
    - [ ]  Time Granularity (How precise is the data based on the area it covers. Example: Data every day / Data every hour)
    - [ ]  Temporal Range (When the data set starts and ends. Example: 2015 - 2023 / 2007 - Now)
    - [ ]  Data type measured ( Example: Precipitation / Fire Radiance Index )
    - [ ]  Format ( What format the data is. Example: PNG, GeoTIFF, NetCDF )
- [ ]  Research How to process this data programmatically
  - [ ]  Find out how data like the one you downloaded as an example is processed. See if there is any guidance or help in the GIBS documentation. If not, search on the internet
  - [ ]  List what methods/libraries can be used to process a data
  - [ ]  Document the findings
- [ ]  Process an example data
  - [ ]  Make a script that gets the data set
  - [ ]  Download/Install a library for processing this data set
  - [ ]  Make a script for processing the script
  - [ ]  Save the results on file system
  - [ ]  Analyze the results
  - [ ]  Document the process

### Resources

- [NASA EarthData for Open Access for Open Science](https://www.earthdata.nasa.gov/eosdis/science-system-description/eosdis-components/gibs)
- [NASA GIBS Visualization Product Catalog](https://nasa-gibs.github.io/gibs-api-docs/available-visualizations/#visualization-product-catalog)
- [GIBS API Docs](https://nasa-gibs.github.io/gibs-api-docs/)
- [GIBS Access via API](https://nasa-gibs.github.io/gibs-api-docs/python-usage/)
