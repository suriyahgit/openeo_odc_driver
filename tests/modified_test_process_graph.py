# coding=utf-8
# Author: Claus Michele - Eurac Research
import requests
import json
import sys
from time import time
import os

start = time()
if len(sys.argv) != 2:
    raise ValueError('Please provide process graph.')

process_graph = sys.argv[1]
with open(process_graph) as f:
    d = json.load(f)

try:
    res = requests.post('http://localhost:5000/graph', json=d, timeout=60)
    res.raise_for_status()  # Raises exception for HTTP errors
    
    print(res)
    print(res.headers['content-type'])
    
    # Handle different response types
    if res.headers['content-type'] == 'application/json':
        try:
            result = res.json()
            if 'output' in result:
                print('Result:', result['output'])
            else:
                print('Processing completed. Output:', result)
        except ValueError:
            print('Response content:', res.text)
    else:
        print('Non-JSON response:', res.text)
    
    print('Elapsed time: ', time() - start)

except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
    print('Elapsed time: ', time() - start)
    sys.exit(1)