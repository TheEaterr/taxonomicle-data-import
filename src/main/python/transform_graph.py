import networkx as nx
from time import time

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


if __name__ == "__main__":
    t = time()
    animalia_tree = nx.read_graphml("results/animalia_tree.graphml")
    print(time() - t)
    print("Tree of animalia : ", animalia_tree)
    total_site_links = 0
    site_links_per_rank = {}
    count_per_rank = {}
    prop_ranks = {}
    no_rank = 0
    for rank_id in TAXONS_TO_KEEP:
        rank = TAXONS_TO_KEEP[rank_id]
        site_links_per_rank[rank] = 0
        count_per_rank[rank] = 0
        prop_ranks[rank] = 0
    for node in animalia_tree.nodes():
        node_data = animalia_tree.nodes[node]
        if node_data["site_link"]:
            total_site_links += 1
        if node_data.get("rank"):
            count_per_rank[node_data["rank"]] += 1
            if node_data["site_link"]:
                site_links_per_rank[node_data["rank"]] += 1
        else:
            no_rank += 1

    def hasSiteLink(node):
        return animalia_tree.nodes[node].get("site_link") == True or not animalia_tree.nodes[node].get("rank") or animalia_tree.nodes[node].get("rank") == "subgenus"

    only_wiki = nx.subgraph_view(animalia_tree, filter_node=hasSiteLink)
    only_wiki_tree = nx.bfs_tree(only_wiki, "Q729", reverse=False, depth_limit=None, sort_neighbors=None)
    print("Animalia tree of connected wiki pages: ", only_wiki_tree)
    print("Number of wiki pages :", total_site_links)
    print("Wikipage per taxon :", site_links_per_rank)
    print("Total count per taxon :", count_per_rank)
    for rank_id in TAXONS_TO_KEEP:
        rank = TAXONS_TO_KEEP[rank_id]
        prop_ranks[rank] = site_links_per_rank[rank] / count_per_rank[rank]
    print("Wikipage proportion per taxon :", prop_ranks)
    print("Taxons with no rank :", no_rank)
