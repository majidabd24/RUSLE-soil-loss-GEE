# RUSLE-soil-loss-GEE
# RUSLE Soil Loss Estimation Using Google Earth Engine

## Description
This script estimates soil loss using the Revised Universal Soil Loss Equation (RUSLE) in Google Earth Engine (GEE). It calculates the mean annual soil loss based on various factors including rainfall erosivity, soil erodibility, slope, land cover, and erosion management practices.

The formula used is:
\[ A = R \times K \times LS \times C \times P \]
Where:
- **A** - Mean annual soil loss (metric tonnes/ha/year)
- **R** - Rainfall erosivity factor
- **K** - Soil erodibility factor
- **LS** - Slope length and steepness factor
- **C** - Land cover and management factor
- **P** - Erosion management factor

## Dependencies
- Google Earth Engine (GEE)
- JavaScript (for the GEE Code Editor)

## Usage
1. Clone this repository to your local machine or open the script in the GEE Code Editor.
2. Ensure you have access to the required datasets in Google Earth Engine.
3. Modify the area of interest (AOI) and date ranges as necessary for your analysis.

## How to Run the Script
1. Open the Google Earth Engine Code Editor: [GEE Code Editor](https://code.earthengine.google.com/)
2. Copy and paste the script into the editor.
3. Adjust the parameters as needed, particularly the area of interest and date range.
4. Click on the "Run" button to execute the script and visualize the results.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Contact Information
For questions or feedback, please contact:
**Name**: Majid Abdalla  
**Email**: majidmonim@gmail.com  A project for estimating soil loss using the RUSLE model in Google Earth Engine.
