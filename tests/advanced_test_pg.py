# coding=utf-8
import requests
import json
import sys
from time import time
import xarray as xr
import os

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
            output_rel_path = response_data['output']
            full_path = output_rel_path
            print('Result stored in:', response_data['output'])
            print('Full path (NetCDF):', full_path)

            # Try to open and inspect the NetCDF file
            try:
                ds = xr.open_dataset(full_path)
                print("\n✅ Opened NetCDF dataset successfully.")
                print(ds)  # summary
                print("\nDimensions:", ds.dims)
                print("Data variables:", list(ds.data_vars))
                # Optionally print shape of first variable
                if ds.data_vars:
                    first_var = list(ds.data_vars)[0]
                    print(f"Shape of '{first_var}':", ds[first_var].shape)
            except Exception as e:
                print("❌ Failed to open NetCDF file with xarray:", e)

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
