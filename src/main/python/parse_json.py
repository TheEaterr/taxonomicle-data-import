import json
from tqdm import tqdm
import networkx as nx
from utils import TAXONS_TO_KEEP, TAXON_RANKS, IUCNS, removeAndReconnect

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

        # Remove edge that shouldn't be there between a suborder and its
        # infraorder
        G.remove_edge('Q21228934', 'Q1008888')
        
        # Recreate some taxons that should be there (not in the data
        # because noted as fossils)
        data["Q1049466"] = {
            "site_link": "Trachiniformes",
            "scientific": "Trachinoidei",
            "image": "Parapercis hexophtalma 1.jpg",
            "rank": "suborder"
        }
        G.add_edge('Q127595', 'Q1049466')
        data["Q2370888"] = {
            "site_link": False,
            "scientific": "Gadinae",
            "rank": "subfamily"
        }
        G.add_edge('Q208028', 'Q2370888')
        data["Q140260"] = {
            "site_link": "Pegasidae",
            "scientific": "Pegasidae",
            "image": "Eurypegasus draconis.JPG",
            "rank": "family"
        }
        G.add_edge('Q13173180', 'Q140260')
        data["Q2447537"] = {
            "site_link": "Trachyrincinae",
            "scientific": "Trachyrincinae",
            "rank": "subfamily",
            "image": "Trachyrincus longirostris (Slender unicorn rattail).gif"
        }
        G.add_edge('Q766678', 'Q2447537')
        data["Q5055196"] = {
            "site_link": "Cavolinioidea",
            "scientific": "Cavolinioidea",
            "image": "Sea butterfly.jpg",
            "rank": "superfamily"
        }
        G.add_edge("Q5414457", "Q5055196")
        data["Q7188098"] = {
            "site_link": "Phreatoicidea",
            "scientific": "Phreatoicidea",
            "rank": "suborder",
            "image": "Eoph MagelaT site2.jpg"
        }
        G.add_edge("Q206338", "Q7188098")
        # it's a redirect page
        data["Q3863014"]["site_link"] = "Uramphisopus"
        data["Q2160533"] = {
            "site_link": "Priapulimorphida",
            "scientific": "Priapulimorphida",
            "rank": "order",
            "image": "Priapulus caudatus FZ.png"
        }
        G.add_edge("Q5184", "Q2160533")
        G.add_edge("Q282487", "Q130910")
        data["Q3269358"] = {
            "site_link": "Discinidae",
            "scientific": "Discinidae",
            "rank": "family",
            "image": "Discinisca lamellosa 001.png"
        }
        G.add_edge("Q5281459", "Q3269358")
        data["Q4020097"] = {
            "site_link": "Cypridinidae",
            "scientific": "Cypridinidae",
            "rank": "family",
            "image": "CypridinaMediterranea.png"
        }
        G.add_edge("Q11842665", "Q4020097")
        data["Q16989943"] = {
            "site_link": False,
            "scientific": "Trigoniinae",
            "rank": "subfamily",
        }
        G.add_edge("Q1797614", "Q16989943")
        G.add_edge("Q16833565", "Q3389440")
        G.add_edge("Q18395404", "Q13582529")
        data["Q135608"] = {
            "site_link": "Chlopsidae",
            "scientific": "Chlopsidae",
            "rank": "family",
            "image": "Chlopsis bicolor.jpg"
        }
        G.add_edge("Q128685", "Q135608")
        
        # G.remove_edge('Q124289021', 'Q124289021')
        data["Q2072138"]["site_link"] = "Myxiniformes"
        data["Q15100334"]["site_link"] = "Myxini"
        data["Q3745848"]["site_link"] = "Platypus"
        # delete problematic taxa (by removing their rank)
        data["Q3748423"].pop("rank")
        data["Q4000124"].pop("rank")
        data["Q822890"].pop("rank")
        data["Q3111386"].pop("rank")
        data["Q21224524"].pop("rank")
        data["Q343460"].pop("rank")
        data["Q47544996"].pop("rank")
        # remove fossile taxon
        data["Q3055905"].pop("rank")
        # Salentia is just a regular clade according to wikipedia
        data["Q1746027"].pop("rank")
        # According to worms, Enopla is not an accepted taxon
        # data["Q275879"].pop("rank")
        # And Hoplonemertea is a class
        data["Q9293731"]["rank"] = "class"
        # add crocolymorphes as superorder
        data["Q131863"]["rank"] = "superorder"
        
        # Scleroglossa just a clade
        data["Q2944038"].pop("rank")
        
        # remove all zoa phylums
        data["Q2698547"].pop("rank")
        data["Q1407833"].pop("rank")
        data["Q2503841"].pop("rank")
        data["Q27207"].pop("rank")
        data["Q47966"].pop("rank")
        data["Q47969"].pop("rank")
        data["Q245695"].pop("rank")
        data["Q1085980"].pop("rank")
        data["Q1209254"].pop("rank")
        data["Q7444798"].pop("rank")
        data["Q1096960"].pop("rank")
        data["Q2910821"].pop("rank")
        # Remove cetartiodactyle
        data["Q27850"].pop("rank")
        # Unaccepted taxon according to WOoMS
        data["Q28432106"].pop("rank")
        # Seems to be a subgenus in WoRMS
        data["Q21224351"].pop("rank")
        data["Q2781884"].pop("rank")
        data["Q85763751"].pop("rank")
        data["Q134665"].pop("rank")
        data["Q138259"].pop("rank")
        data["Q111752876"].pop("rank")
        # data["Q1633496"].pop("rank")
        data["Q160830"].pop("rank")
        data["Q2330918"].pop("rank")
        data["Q2513125"].pop("rank")
        data["Q1231177"].pop("rank")
        data["Q337777"].pop("rank")
        data["Q671280"].pop("rank")
        data["Q46851"].pop("rank")
        data["Q27584"].pop("rank")
        data["Q7921546"].pop("rank")
        # data["Q5173"].pop("rank")
        data["Q321481"].pop("rank")
        data["Q3609046"].pop("rank")
        data["Q16987281"].pop("rank")
        # REmoving Ambulacraria and Xenambulacraria 
        data["Q2412197"].pop("rank")
        data["Q136956"].pop("rank")
        # Remove Endopterygota considered as a clade and not a suborder in
        # wikipedia
        data["Q304358"].pop("rank")
        
        # extinct family
        data["Q20817854"].pop("rank")
        
        # Remove Conchifera and Aclopophora because they are not in WoRMS
        data["Q213228"].pop("rank")
        data["Q675203"].pop("rank")
        # Remove holotherians
        data["Q2478975"].pop("rank")
        # Remove eutherians
        data["Q17092469"].pop("rank")
        # removing maxillpoda as they only contain copepoda and Flavien
        # wanted me to
        data["Q132662"].pop("rank")
                
        print("Making animalia tree...")
        # Remove taxa without rank or site_link
        data["Q2382443"]["site_link"] = "Biota"
        data["Q2382443"]["rank"] = "superkingdom"
        print(data["Q2382443"])
        G = removeAndReconnect(G, data=data)
        # Remove taxa not connected to animalia but also output what isn't
        # connected to anything to find problem in the data (mostly
        # extinct taxa)
        connected_to_biota = nx.dfs_tree(G, "Q2382443")
        to_check = []
        for node in list(G):
            if node not in connected_to_biota:
                if data.get(node) and data[node]["site_link"] and data[node].get("rank") and data[node].get("scientific") and data[node].get("image"):
                    to_check.append(node)
        to_print = []
        for node in to_check:
            while G.has_node(node) and len(list(G.predecessors(node))):
                node = list(G.predecessors(node))[0]
            if data[node] and data[node]["rank"] != "species" and data[node]["rank"] != "subspecies":
                to_print.append(node)
        with open("results/unconnected_taxa.json", "w") as f:
            json.dump(to_print, f, indent=2)
        print("Number of taxa not connected to biota:", len(to_print))
        
        connected_to_animalia = nx.dfs_tree(G, "Q729")
        for node in list(G):
            if node not in connected_to_animalia:
                G.remove_node(node)
        # try:
        #     print(nx.find_cycle(G))
        # except nx.NetworkXNoCycle:
        #     pass
        topo_sort = list(nx.topological_sort(G))
        for i, node in enumerate(topo_sort):
            data[node]["height"] = i
        animalia_tree = nx.DiGraph()
        animalia_tree.add_node("Q729")
        # We use a topological sort to get the longest path possible
        # as it is the most likely to be correct
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

        number_problem = 0
        for taxon_info in DOUBLE_TAXONS:    
            taxon = taxon_info["id"]
            ranks = taxon_info["ranks"]
            if animalia_tree.has_node(taxon):
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