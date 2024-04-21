import networkx as nx

IUCNS = {
    "Q237350": "EX",
    "Q239509": "EW",
    "Q219127": "CR",
    "Q11394": "EN",
    "Q278113": "VU",
    "Q719675": "NT",
    "Q211005": "LC",
    "Q3245245": "DD"
}

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
    "Q2361851": "infraphylum",
    "Q7432": "species",
    "Q68947": "subspecies",
    "Q34740": "genus",
    "Q1153785": "subphylum",
    "Q3965313": "subtribe",
    "Q36602": "order",
    "Q2007442": "infraclass",
    "Q3150876": "infrakingdom",
    "Q6311258": "pavorder",
    "Q36732": "kingdom",
    "Q5867959": "suborder"
}

TAXON_RANKS = {
    "kingdom": 10,
    "subkingdom": 11,
    "infrakingdom": 12,
    "superphylum": 19,
    "phylum": 20,
    "subphylum": 21,
    "infraphylum": 22,
    "superclass": 29,
    "class": 30,
    "subclass": 31,
    "infraclass": 32,
    "superorder": 39,
    "order": 40,
    "suborder": 41,
    "infraorder": 42,
    "pavorder": 43,
    "superfamily": 49,
    "family": 50,
    "subfamily": 51,
    "tribe": 60,
    "subtribe": 61,
    "genus": 70,
    "subgenus": 71,
    "species": 80,
    "subspecies": 81,
}

def getAndPrintStats(tree: nx.DiGraph):
    print(tree)
    total_site_links = 0
    site_links_per_rank = {}
    count_per_rank = {}
    prop_ranks = {}
    no_rank = 0
    no_scientific = 0
    problems = 0
    for rank_id in TAXONS_TO_KEEP:
        rank = TAXONS_TO_KEEP[rank_id]
        site_links_per_rank[rank] = 0
        count_per_rank[rank] = 0
        prop_ranks[rank] = 0


    for node in tree.nodes():
        node_data = tree.nodes[node]
        if not node_data.get("scientific"):
            # print("No scientific name for", node, node_data)
            no_scientific += 1
        if node_data["site_link"]:
            total_site_links += 1
        if node_data.get("rank"):
            count_per_rank[node_data["rank"]] += 1
            if node_data["site_link"]:
                site_links_per_rank[node_data["rank"]] += 1
            
            predecessors = list(tree.predecessors(node))
            if len(predecessors) > 0:
                predecessor = predecessors[0]
                predecessor_rank = tree.nodes[predecessor].get("rank")
                predecessor_site_link = tree.nodes[predecessor].get("site_link")
                if node_data["site_link"] and predecessor_site_link and predecessor_rank is not None and TAXON_RANKS[node_data["rank"]] <= TAXON_RANKS[predecessor_rank]:
                    print("Problem of hierachy between", predecessor + " (" + predecessor_rank + ")", " and ", node + " (" + node_data["rank"] + ")")
                    problems += 1
        else:
            no_rank += 1
    
    print(problems)

    def hasSiteLink(node):
        return tree.nodes[node].get("site_link") or not tree.nodes[node].get("rank") or tree.nodes[node].get("rank") == "subgenus"

    only_wiki = nx.subgraph_view(tree, filter_node=hasSiteLink)
    only_wiki_tree = nx.bfs_tree(only_wiki, "Q729", reverse=False, depth_limit=None, sort_neighbors=None)
    print("Animalia tree of connected wiki pages: ", only_wiki_tree)
    print("Number of wiki pages :", total_site_links)
    print("Wikipage per taxon :", site_links_per_rank)
    print("Total count per taxon :", count_per_rank)
    for rank_id in TAXONS_TO_KEEP:
        rank = TAXONS_TO_KEEP[rank_id]
        if rank != "subspecies":
            prop_ranks[rank] = site_links_per_rank[rank] / count_per_rank[rank]
    print("Wikipage proportion per taxon :", prop_ranks)
    print("Taxons with no rank :", no_rank)
    print("Taxons with no scientific :", no_scientific)

def recurseRemoveNode(tree: nx.DiGraph, node: str, count: int):
    queue = list(tree.successors(node))
    to_remove = [node]
    while queue:
        curr_node = queue.pop()
        queue.extend(tree.successors(curr_node))
        to_remove.append(curr_node)
        if tree.nodes[curr_node].get("image") and tree.nodes[curr_node]["rank"] == "species":
            # print(f"Removing {curr_node}, {tree.nodes[curr_node].get('scientific')}, {tree.nodes[curr_node].get('vernacular')} because of {node}.")
            count += 1

    for node in to_remove:
        tree.remove_node(node)

    return count

def removeAndReconnect(graph: nx.DiGraph, data = None):
    pruned_graph = graph.copy()
    print(pruned_graph)
    nodes = list(pruned_graph)[:]
    for node in nodes:
        if data is None:
            node_data = pruned_graph.nodes[node]
        else:
            node_data = data.get(node)
        if node_data is None or node_data.get("rank") is None or not node_data["site_link"]:
            successors = list(pruned_graph.successors(node))
            predecessors = list(pruned_graph.predecessors(node))
            for predecessor in predecessors:
                for successor in successors:
                    pruned_graph.add_edge(predecessor, successor)
            pruned_graph.remove_node(node)

    return pruned_graph