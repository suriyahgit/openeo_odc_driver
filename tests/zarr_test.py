# coding=utf-8
import requests
import json
import sys
from time import time
import xarray as xr
import os
import zipfile
import tempfile

def read_zarr_from_zip(zip_path):
    """Extract and read zarr from zip file"""
    with tempfile.TemporaryDirectory() as temp_dir:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        zarr_folder_name = os.path.splitext(os.path.basename(zip_path))[0]
        zarr_path = os.path.join(temp_dir, zarr_folder_name)
        return xr.open_zarr(zarr_path)

def inspect_dataset(ds, format_type):
    """Common inspection for both NetCDF and Zarr datasets"""
    print(f"\n✅ Opened {format_type} dataset successfully.")
    print(ds)  # summary
    print("\nDimensions:", ds.dims)
    print("Data variables:", list(ds.data_vars))
    if ds.data_vars:
        first_var = list(ds.data_vars)[0]
        print(f"Shape of '{first_var}':", ds[first_var].shape)
    # Additional checks specific to your data
    if 'time' in ds.dims:
        print("Time range:", ds.time.values.min(), "to", ds.time.values.max())
    if 'bands' in ds.dims:
        print("Available bands:", ds.bands.values)

start = time()
if len(sys.argv) != 2:
    raise ValueError('Please provide process graph.')

process_graph = sys.argv[1]
with open(process_graph) as f:
    d = json.load(f)

res = requests.post('http://0.0.0.0:5000/graph', json=d)

# Debug output
print("Status Code:", res.status_code)
print("Headers:", res.headers)
print("Content-Type:", res.headers.get('content-type', 'unknown'))
print("Raw Response:", res.text[:500])  # Print first 500 chars to avoid huge outputs

try:
    response_data = res.json()
    
    # Handle different response formats
    if isinstance(response_data, list) and len(response_data) > 0 and isinstance(response_data[0], dict):
        error_info = response_data[0]
        print("Error:", error_info.get('error', 'Unknown error'))
        if 'output' in error_info:
            print("Output path:", error_info['output'])

    elif isinstance(response_data, dict):
        if 'output' in response_data:
            output_path = response_data['output']
            print('Result stored in:', output_path)
            
            # Determine file type and read accordingly
            if output_path.endswith('.nc'):
                print('Detected NetCDF format')
                try:
                    ds = xr.open_dataset(output_path)
                    inspect_dataset(ds, "NetCDF")
                except Exception as e:
                    print("❌ Failed to open NetCDF file with xarray:", e)
                    
            elif output_path.endswith('.zarr.zip'):
                print('Detected Zarr format (zipped)')
                try:
                    ds = read_zarr_from_zip(output_path)
                    inspect_dataset(ds, "Zarr")
                except Exception as e:
                    print("❌ Failed to open Zarr file with xarray:", e)
                    
            elif output_path.endswith('.json'):  # For STAC outputs
                print('Detected STAC metadata')
                with open(output_path) as f:
                    stac_data = json.load(f)
                print("STAC collection ID:", stac_data.get('id'))
                
            else:
                print('Unknown output format:', os.path.splitext(output_path)[1])

        elif 'error' in response_data:
            print('Error:', response_data['error'])
        else:
            print('Unexpected response format:', response_data)

    else:
        print('Unexpected response type:', type(response_data), response_data)

except ValueError as e:
    print('Failed to parse JSON response:', e)
    print('Raw response:', res.text)

print('Elapsed time: ', time() - start)