# Taxonomicle data import

Maven project made by modifying the examples in https://github.com/Wikidata/Wikidata-Toolkit for the purposes of the project.

## Build the dataset

Several pieces of code need to be executed to build the dataset. Here are the various steps :

- Download a `wikidata` dump in `json` format:
```bash
# You might want to launch this in a tmux (or other) as this is a ~100 GB file
cd dumps && wget https://dumps.wikimedia.org/other/wikibase/wikidatawiki/latest-all.json.gz
```
- Launch the `Java` code (extracts only taxonomic data from the database):
```bash
mvn exec:java -Dexec.mainClass="com.taxonomicle.data_import.LocalDumpFileExample"
```
- Launch the python codes `parse_json.py` then `transform_graph.py` then `analyze_pruned_graph.py` then `graph_to_json.py`.
- Launch the `javascript` code `getDescriptions.js` then `upload.js` (with `npm run` in the `js` folder). The last one needs an instance of `PocketBase` made with the website repo launched.