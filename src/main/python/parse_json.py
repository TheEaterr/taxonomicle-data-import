import json
from tqdm import tqdm
import networkx as nx

def parse_large_json_file(file_path):
    G = nx.DiGraph()
    # Get the total number of lines in the file for progress tracking
    total_lines = sum(1 for line in open(file_path))

    with open(file_path, 'r') as f:
        # Initialize tqdm progress bar
        progress_bar = tqdm(total=total_lines)
        first = True

        # Iterate over each line in the file
        for line in f:
            if (len(line) < 3):
                print(line)
                progress_bar.update(1)
                continue

            # Parse JSON from the line
            if line[-2] == ",":
                json_data = json.loads(line[:-2])
            else:
                json_data = json.loads(line)

            # Perform desired operations with the JSON data
            # Example: print(json_data)
            # print(json_data)
            parents = json_data["claims"]["P171"]
            for parent in parents:
                parent_snak = parent["mainsnak"]
                if (parent_snak.get("datavalue") == None):
                    continue
                parent_id = parent_snak["datavalue"]["value"]["id"]

                G.add_edge(parent_id, json_data["id"])
                G.nodes[json_data["id"]]["site_link"] = json_data["sitelinks"].get("enwiki") != None

            # Update progress bar
            progress_bar.update(1)

        # Close progress bar after completion
        progress_bar.close()
        print("Making animalia tree...")
        return nx.bfs_tree(G, "Q729", reverse=False, depth_limit=None, sort_neighbors=None)

if __name__ == "__main__":
    file_path = 'results/json-all-taxon.json'
    animalia_tree = parse_large_json_file(file_path)
    nx.write_graphml_lxml(animalia_tree, "results/animalia_tree.graphml")