import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt

st.set_page_config(page_title="Map Coloring CSP", layout="wide")

st.title("🌍 Map Coloring CSP Solver")

# --------------------------
# MAP DEFINITIONS
# --------------------------
maps = {
    "Australia": {
        "nodes": ["WA", "NT", "SA", "Q", "NSW", "V", "T"],
        "edges": [
            ("WA", "NT"), ("WA", "SA"),
            ("NT", "SA"), ("NT", "Q"),
            ("SA", "Q"), ("SA", "NSW"), ("SA", "V"),
            ("Q", "NSW"),
            ("NSW", "V")
        ]
    },
    "India (Sample)": {
        "nodes": ["Punjab", "Haryana", "Delhi", "UP", "Rajasthan"],
        "edges": [
            ("Punjab", "Haryana"),
            ("Haryana", "Delhi"),
            ("Haryana", "UP"),
            ("Rajasthan", "Haryana"),
            ("Rajasthan", "UP")
        ]
    },
    "USA (Sample)": {
        "nodes": ["CA", "NV", "AZ", "UT"],
        "edges": [
            ("CA", "NV"), ("CA", "AZ"),
            ("NV", "AZ"), ("NV", "UT"),
            ("AZ", "UT")
        ]
    }
}

colors = ["Red", "Green", "Blue"]

# --------------------------
# SELECT MAP
# --------------------------
map_name = st.selectbox("Select Map", list(maps.keys()))
data = maps[map_name]

G = nx.Graph()
G.add_nodes_from(data["nodes"])
G.add_edges_from(data["edges"])

# --------------------------
# SESSION STATE
# --------------------------
if "coloring" not in st.session_state:
    st.session_state.coloring = {}

# --------------------------
# USER INPUT
# --------------------------
st.subheader("🎯 Assign Colors")

col1, col2 = st.columns(2)

with col1:
    region = st.selectbox("Select Region", data["nodes"])

with col2:
    color = st.selectbox("Select Color", colors)

if st.button("Apply Color"):
    st.session_state.coloring[region] = color

# --------------------------
# CONFLICT CHECK
# --------------------------
def check_conflicts(G, coloring):
    conflicts = []
    for u, v in G.edges():
        if u in coloring and v in coloring:
            if coloring[u] == coloring[v]:
                conflicts.append((u, v))
    return conflicts

conflicts = check_conflicts(G, st.session_state.coloring)

# --------------------------
# AUTO SOLVER (BACKTRACKING)
# --------------------------
def is_valid(node, color, coloring, G):
    for neighbor in G.neighbors(node):
        if neighbor in coloring and coloring[neighbor] == color:
            return False
    return True

def backtrack(coloring, nodes, G):
    if len(coloring) == len(nodes):
        return coloring

    node = [n for n in nodes if n not in coloring][0]

    for c in colors:
        if is_valid(node, c, coloring, G):
            coloring[node] = c
            result = backtrack(coloring, nodes, G)
            if result:
                return result
            del coloring[node]

    return None

if st.button("Solve Automatically"):
    solution = backtrack({}, data["nodes"], G)
    if solution:
        st.session_state.coloring = solution
        st.success("Solution Found!")
    else:
        st.error("No solution exists")

# --------------------------
# DRAW GRAPH
# --------------------------
st.subheader("🗺️ Map Visualization")

color_map = []
for node in G.nodes():
    if node in st.session_state.coloring:
        c = st.session_state.coloring[node]
        if c == "Red":
            color_map.append("red")
        elif c == "Green":
            color_map.append("green")
        elif c == "Blue":
            color_map.append("blue")
    else:
        color_map.append("gray")

plt.figure(figsize=(6,6))
pos = nx.spring_layout(G, seed=42)

nx.draw(
    G,
    pos,
    with_labels=True,
    node_color=color_map,
    node_size=2000,
    font_size=10,
    font_color="white"
)

# Highlight conflicts
nx.draw_networkx_edges(
    G,
    pos,
    edgelist=conflicts,
    edge_color="red",
    width=3
)

st.pyplot(plt)

# --------------------------
# STATUS
# --------------------------
st.subheader("📊 Status")

if conflicts:
    st.error(f"❌ Conflicts detected: {conflicts}")
else:
    if len(st.session_state.coloring) == len(G.nodes()):
        st.success("✅ Valid Coloring!")
    else:
        st.info("⏳ Continue coloring...")

# --------------------------
# RESET
# --------------------------
if st.button("Reset"):
    st.session_state.coloring = {}
    st.rerun()
