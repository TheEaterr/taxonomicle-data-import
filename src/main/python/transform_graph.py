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
    "Q2361851": "infraphylum",
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

TAXON_RANKS = {
    "kindgom": 10,
    "subkingdom": 11,
    "infrakingdon": 12,
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

if __name__ == "__main__":
    t = time()
    full_animalia_tree = nx.read_graphml("results/animalia_tree.graphml")
    print(time() - t)
    print("Full tree of animalia (with subspecies) : ", full_animalia_tree)

    # fixing ranks
    full_animalia_tree.nodes["Q107394682"]["rank"] = "genus"
    full_animalia_tree.nodes["Q104857768"]["rank"] = "species"
    full_animalia_tree.nodes["Q104857767"]["rank"] = "species"
    full_animalia_tree.nodes["Q104815681"]["rank"] = "genus"
    full_animalia_tree.nodes["Q117291954"]["rank"] = "genus"
    full_animalia_tree.nodes["Q47966"].pop("rank")
    full_animalia_tree.nodes["Q47969"].pop("rank")
    full_animalia_tree.nodes["Q245695"].pop("rank")
    full_animalia_tree.nodes["Q1085980"].pop("rank")
    full_animalia_tree.nodes["Q1209254"].pop("rank")
    full_animalia_tree.nodes["Q7444798"].pop("rank")
    full_animalia_tree.nodes["Q1096960"].pop("rank")
    full_animalia_tree.nodes["Q2910821"].pop("rank")
    full_animalia_tree.nodes["Q161095"]["rank"] = "infraphylum"
    full_animalia_tree.nodes["Q275544"]["rank"] = "subclass"
    full_animalia_tree.nodes["Q567567"]["rank"] = "superorder"
    full_animalia_tree.nodes["Q205712"]["rank"] = "class"
    full_animalia_tree.nodes["Q10432880"]["rank"] = "suborder"
    full_animalia_tree.nodes["Q17166"]["rank"] = "suborder"
    full_animalia_tree.nodes["Q85762296"]["rank"] = "superfamily"
    full_animalia_tree.nodes["Q95498523"]["rank"] = "family"
    full_animalia_tree.nodes["Q2552226"]["rank"] = "subspecies"
    full_animalia_tree.nodes["Q7181301"]["rank"] = "subspecies"
    full_animalia_tree.nodes["Q113959354"]["rank"] = "species"
    full_animalia_tree.nodes["Q603237"]["rank"] = "subclass"
    full_animalia_tree.nodes["Q2781884"].pop("rank")
    full_animalia_tree.nodes["Q85763751"].pop("rank")
    full_animalia_tree.nodes["Q134665"].pop("rank")
    full_animalia_tree.nodes["Q138259"].pop("rank")
    full_animalia_tree.nodes["Q111752876"].pop("rank")
    full_animalia_tree.remove_edge("Q3699922", "Q5158096")
    full_animalia_tree.add_edge("Q1072243", "Q5158096")
    full_animalia_tree.remove_edge("Q3175675", "Q55000290")
    full_animalia_tree.add_edge("Q7415384", "Q55000290")
    full_animalia_tree.remove_edge("Q3175675", "Q55000007")
    full_animalia_tree.add_edge("Q7415384", "Q55000007")
    full_animalia_tree.remove_edge("Q771067", "Q6525920")
    full_animalia_tree.add_edge("Q134759", "Q6525920")
    full_animalia_tree.remove_edge("Q16948752", "Q7253962")
    full_animalia_tree.add_edge("Q3655255", "Q7253962")
    full_animalia_tree.nodes["Q7253962"]["rank"] = "subfamily"
    full_animalia_tree.nodes["Q65076322"]["rank"] = "subfamily"
    full_animalia_tree.nodes["Q3055723"]["rank"] = "infraorder"
    full_animalia_tree.nodes["Q10492551"]["rank"] = "subgenus"
    
    def isNotSubspecies(node):
        return full_animalia_tree.nodes[node].get("rank") != "subspecies"

    animalia_tree = nx.subgraph_view(full_animalia_tree, filter_node=isNotSubspecies)

    total_site_links = 0
    site_links_per_rank = {}
    count_per_rank = {}
    prop_ranks = {}
    no_rank = 0
    problems = 0
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
            
            predecessors = list(animalia_tree.predecessors(node))
            if len(predecessors) > 0:
                predecessor = predecessors[0]
                predecessor_rank = animalia_tree.nodes[predecessor].get("rank")
                predecessor_site_link = animalia_tree.nodes[predecessor].get("site_link")
                if node_data["site_link"] and predecessor_site_link and predecessor_rank is not None and TAXON_RANKS[node_data["rank"]] <= TAXON_RANKS[predecessor_rank]:
                    print("Problem of hierachy between", predecessor + " (" + predecessor_rank + ")", " and ", node + " (" + node_data["rank"] + ")")
                    problems += 1
        else:
            no_rank += 1
    
    print(problems)

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
        if rank != "subspecies":
            prop_ranks[rank] = site_links_per_rank[rank] / count_per_rank[rank]
    print("Wikipage proportion per taxon :", prop_ranks)
    print("Taxons with no rank :", no_rank)
