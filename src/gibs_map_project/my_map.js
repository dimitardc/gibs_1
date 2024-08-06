window.onload = function () {
    const LAYER_TYPES = {
        VECTOR: 'application/vnd.mapbox-vector-tile',
        IMAGE: 'image/png'
    };

    const LAYERS_INFO_JSON = '../../data/layers_info.json';

    let tileLayerResolutions = [0.5625, 0.28125, 0.140625, 0.0703125, 0.03515625, 0.017578125, 0.0087890625, 0.00439453125, 0.002197265625];
    let tileResolutions = [0.28125, 0.140625, 0.0703125, 0.03515625, 0.017578125, 0.0087890625, 0.00439453125, 0.002197265625, 0.0010986328125, 0.00054931640625];
    let tileExtent = [-180, -90, 180, 90];
    let matrixIds = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
    let tileSize = 512;
    let tileOrigin = [-180, 90]
    let baseUrl = 'https://gibs.earthdata.nasa.gov/wmts/epsg4326/best/wmts.cgi?';

    let layerInformation = {};
    let selectedLayer;
    let currentUrl;
    let vectorLayer;
    let lonmin;
    let latmin;
    let lonmax;
    let latmax;
    let legendContainer = document.getElementById('legend-container');
    let select = document.getElementById('layer-select');
    let map;
    let startDate
    let endDate

    function calculateMinDays(timeExtent) {
        if (!timeExtent || timeExtent.length === 0) {
            return -10; // If no time extent, set min to -10
        }
        let firstDate = new Date(timeExtent[0].split('/')[0]);
        let currentDate = new Date();
        let differenceInTime = currentDate.getTime() - firstDate.getTime();
        let differenceInDays = Math.floor(differenceInTime / (1000 * 3600 * 24));
        return -differenceInDays;
    }

    function saveDates() {
        startDate = document.getElementById('start-date').value;
        endDate = document.getElementById('end-date').value;
    }

    function calculateMaxDays(timeExtent) {
        if (!timeExtent || timeExtent.length === 0) {
            return 0; // If no time extent, set max to 0
        }
        let lastDate = new Date(timeExtent[timeExtent.length - 1].split('/')[1]);
        let currentDate = new Date();
        let differenceInTime = lastDate.getTime() - currentDate.getTime();
        let differenceInDays = Math.floor(differenceInTime / (1000 * 3600 * 24));
        return differenceInDays;
    }

    function fetchLegend(legendUrl) {
        let legendImg = document.createElement('img');
        legendImg.src = legendUrl;
        legendContainer.innerHTML = ''; // Clear previous legend
        legendContainer.appendChild(legendImg);
    }

    function generateUrl(days, layerObj) {
        let currentDate = new Date();
        currentDate.setDate(currentDate.getDate() + days);
        let formattedDate = currentDate.getFullYear() + '-' +
            ('0' + (currentDate.getMonth() + 1)).slice(-2) + '-' +
            ('0' + currentDate.getDate()).slice(-2);
        return baseUrl +
            'TIME=' + formattedDate + 'T00:00:00Z&' +
            'layer=' + layerObj.Layer + '&' +
            'tilematrixset=' + layerObj.TileMatrixSet + '&' +
            'Service=WMTS&' +
            'Request=GetTile&' +
            'Version=1.0.0&' +
            'FORMAT=' + layerObj.Format + '&' +
            'TileMatrix={z}&' +
            'TileCol={x}&' +
            'TileRow={y}';
    }

    function createLayer(layerObj, url) {
        if (layerObj.Format === LAYER_TYPES.VECTOR) {
            return new ol.layer.VectorTile({
                renderMode: 'vector',
                style: new ol.style.Style({
                    image: new ol.style.Circle({
                        radius: 2,
                        fill: new ol.style.Fill({
                            color: 'rgb(236, 98, 16)'
                        })
                    })
                }),
                source: new ol.source.VectorTile({
                    visible: true,
                    url: url,
                    format: new ol.format.MVT(),
                    matrixSet: layerObj.TileMatrixSet,
                    projection: ol.proj.get('EPSG:4326'),
                    tileGrid: new ol.tilegrid.WMTS({
                        extent: tileExtent,
                        resolutions: tileLayerResolutions,
                        tileSize: [tileSize, tileSize]
                    })
                })
            });
        } else if (layerObj.Format !== LAYER_TYPES.VECTOR) {
            return new ol.layer.Tile({
                source: new ol.source.WMTS({
                    url: url,
                    layer: layerObj.Layer,
                    format: layerObj.Format,
                    matrixSet: layerObj.TileMatrixSet,
                    tileGrid: new ol.tilegrid.WMTS({
                        origin: tileOrigin,
                        resolutions: tileLayerResolutions,
                        matrixIds: [0, 1, 2, 3, 4, 5, 6, 7, 8],
                        tileSize: tileSize
                    })
                })
            });
        }
    }

    function updateDateLabel(days) {
        let currentDate = new Date();
        if (days !== undefined) {
            currentDate.setDate(currentDate.getDate() + days);
        }
        let formattedDate = currentDate.toDateString();
        let label = document.getElementById('day-label');
        label.innerText = formattedDate;
    }

    function drawRectangle(lonmin, latmin, lonmax, latmax) {
        // Define the coordinates for the rectangle
        let coordinates = [
            [lonmin, latmin],
            [lonmin, latmax],
            [lonmax, latmax],
            [lonmax, latmin],
            [lonmin, latmin]
        ];

        let geometry = new ol.geom.Polygon([coordinates]);

        let feature = new ol.Feature({
            geometry: geometry
        });

        let style = new ol.style.Style({
            stroke: new ol.style.Stroke({
                color: 'blue',
                width: 2
            }),
            fill: new ol.style.Fill({
                color: 'rgba(0, 0, 255, 0.1)'
            })
        });

        feature.setStyle(style);

        let source = new ol.source.Vector({
            features: [feature]
        });

        let layer = new ol.layer.Vector({
            source: source
        });

        map.addLayer(layer);
    }

    function clearRectangles() {
        let layers = map.getLayers().getArray();

        layers.forEach(function (layer) {
            if (layer instanceof ol.layer.Vector) {
                map.removeLayer(layer);
            }
        });
    }

    function updateTimeExtentsList(layerInfo) {
        const timeExtentsList = document.getElementById('time-extents-list');
        timeExtentsList.innerHTML = ''; // Clear previous list

        if (layerInfo && layerInfo.TimeExtent && layerInfo.TimeExtent.length > 0) {
            const timeExtents = layerInfo.TimeExtent;
            const list = document.createElement('ul');

            timeExtents.forEach(extent => {
                const listItem = document.createElement('li');
                listItem.textContent = extent;
                list.appendChild(listItem);
            });

            timeExtentsList.appendChild(list);
        }
    }

    function showDownloadPanel() {
        var downloadPanel = document.getElementById('download-panel');
        downloadPanel.innerText = 'GENERATING NETCDF FILE...';
        downloadPanel.style.display = 'block';
    }

    function hideDownloadPanel() {
        var downloadPanel = document.getElementById('download-panel');
        downloadPanel.style.display = 'none';
    }

    function showFinishedPanel() {
        var finishedPanel = document.getElementById('finished-panel');
        finishedPanel.innerText = 'FINISHED GENERATING';
        finishedPanel.style.display = 'block';
        setTimeout(function() {
            finishedPanel.style.display = 'none';
        }, 5000); 
    }

    fetch(LAYERS_INFO_JSON)
    .then(response => response.json())
    .then(layersInfo => {
        layerInformation = layersInfo;

        Object.keys(layersInfo).forEach(item => {
            let option = document.createElement('option');
            option.value = item;
            option.text = item;
            select.appendChild(option);
        });
    })
    .catch(error => {
        console.error('Error loading layers_info.json file:', error);
    });

    // Map Initialization
    let base = new ol.layer.Tile({
        extent: tileExtent,
        crossOrigin: 'anonymous',
        source: new ol.source.WMTS({
            url: baseUrl,
            layer: 'BlueMarble_NextGeneration',
            format: 'image/jpeg',
            matrixSet: '500m',
            tileGrid: new ol.tilegrid.WMTS({
                origin: tileOrigin,
                resolutions: tileResolutions,
                matrixIds: matrixIds,
                tileSize: tileSize
            })
        })
    });
    let coast = new ol.layer.Tile({
        extent: tileExtent,
        crossOrigin: 'anonymous',
        source: new ol.source.WMTS({
            url: baseUrl,
            layer: 'Coastlines',
            format: 'image/png',
            matrixSet: '250m',
            tileGrid: new ol.tilegrid.WMTS({
                origin: tileOrigin,
                resolutions: tileResolutions,
                matrixIds: matrixIds,
                tileSize: tileSize
            })
        })
    });

    let refFea = new ol.layer.Tile({
        extent: tileExtent,
        crossOrigin: 'anonymous',
        source: new ol.source.WMTS({
            url: baseUrl,
            layer: 'Reference_Features',
            format: 'image/png',
            matrixSet: '250m',
            tileGrid: new ol.tilegrid.WMTS({
                origin: tileOrigin,
                resolutions: tileResolutions,
                matrixIds: matrixIds,
                tileSize: tileSize
            })
        })
    });

    let refLab = new ol.layer.Tile({
        extent: tileExtent,
        crossOrigin: 'anonymous',
        source: new ol.source.WMTS({
            url: baseUrl,
            layer: 'Reference_Labels',
            format: 'image/png',
            matrixSet: '250m',
            tileGrid: new ol.tilegrid.WMTS({
                origin: tileOrigin,
                resolutions: tileResolutions,
                matrixIds: matrixIds,
                tileSize: tileSize
            })
        })
    });

    map = new ol.Map({
        layers: [base, coast, refFea, refLab],
        target: 'map',
        view: new ol.View({
            center: [0, 0],
            maxZoom: 18,
            zoom: 1,
            extent: tileExtent,
            projection: ol.proj.get('EPSG:4326')
        })
    });

    select.addEventListener('change', function () {
        let selectedLayerIndex = select.value;
        selectedLayer = layerInformation[selectedLayerIndex];
        if (selectedLayer) {
            let slider = document.getElementById('day-slider');
            let minDays = calculateMinDays(selectedLayer.TimeExtent);
            let maxDays = calculateMaxDays(selectedLayer.TimeExtent);
            slider.min = minDays;
            slider.max = maxDays;
            slider.value = maxDays; // Reset slider to the latest taken measurement
            console.log('Layer Information:', selectedLayer);
            updateDateLabel(maxDays);
            let currentUrl = generateUrl(0, selectedLayer);

            if (vectorLayer) {
                map.removeLayer(vectorLayer);
            }
            legendContainer.innerHTML = '';

            vectorLayer = createLayer(selectedLayer, currentUrl);
            map.addLayer(vectorLayer);

            fetchLegend(selectedLayer.HorizontalLegendHref);

            if (selectedLayer.Format === LAYER_TYPES.IMAGE) {
                document.getElementById('download-button').style.display = 'block';
            } else {
                document.getElementById('download-button').style.display = 'none';
            }

            updateTimeExtentsList(selectedLayer);
        } else {
            console.error('Layer information not found for selected layer:', selectedLayerIndex);
        }
    });

    const timeButton = document.getElementById('time-button');
    timeButton.addEventListener('click', function () {
        const timeExtentsList = document.getElementById('time-extents-list');
        if (timeExtentsList.style.display === 'block') {
            timeExtentsList.style.display = 'none';
        } else {
            timeExtentsList.style.display = 'block';
        }
    });

    let slider = document.getElementById('day-slider');
    slider.addEventListener('input', function () {
        let value = parseInt(this.value);
        let currentDate = new Date();
        currentDate.setDate(currentDate.getDate() + value);
        let formattedDate = currentDate.toDateString();
        let label = document.getElementById('day-label');
        label.innerText = formattedDate;
        currentUrl = generateUrl(value, selectedLayer);

        if (vectorLayer) {
            map.removeLayer(vectorLayer);
        }

        vectorLayer = createLayer(selectedLayer, currentUrl);
        map.addLayer(vectorLayer);
    });

    document.getElementById('download-button').addEventListener('click', function () {
        let missingElementsPanel = document.getElementById('missing-panel');
        missingElementsPanel.style.display = 'none'
        lonmin = parseFloat(document.getElementById('lonmin').value);
        latmin = parseFloat(document.getElementById('latmin').value);
        lonmax = parseFloat(document.getElementById('lonmax').value);
        latmax = parseFloat(document.getElementById('latmax').value);
        let missingElements = [];

        if (!startDate) missingElements.push('Start Date');
        if (!endDate) missingElements.push('End Date');
        if (isNaN(lonmin)) missingElements.push('Longitude Minimum');
        if (isNaN(latmin)) missingElements.push('Latitude Minimum');
        if (isNaN(lonmax)) missingElements.push('Longitude Maximum');
        if (isNaN(latmax)) missingElements.push('Latitude Maximum');

        if (missingElements.length > 0) {
            missingElementsPanel.innerHTML = 'Missing Elements: ' + missingElements.join(', ');
            missingElementsPanel.style.display = 'block';
            return;
        }

        showDownloadPanel();

        let data = {
            layer: selectedLayer.Layer,
            metadataHref: selectedLayer.MetadataHref,
            startDate: startDate,
            endDate: endDate,
            lonmin: lonmin,
            latmin: latmin,
            lonmax: lonmax,
            latmax: latmax
        };

        fetch('http://localhost:5000/save_data', { 
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data) 
            })
            .then(response => {
                if (response.ok) {
                    console.log('Data sent successfully');
                    // you can handle the response here
                    hideDownloadPanel(); 
                    showFinishedPanel();
                } else {
                    console.error('Failed to send data');
                    hideDownloadPanel(); 
                }
            })
            .catch(error => {
                console.error('Error:', error);
                hideDownloadPanel(); 
            });
    });
    
    document.getElementById('view-button').addEventListener('click', function () {
        lonmin = parseFloat(document.getElementById('lonmin').value);
        latmin = parseFloat(document.getElementById('latmin').value);
        lonmax = parseFloat(document.getElementById('lonmax').value);
        latmax = parseFloat(document.getElementById('latmax').value);

        if (isNaN(lonmin) || isNaN(latmin) || isNaN(lonmax) || isNaN(latmax)) {
            alert('Please enter valid numerical values for coordinates.');
            return;
        }

        clearRectangles();

        drawRectangle(lonmin, latmin, lonmax, latmax);
    });

    document.getElementById("clear-button").addEventListener('click', function() {
        clearRectangles();
    });

    document.getElementById('start-date').addEventListener('change', saveDates);

    document.getElementById('end-date').addEventListener('change', saveDates);

    const searchInput = document.getElementById('layer-search');
    searchInput.addEventListener('input', function () {
        const searchText = searchInput.value.toLowerCase();
        const options = select.options;
        for (let i = 0; i < options.length; i++) {
            const option = options[i];
            const optionText = option.text.toLowerCase();
            if (optionText.includes(searchText)) {
                option.style.display = 'block';
            } else {
                option.style.display = 'none';
            }
        }
    });

    var displayFeatureInfo = function (event) {
        var features = map.getFeaturesAtPixel(event.pixel);
        if (features.length === 0) {
          info.innerText = '';
          info.style.opacity = 0;
          return;
        }
        var properties = features[0].getProperties();
        info.innerText = JSON.stringify(properties, null, 2);
        info.style.opacity = 1;
      };
      map.on('pointermove', displayFeatureInfo);  
};
