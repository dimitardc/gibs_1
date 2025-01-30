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


### Resources

- [NASA EarthData for Open Access for Open Science](https://www.earthdata.nasa.gov/eosdis/science-system-description/eosdis-components/gibs)
- [NASA GIBS Visualization Product Catalog](https://nasa-gibs.github.io/gibs-api-docs/available-visualizations/#visualization-product-catalog)
- [GIBS API Docs](https://nasa-gibs.github.io/gibs-api-docs/)
- [GIBS Access via API](https://nasa-gibs.github.io/gibs-api-docs/python-usage/)
