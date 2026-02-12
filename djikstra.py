import osmnx as ox
import networkx as nx
import folium
import streamlit as st
from streamlit_folium import st_folium
import os

# --------------------------
# Streamlit title
# --------------------------
st.title("Overlay Algoritma Dijkstra dalam Menentukan Rute Tercepat Perjalanan Sepeda Motor dari Margaasih ke Universitas Komputer Indonesia")

# --------------------------
# Locations
# --------------------------
START_NAME = "Halte Margaasih"
START_LAT, START_LON = -6.934878, 107.539303

END_NAME = "Universitas Komputer Indonesia"
END_LAT, END_LON = -6.887135, 107.615148

# --------------------------
# Load Drive Network (once)
# --------------------------
@st.cache_data
def load_graph():
    file_path = os.path.join("bandung_margaasih.graphml")
    return ox.load_graphml(file_path)

G_big = load_graph()

# -----------------------------------
# Define bbox (north, south, east, west)
# -----------------------------------
bbox = (
    -6.85,   # north
    -6.99,   # south
    107.65,  # east
    107.50   # west
)

# -----------------------------------
# Truncate graph
# -----------------------------------
G = ox.truncate.truncate_graph_bbox(G_big, bbox)

st.write("Truncated nodes:", G.number_of_nodes())
st.write("Truncated edges:", G.number_of_edges())

# --------------------------
# Find nearest nodes
# --------------------------
start_node = ox.nearest_nodes(G, START_LON, START_LAT)
end_node = ox.nearest_nodes(G, END_LON, END_LAT)

# --------------------------
# Run Dijkstra (shortest path)
# --------------------------
route = nx.shortest_path(
    G,
    start_node,
    end_node,
    weight="length",
    method="dijkstra"
)

# --------------------------
# Compute total distance
# --------------------------
total_distance_m = 0.0

for u, v in zip(route[:-1], route[1:]):
    edge_data = G.get_edge_data(u, v)
    shortest_edge = min(edge_data.values(), key=lambda d: d.get("length", 0))
    total_distance_m += shortest_edge.get("length", 0)

distance_km = total_distance_m / 1000

st.success(f"Total jarak rute terpendek: {distance_km:.2f} km")

# --------------------------
# Create Folium Map
# --------------------------
m = folium.Map(tiles="cartodbpositron")

# --------------------------
# Draw graph edges (optional background)
# --------------------------
for u, v, data in G.edges(data=True):
    if "geometry" in data:
        coords = [(lat, lon) for lon, lat in data["geometry"].coords]
    else:
        coords = [
            (G.nodes[u]["y"], G.nodes[u]["x"]),
            (G.nodes[v]["y"], G.nodes[v]["x"])
        ]

    folium.PolyLine(
        coords,
        color="gray",
        weight=1,
        opacity=0.3
    ).add_to(m)

# --------------------------
# Overlay shortest path
# --------------------------
path_coords = [(G.nodes[n]["y"], G.nodes[n]["x"]) for n in route]

folium.PolyLine(
    path_coords,
    color="red",
    weight=5,
    opacity=0.9,
    tooltip=f"Rute Terpendek: {total_distance_m:.0f} meter ({distance_km:.2f} km)"
).add_to(m)

# --------------------------
# Auto-center & zoom to route
# --------------------------
m.fit_bounds(path_coords, padding=(50, 50))

# --------------------------
# Markers
# --------------------------
folium.Marker(
    location=[START_LAT, START_LON],
    popup=START_NAME,
    icon=folium.Icon(color="green", icon="play")
).add_to(m)

folium.Marker(
    location=[END_LAT, END_LON],
    popup=END_NAME,
    icon=folium.Icon(color="red", icon="stop")
).add_to(m)

# --------------------------
# Custom CSS
# --------------------------
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(120deg,#0f172a,#1e3a8a);
        color: white;
    }

    .folium-map {
        border-radius: 12px;
        border: 1px solid #1e40af;
    }

    h1, h2, h3, p {
        color: #93c5fd;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --------------------------
# Display Map
# --------------------------
st_folium(m, width=1600, height=900, returned_objects=[])
