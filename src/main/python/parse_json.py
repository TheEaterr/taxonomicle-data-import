import json
from tqdm import tqdm
import networkx as nx
from utils import TAXONS_TO_KEEP, TAXON_RANKS

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
            has_preferred_parent = False
            for parent in parents:
                if parent.get("rank") == "preferred":
                    has_preferred_parent = True
            for parent in parents:
                if parent.get("rank") == "deprecated":
                    continue
                if has_preferred_parent and parent.get("rank") != "preferred":
                    continue
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
            preferred_rank = None
            if rank_claims:
                for rank_prop in rank_claims:
                    if rank_prop.get("rank") == "deprecated":
                        continue
                    rank_snak = rank_prop["mainsnak"]
                    if (rank_snak.get("datavalue") == None):
                        continue
                    if rank_prop.get("rank") == "preferred":
                        preferred_rank = TAXONS_TO_KEEP.get(rank_snak["datavalue"]["value"]["id"])
                    rank_id = rank_snak["datavalue"]["value"]["id"]
                    rank = TAXONS_TO_KEEP.get(rank_id)
                    if rank:
                        ranks.append(rank)
                if len(ranks) > 1:
                    mul_rank += 1
                    DOUBLE_TAXONS.append({"id": json_data["id"], "ranks": ranks})
                if ranks:
                    if preferred_rank:
                        filtered_data["rank"] = preferred_rank
                    else:
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
        for taxon_info in DOUBLE_TAXONS:
            taxon = taxon_info["id"]
            if animalia_tree.has_node(taxon):
                DOUBLE_TAXONS_ANIMALIA.append(taxon)
                if animalia_tree.nodes[taxon]["site_link"]:
                    DOUBLE_TAXONS_ANIMALIA_WIKI.append(taxon)
        print("DOUBLE_TAXONS_ANIMALIA", len(DOUBLE_TAXONS_ANIMALIA), DOUBLE_TAXONS_ANIMALIA)
        print("DOUBLE_TAXONS_ANIMALIA_WIKI", len(DOUBLE_TAXONS_ANIMALIA_WIKI), DOUBLE_TAXONS_ANIMALIA_WIKI)

        # delete problematic taxons (by removing their rank)
        skip_taxons = []
        animalia_tree.nodes["Q3748423"].pop("rank")
        animalia_tree.nodes["Q4000124"].pop("rank")
        animalia_tree.nodes["Q822890"].pop("rank")
        animalia_tree.nodes["Q3111386"].pop("rank")
        animalia_tree.nodes["Q21224524"].pop("rank")
        animalia_tree.nodes["Q343460"].pop("rank")
        skip_taxons.append("Q822890")
        # animalia_tree.nodes["Q26214"]["rank"] = "infraphylum"
        # skip_taxons.append("Q26214")

        number_problem = 0
        for taxon_info in DOUBLE_TAXONS:    
            taxon = taxon_info["id"]
            ranks = taxon_info["ranks"]
            if animalia_tree.has_node(taxon) and taxon not in skip_taxons:
                sucessors = list(animalia_tree.successors(taxon))
                predecessor_rank = animalia_tree.nodes[list(animalia_tree.predecessors(taxon))[0]].get("rank")
                pred_filter_ranks = []
                for rank in ranks:
                    if predecessor_rank is None or TAXON_RANKS[rank] > TAXON_RANKS[predecessor_rank]:
                        pred_filter_ranks.append(rank)
                    else:
                        number_problem += 1
                all_filter_ranks = []
                problem_succs = []
                for rank in pred_filter_ranks:
                    problem = False
                    for succ in sucessors:
                        if not animalia_tree.nodes[succ]["site_link"]:
                            continue
                        succ_rank = animalia_tree.nodes[succ].get("rank")
                        if succ_rank is not None and TAXON_RANKS[rank] >= TAXON_RANKS[succ_rank]:
                            problem = True
                            problem_succs.append(succ)
                    if problem:
                        number_problem += 1
                    else:
                        all_filter_ranks.append(rank)
                if len(all_filter_ranks) == 0:
                    print("Big problem with ", taxon, " having ", list(animalia_tree.predecessors(taxon))[0], " and ", problem_succs)
                    animalia_tree.nodes[taxon].pop("rank")
                else:
                    min_diff = 100
                    min_value = None
                    for rank in all_filter_ranks:
                        taxon_rank = TAXON_RANKS[rank]
                        diff = abs((taxon_rank // 10) * taxon_rank - taxon_rank)
                        if diff < min_diff:
                            min_diff = diff
                            min_value = rank
                    animalia_tree.nodes[taxon]["rank"] = rank
                    # print("Chose ", rank, " for taxon ", taxon)
        print(number_problem)

        return animalia_tree

if __name__ == "__main__":
    file_path = 'results/json-all-taxon.json'
    animalia_tree = parse_large_json_file(file_path)
    nx.write_graphml_lxml(animalia_tree, "results/animalia_tree.graphml")