### Earthdata Overview (WIP)

Earthdata is comprised of three main components:

1. **Search Criteria Panel**: Located on the left-hand side of the interface, this panel allows users to input their search criteria. Users can specify parameters such as date range, spatial region, and other filters.

2. **Data Display Panel**: Situated in the center of the interface, this panel showcases datasets that match the search criteria entered in the search panel. Users can manually navigate through filters to select the data they need.

3. **Map Visualization Panel**: Positioned on the right side of the interface, this panel provides a map interface for spatial search and data visualization. Users can utilize this feature to visualize spatial data on a map.

Additionally, users can input a specified date range using the date input feature located in the upper left corner. There's also an option to search within a region by cropping in a rectangle or employing other methods.

### Visualization Filtering

Upon filtering the desired criteria, users receive a list of visualizations that fit the specified criteria. This list includes the title of the data, the number of individual data files associated with the collection (known as granules), and the type of data, particularly emphasizing the HDF data type.

### About HDF (Hierarchical Data Format)

HDF is a data model consisting of three fundamental elements:

- **Datasets**: These are multidimensional arrays of homogeneous or heterogeneous data, akin to numpy-style multidimensional arrays.
  
- **Attributes**: Metadata associated with groups or datasets, providing additional information about the data. Attributes are in the form of key-value pairs and are attached to datasets.
  
- **Groups**: Containers capable of holding other groups or datasets, similar to folders in a file system.

The main library for working with hdf files is h5py
Remember h5py.File acts like a Python dictionary, thus we can check the keys