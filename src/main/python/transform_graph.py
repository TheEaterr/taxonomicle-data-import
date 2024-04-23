import networkx as nx
from time import time
import matplotlib.pyplot as plt
from utils import getAndPrintStats, removeAndReconnect

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
    full_animalia_tree.nodes["Q551092"]["rank"] = "subfamily"
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
    full_animalia_tree.nodes["Q160"]["rank"] = "infraorder"
    full_animalia_tree.nodes["Q168366"]["rank"] = "pavorder"
    full_animalia_tree.nodes["Q7253962"]["rank"] = "subfamily"
    full_animalia_tree.nodes["Q65076322"]["rank"] = "subfamily"
    full_animalia_tree.nodes["Q3055723"]["rank"] = "infraorder"
    full_animalia_tree.nodes["Q10492551"]["rank"] = "subgenus"
    full_animalia_tree.nodes["Q1185781"]["rank"] = "superorder"
    # Following what is written in wikipedia
    full_animalia_tree.nodes["Q4286979"]["rank"] = "subgenus"
    
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
    # full_animalia_tree.remove_edge("Q25375", "Q4035771")
    # full_animalia_tree.add_edge("Q230502", "Q4035771")
    full_animalia_tree.remove_edge("Q1782769", "Q20889393")
    full_animalia_tree.add_edge("Q29877020", "Q20889393")
    
    # restore Aulipotyphla to their correct place
    full_animalia_tree.remove_edge("Q7377", "Q16635184")
    full_animalia_tree.add_edge("Q27379", "Q16635184")
    
    full_animalia_tree.remove_edge("Q7377", "Q26332")
    full_animalia_tree.add_edge("Q25336", "Q26332")
    
    full_animalia_tree.remove_edge("Q784667", "Q35083222")
    full_animalia_tree.add_edge("Q18710482", "Q35083222")
    
    full_animalia_tree.remove_edge("Q425791", "Q26897763")
    full_animalia_tree.remove_edge("Q1552315", "Q425791")
    full_animalia_tree.add_edge("Q26897763", "Q425791")
    
    # Q244269 was written as a child of a species
    full_animalia_tree.remove_edge("Q662226", "Q244269")
    full_animalia_tree.add_edge("Q223302", "Q244269")
    
    # malacostraca are multicrustacea
    full_animalia_tree.remove_edge("Q25364", "Q182978")
    full_animalia_tree.add_edge("Q11937877", "Q182978")
    
    # Species under another species
    full_animalia_tree.remove_edge("Q168327", "Q328516")
    full_animalia_tree.add_edge("Q172923", "Q328516")
    
    def isNotSubspecies(node):
        return full_animalia_tree.nodes[node].get("rank") != "subspecies"

    animalia_tree = nx.subgraph_view(full_animalia_tree, filter_node=isNotSubspecies)

    pruned_animalia_tree = removeAndReconnect(animalia_tree)
    getAndPrintStats(pruned_animalia_tree)
    nx.write_graphml_lxml(pruned_animalia_tree, "results/animalia_tree_filtered.graphml")
