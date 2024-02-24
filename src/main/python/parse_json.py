import json
from tqdm import tqdm
import networkx as nx

TAXONS_TO_KEEP = {
    "Q38348": "phylum",
    "Q164280": "subfamily",
    "Q227936": "tribe",
    "Q5867051": "subclass",
    "Q2889003": "infraorder",
    "Q35409": "family",
    "Q3238261": "subgenus",
    "Q5868144": "superorder",
    "Q37517": "class",
    "Q3504061": "superclass",
    "Q2752679": "subkingdom",
    "Q2136103": "superfamily",
    "Q2111790": "superphylum",
    "Q7432": "species",
    "Q68947": "subspecies",
    "Q34740": "genus",
    "Q1153785": "subphylum",
    "Q3965313": "subtribe",
    "Q36602": "order",
    "Q2007442": "infraclass",
    "Q3150876": "infrakingdon",
    "Q6311258": "pavorder",
    "Q36732": "kindgom",
    "Q5867959": "suborder"
}

DOUBLE_TAXONS = []

def parse_large_json_file(file_path):
    data = {}
    G = nx.DiGraph()
    # Get the total number of lines in the file for progress tracking
    total_lines = sum(1 for line in open(file_path))
    mul_rank = 0

    with open(file_path, 'r') as f:
        # Initialize tqdm progress bar
        progress_bar = tqdm(total=total_lines)
        first = True

        # Iterate over each line in the file
        for line in f:
            if (len(line) < 3):
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

            filtered_data = {}
            filtered_data["site_link"] = json_data["sitelinks"].get("enwiki") != None

            rank_claims = json_data["claims"].get("P105")
            ranks = []
            if rank_claims:
                for rank_prop in rank_claims:
                    rank_snak = rank_prop["mainsnak"]
                    if (rank_snak.get("datavalue") == None):
                        continue
                    rank_id = rank_snak["datavalue"]["value"]["id"]
                    rank = TAXONS_TO_KEEP.get(rank_id)
                    if rank:
                        ranks.append(rank)
                if len(ranks) > 1:
                    mul_rank += 1
                    DOUBLE_TAXONS.append(json_data["id"])
                if ranks:
                    filtered_data["rank"] = ranks[0]
            data[json_data["id"]] = filtered_data

            # Update progress bar
            progress_bar.update(1)

        # Close progress bar after completion
        progress_bar.close()
        print(mul_rank)
        print("Making animalia tree...")
        animalia_tree = nx.bfs_tree(G, "Q729", reverse=False, depth_limit=None, sort_neighbors=None)
        for node in animalia_tree.nodes():
            for key in data[node]:
                animalia_tree.nodes[node][key] = data[node][key]
        print(animalia_tree.nodes["Q729"])
        DOUBLE_TAXONS_ANIMALIA = []
        DOUBLE_TAXONS_ANIMALIA_WIKI = []
        for taxon in DOUBLE_TAXONS:
            if animalia_tree.has_node(taxon):
                DOUBLE_TAXONS_ANIMALIA.append(taxon)
                if animalia_tree.nodes[taxon]["site_link"]:
                    DOUBLE_TAXONS_ANIMALIA_WIKI.append(taxon)
        print("DOUBLE_TAXONS_ANIMALIA", len(DOUBLE_TAXONS_ANIMALIA), DOUBLE_TAXONS_ANIMALIA)
        print("DOUBLE_TAXONS_ANIMALIA_WIKI", len(DOUBLE_TAXONS_ANIMALIA_WIKI), DOUBLE_TAXONS_ANIMALIA_WIKI)
        return animalia_tree

if __name__ == "__main__":
    file_path = 'results/json-all-taxon.json'
    animalia_tree = parse_large_json_file(file_path)
    nx.write_graphml_lxml(animalia_tree, "results/animalia_tree.graphml")