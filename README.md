# Taxonomicle data import

Maven project made by modifying the examples in https://github.com/Wikidata/Wikidata-Toolkit for the purposes of the project.

## Build the dataset

Several pieces of code need to be executed to build the dataset. Here are the various steps :

- Download a `wikidata` dump in `json` format and change the path to it in `LocalDumpFileExample.java` then execute this file
- Launch the python codes `parse_json.py` then `transform_graph.py` then `analyze_pruned_graph.py` then `graph_to_json.py`
- Launch the `javascript` code `getImageLinks.js` then `upload.js`. The last one needs an instance of `PocketBase` made with the website repo launched