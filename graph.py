import osmnx as ox
import networkx as nx

G_bandung = ox.graph_from_place(
    "Bandung, West Java, Indonesia",
    network_type="drive",
    simplify=True,
)


G_margaasih = ox.graph_from_point(
    (-6.9309792,107.5421506),
    dist=3000,               # satuan meters (adjust if needed)
    network_type="drive",
    
)

# Merge graphs
G_merged = nx.compose(G_bandung, G_margaasih)

# Save
ox.save_graphml(G_merged, filepath="bandung_margaasih.graphml")
