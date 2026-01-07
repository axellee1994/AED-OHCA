#### Setting up environments for the codes to run
For .py files, you can install the required packages by running `pip install -r requirements.txt`, ensure that you run this command in the same directory as requirement.txt file

For .ipynb files, it is best to create a new conda environment:
```
conda create -n geospatial_env
conda activate geospatial_env
conda intall pandas geopandas geopy openpyxl msoffcrypto
```
If you would like to run the codes in the Archive_codes folder:
```conda install qgis --channel conda-forge```
This will allow you to run the codes that use QGIS for geospatial analysis.

src/describing_datasets/describing_paros.ipynb contains the 

To read the paros dataset with the ipynb files (eg. describing_paros.ipynb), create a .env file with this line: 
PAROS_PASSWORD = "replace_with_actual_password"

Place the .env in the root directory (i.e. Mobile-AED-Study)

The python script, postal_to_coordinates.py in src/script/. requires an API key. Add this line to the .env file:

API_KEY = "Your_google_cloud_API_KEY"

