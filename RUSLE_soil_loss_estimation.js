// Define the ROI
var roi = ee.FeatureCollection("projects/ee-majidmonim2/assets/AZB_watershed");

// Load Landsat 8 imagery
var landsat = ee.ImageCollection('LANDSAT/LC08/C01/T1_TOA')
  .filterBounds(roi)
  .filterDate('2019-01-01', '2019-12-31')
  .median();

// Load Sentinel-2 imagery
var sentinel2 = ee.ImageCollection('COPERNICUS/S2')
  .filterBounds(roi)
  .filterDate('2019-01-01', '2019-12-31')
  .median();

// Load MODIS imagery
var modis = ee.ImageCollection('MODIS/006/MOD09A1')
  .filterBounds(roi)
  .filterDate('2019-01-01', '2019-12-31')
  .median();

// Merge all image collections
var imagery = ee.Image.cat([
  landsat.select(['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B10', 'B11']),
  sentinel2.select(['B2', 'B3', 'B4', 'B8', 'B11', 'B12']),
  modis.select(['sur_refl_b01', 'sur_refl_b02', 'sur_refl_b06', 'sur_refl_b07'])
]);

// Calculate NDVI
var ndvi = imagery.normalizedDifference(['B5', 'B4']).rename('NDVI');

// Load DEM
var dem = ee.Image('USGS/SRTMGL1_003')
  .clip(roi);

// Calculate slope in degrees
var slope = ee.Terrain.slope(dem)
  .select('slope');

// Load annual rainfall data
var rainfall = ee.ImageCollection('UCSB-CHG/CHIRPS/PENTAD')
  .filterBounds(roi)
  .filterDate('2019-01-01', '2019-12-31')
  .sum();

// Load soil texture data
var soilTexture = ee.Image("OpenLandMap/SOL/SOL_TEXTURE-CLASS_USDA-TT_M/v02")
  .clip(roi);

// Calculate R factor
var R_factor = rainfall;

// Calculate LS factor
var LS_factor = ee.Terrain.slope(dem)
  .tan()
  .multiply(ee.Image.constant(0.0896))
  .add(1)
  .multiply(ndvi.divide(0.0896))
  .rename('LS');

// Calculate K factor (soil erodibility)
var K_factor = soilTexture.expression(
  '(0.15 + 0.15 * b(0))', {
    'constant': soilTexture
  }
).rename('K');

// Calculate C factor (cover management factor)
var C_factor = ee.Image(0.01);

// Combine factors to calculate soil erosion
var erosion = R_factor.multiply(K_factor).multiply(LS_factor).multiply(C_factor)
  .rename('erosion');

// Define thresholds for soil degradation classes
var lowThreshold = 50;
var highThreshold = 150;

// Create soil degradation map
var soilDegradation = erosion.expression(
  'b() < low ? 0 : (b() < high ? 1 : 2)', {
    'low': lowThreshold,
    'high': highThreshold
  }
).rename('soil_degradation');

// Clip the soil degradation map to the ROI
soilDegradation = soilDegradation.clip(roi);

// Define visualization parameters for soil degradation map
var degradationVis = {
  min: 0,
  max: 2,
  palette: ['yellow', 'orange', 'red']
};

// Classify the erosion map into three classes
var erosionClasses = erosion
  .gt(0).multiply(1)
  .add(erosion.gt(10).multiply(2))
  .add(erosion.gt(50).multiply(3))
  .rename('erosion_classes');

// Define visualization parameters for erosion map
var erosionVis = {
  min: 1,
  max: 3,
  palette: ['green', 'yellow', 'red']
};

// Add the soil degradation layer to the map
Map.addLayer(soilDegradation, degradationVis, 'Soil Degradation');

// Add the erosion layer to the map
Map.addLayer(erosionClasses, erosionVis, 'Annual Soil Erosion (Classes)');

// Export the soil degradation map to Google Drive
Export.image.toDrive({
  image: soilDegradation,
  description: 'soil_degradation_map',
  region: roi,
  scale: 30
});

// Export the erosion map to Google Drive
Export.image.toDrive({
  image: erosionClasses,
  description: 'annual_soil_erosion_classes',
  region: roi,
  scale: 30
});

