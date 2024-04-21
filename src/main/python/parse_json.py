import json
from tqdm import tqdm
import networkx as nx
from utils import TAXONS_TO_KEEP, TAXON_RANKS, IUCNS

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
            if (json_data["id"] == "Q5173"):
                G.add_edge("Q5174", json_data["id"])
                parents = []
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
                # G.nodes[json_data["id"]]["site_link"] = json_data["sitelinks"].get("enwiki") != None

            filtered_data = {}
            if json_data["sitelinks"].get("enwiki"):
                filtered_data["site_link"] = json_data["sitelinks"]["enwiki"]["title"]
            else:
                filtered_data["site_link"] = False

            rank_claims = json_data["claims"].get("P105")
            ranks = []
            preferred_rank = None
            if rank_claims:
                for rank_prop in rank_claims:
                    if rank_prop.get("rank") == "deprecated":
                        continue
                    rank_snak = rank_prop["mainsnak"]
                    if (rank_snak.get("datavalue") == None):
                        if rank_prop.get("rank") == "preferred":
                            # no rank is preferred so we remove everything
                            ranks = []
                            preferred_rank = None
                            break
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

            vernacular_claims = json_data["claims"].get("P1843")
            vernaculars = []
            preferred_vernacular = None
            if vernacular_claims:
                for vernacular_prop in vernacular_claims:
                    if vernacular_prop.get("rank") == "deprecated":
                        continue
                    vernacular_snak = vernacular_prop["mainsnak"]
                    if (vernacular_snak.get("datavalue") == None):
                        continue
                    if vernacular_prop.get("rank") == "preferred":
                        preferred_vernacular = vernacular_snak["datavalue"]["value"]["text"]
                    vernacular = vernacular_snak["datavalue"]["value"]["text"]
                    vernaculars.append(vernacular)
                if vernaculars:
                    if preferred_vernacular:
                        filtered_data["vernacular"] = preferred_vernacular
                    else:
                        filtered_data["vernacular"] = vernaculars[0]

            scientific_claims = json_data["claims"].get("P225")
            scientifics = []
            preferred_scientific = None
            if scientific_claims:
                for scientific_prop in scientific_claims:
                    if scientific_prop.get("rank") == "deprecated":
                        continue
                    scientific_snak = scientific_prop["mainsnak"]
                    if (scientific_snak.get("datavalue") == None):
                        continue
                    if scientific_prop.get("rank") == "preferred":
                        preferred_scientific = scientific_snak["datavalue"]["value"]
                    scientific = scientific_snak["datavalue"]["value"]
                    scientifics.append(scientific)
                if scientifics:
                    if preferred_scientific:
                        filtered_data["scientific"] = preferred_scientific
                    else:
                        filtered_data["scientific"] = scientifics[0]

            iucn_claims = json_data["claims"].get("P141")
            iucns = []
            preferred_iucn = None
            if iucn_claims:
                for iucn_prop in iucn_claims:
                    if iucn_prop.get("rank") == "deprecated":
                        continue
                    iucn_snak = iucn_prop["mainsnak"]
                    if (iucn_snak.get("datavalue") == None):
                        continue
                    if iucn_prop.get("rank") == "preferred":
                        preferred_iucn = TAXONS_TO_KEEP.get(iucn_snak["datavalue"]["value"]["id"])
                    iucn_id = iucn_snak["datavalue"]["value"]["id"]
                    iucn = IUCNS.get(iucn_id)
                    if iucn:
                        iucns.append(iucn)
                    else:
                        print("IUCN not found", iucn_id)
                if iucns:
                    if preferred_iucn:
                        filtered_data["iucn"] = preferred_iucn
                    else:
                        filtered_data["iucn"] = iucns[0]


            image_claims = json_data["claims"].get("P18")
            if image_claims:
                image_snak = image_claims[0]["mainsnak"]
                if image_snak.get("datavalue") and image_snak["datavalue"]["type"] == "string":
                    image = image_snak["datavalue"]["value"]
                    filtered_data["image"] = image

            data[json_data["id"]] = filtered_data

            # Update progress bar
            progress_bar.update(1)

        # Close progress bar after completion
        progress_bar.close()
        print(mul_rank)
        
        # Remove edge that shouldn't be there between a genus and its
        # subfamily
        G.remove_edge('Q123912920', 'Q2708291')
        G.remove_edge('Q124289021', 'Q124289021')
        print("Making animalia tree...")
        connected_to_animalia = nx.dfs_tree(G, "Q729")
        for node in list(G):
            if node not in connected_to_animalia:
                G.remove_node(node)
        topo_sort = list(nx.topological_sort(G))
        for i, node in enumerate(topo_sort):
            data[node]["height"] = i
        animalia_tree = nx.DiGraph()
        animalia_tree.add_node("Q729")
        for node in topo_sort:
            if node not in data:
                continue
            animalia_tree.add_node(node)
            for key in data[node]:
                animalia_tree.nodes[node][key] = data[node][key]
            max_height = -1
            max_height_node = None
            for parent in G.predecessors(node):
                if parent in data:
                    if data[parent]["height"] > max_height:
                        max_height = data[parent]["height"]
                        max_height_node = parent
            if max_height_node:
                animalia_tree.add_edge(max_height_node, node)
                
        # for node in animalia_tree.nodes():
        #     for key in data[node]:
        #         animalia_tree.nodes[node][key] = data[node][key]
        print(animalia_tree.nodes["Q729"])
        print(animalia_tree.nodes["Q140"])
        DOUBLE_TAXONS_ANIMALIA = []
        DOUBLE_TAXONS_ANIMALIA_WIKI = []
        for taxon_info in DOUBLE_TAXONS:
            taxon = taxon_info["id"]
            if animalia_tree.has_node(taxon):
                DOUBLE_TAXONS_ANIMALIA.append(taxon)
                if animalia_tree.nodes[taxon]["site_link"]:
                    DOUBLE_TAXONS_ANIMALIA_WIKI.append(taxon)
        # print("DOUBLE_TAXONS_ANIMALIA", len(DOUBLE_TAXONS_ANIMALIA), DOUBLE_TAXONS_ANIMALIA)
        # print("DOUBLE_TAXONS_ANIMALIA_WIKI", len(DOUBLE_TAXONS_ANIMALIA_WIKI), DOUBLE_TAXONS_ANIMALIA_WIKI)

        # delete problematic taxons (by removing their rank)
        skip_taxons = []
        animalia_tree.nodes["Q3748423"].pop("rank")
        animalia_tree.nodes["Q4000124"].pop("rank")
        animalia_tree.nodes["Q822890"].pop("rank")
        animalia_tree.nodes["Q3111386"].pop("rank")
        animalia_tree.nodes["Q21224524"].pop("rank")
        animalia_tree.nodes["Q343460"].pop("rank")
        animalia_tree.nodes["Q47544996"].pop("rank")
        
        # remove all zoa phylums
        animalia_tree.nodes["Q2698547"].pop("rank")
        animalia_tree.nodes["Q1407833"].pop("rank")
        animalia_tree.nodes["Q2503841"].pop("rank")
        animalia_tree.nodes["Q27207"].pop("rank")
        animalia_tree.nodes["Q48918"].pop("rank")
        for node in list(animalia_tree.successors("Q48918")):
            animalia_tree.remove_edge("Q48918", node)
            animalia_tree.add_edge("Q194257", node)
        
        animalia_tree.nodes["Q2072138"]["site_link"] = "Myxiniformes"
        animalia_tree.nodes["Q15100334"]["site_link"] = "Myxini"
        
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
                    min_value = all_filter_ranks[0]
                    for rank in all_filter_ranks:
                        taxon_rank = TAXON_RANKS[rank]
                        diff = abs((taxon_rank // 10) * taxon_rank - taxon_rank)
                        if diff < min_diff:
                            min_diff = diff
                            min_value = rank
                    animalia_tree.nodes[taxon]["rank"] = min_value

        print(number_problem)
            
        return animalia_tree

if __name__ == "__main__":
    file_path = 'results/json-all-taxon.json'
    animalia_tree = parse_large_json_file(file_path)
    nx.write_graphml_lxml(animalia_tree, "results/animalia_tree.graphml")