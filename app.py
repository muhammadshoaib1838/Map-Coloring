import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt

st.set_page_config(page_title="Map Coloring CSP", layout="wide")

# --------------------------
# 🎨 CUSTOM CSS (BACKGROUND + TEXT STYLE)
# --------------------------
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #0f172a, #1e293b);
}
h1 {
    color: #38bdf8;
}
h2 {
    color: #facc15;
}
.stButton>button {
    border-radius: 10px;
    font-weight: bold;
    background: linear-gradient(90deg, #22c55e, #06b6d4);
    color: white;
}
.block-container {
    padding-top: 2rem;
}
</style>
""", unsafe_allow_html=True)

st.title("🌍 Map Coloring CSP Solver")

# --------------------------
# MAPS
# --------------------------
maps = {
    "Australia": {
        "nodes": ["WA", "NT", "SA", "Q", "NSW", "V", "T"],
        "edges": [
            ("WA","NT"), ("WA","SA"),
            ("NT","SA"), ("NT","Q"),
            ("SA","Q"), ("SA","NSW"), ("SA","V"),
            ("Q","NSW"), ("NSW","V")
        ]
    },

    "Pakistan (10 Cities)": {
        "nodes": [
            "Lahore","Karachi","Islamabad","Peshawar","Quetta",
            "Multan","Faisalabad","Hyderabad","Sukkur","Gwadar"
        ],
        "edges": [
            ("Lahore","Islamabad"),
            ("Lahore","Faisalabad"),
            ("Faisalabad","Multan"),
            ("Multan","Quetta"),
            ("Karachi","Hyderabad"),
            ("Hyderabad","Sukkur"),
            ("Sukkur","Multan"),
            ("Quetta","Gwadar"),
            ("Peshawar","Islamabad"),
            ("Islamabad","Quetta")
        ]
    }
}

colors = ["Red","Green","Blue"]

# --------------------------
# SELECT MAP
# --------------------------
map_name = st.selectbox("Select Map", list(maps.keys()))
data = maps[map_name]

G = nx.Graph()
G.add_nodes_from(data["nodes"])
G.add_edges_from(data["edges"])

# --------------------------
# STATE
# --------------------------
if "coloring" not in st.session_state:
    st.session_state.coloring = {}

# --------------------------
# UI INPUT
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
    for u,v in G.edges():
        if u in coloring and v in coloring:
            if coloring[u] == coloring[v]:
                conflicts.append((u,v))
    return conflicts

conflicts = check_conflicts(G, st.session_state.coloring)

# --------------------------
# AUTO SOLVER
# --------------------------
def is_valid(node, color, coloring):
    for n in G.neighbors(node):
        if n in coloring and coloring[n] == color:
            return False
    return True

def backtrack(coloring):
    if len(coloring) == len(G.nodes()):
        return coloring

    node = [n for n in G.nodes() if n not in coloring][0]

    for c in colors:
        if is_valid(node, c, coloring):
            coloring[node] = c
            result = backtrack(coloring)
            if result:
                return result
            del coloring[node]

    return None

if st.button("Solve Automatically"):
    solution = backtrack({})
    if solution:
        st.session_state.coloring = solution
        st.success("✅ Solution Found!")
    else:
        st.error("❌ No solution")

# --------------------------
# GRAPH DRAW
# --------------------------
st.subheader("🗺️ Map Visualization")

color_map = []
for node in G.nodes():
    if node in st.session_state.coloring:
        c = st.session_state.coloring[node]
        color_map.append(c.lower())
    else:
        color_map.append("gray")

plt.figure(figsize=(7,7))
pos = nx.spring_layout(G, seed=42)

nx.draw(
    G, pos,
    with_labels=True,
    node_color=color_map,
    node_size=2000,
    font_color="white"
)

nx.draw_networkx_edges(
    G, pos,
    edgelist=conflicts,
    edge_color="red",
    width=3
)

st.pyplot(plt)

# --------------------------
# STATUS BOX (COLORED)
# --------------------------
st.subheader("📊 Status")

if conflicts:
    st.markdown(
        f"<div style='background:#ef4444;padding:10px;border-radius:10px;color:white;'>❌ Conflict: {conflicts}</div>",
        unsafe_allow_html=True
    )
else:
    if len(st.session_state.coloring)==len(G.nodes()):
        st.markdown(
            "<div style='background:#22c55e;padding:10px;border-radius:10px;color:white;'>✅ Valid Coloring!</div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            "<div style='background:#3b82f6;padding:10px;border-radius:10px;color:white;'>⏳ Continue...</div>",
            unsafe_allow_html=True
        )

# --------------------------
# RESET
# --------------------------
if st.button("Reset"):
    st.session_state.coloring = {}
    st.rerun()
