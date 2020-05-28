# from pyramid.paster import bootstrap, setup_logging
# from sys import argv

# with bootstrap(a.configuration_path) as env, env['request'].tm:

# load database
# get 

'''
Get all generator assets
Build graph
For each generator asset, get connections
For each connection in a generator asset, add an edge using a networkx.Graph, using busIds as graph node ids
Define a function that determines whether asset2 is downstream of asset1
Compute the shortest path between asset1 and each generator using a networkx shortest path algorithm (call it GENERATOR-ASSET1)
Compute the shortest path between asset1 and asset2 (call it ASSET1-ASSET2)
Determine whether GENERATOR-ASSET1 and ASSET2-ASSET2 overlap
If they overlap, then asset2 is downstream of asset1
Get all line and meter assets
Given an asset id, find all line and meter assets that are downstream of that asset
'''

# Pre-compute these values in the update-risks script
# For each risk, store downstream line ids and meter ids
