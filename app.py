import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt

st.set_page_config(page_title="Map Coloring CSP", layout="wide")

# --------------------------
# 🎨 UI STYLE
# --------------------------
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #0f172a, #1e293b);
}
h1 { color: #38bdf8; }
h2 { color: #facc15; }

.block {
    padding: 12px;
    border-radius: 10px;
    color: white;
    margin-bottom: 10px;
}

.success { background: #22c55e; }
.error { background: #ef4444; }
.info { background: #3b82f6; }

textarea {
    background: white !important;
    color: black !important;
}
</style>
""", unsafe_allow_html=True)

st.title("🌍 Map Coloring CSP Solver")

# --------------------------
# 🌍 MAP DATA (MAX 5 REGIONS EACH)
# --------------------------
maps = {

    "Pakistan": {
        "nodes": ["Lahore","Karachi","Islamabad","Peshawar","Quetta"],
        "edges": [
            ("Lahore","Islamabad"),
            ("Islamabad","Peshawar"),
            ("Karachi","Quetta"),
            ("Lahore","Quetta"),
            ("Karachi","Lahore")
        ]
    },

    "Australia": {
        "nodes": ["WA","NT","SA","Q","NSW"],
        "edges": [
            ("WA","NT"),("WA","SA"),
            ("NT","SA"),("NT","Q"),
            ("SA","Q"),("SA","NSW"),
            ("Q","NSW")
        ]
    },

    "India": {
        "nodes": ["Punjab","Delhi","UP","Rajasthan","Haryana"],
        "edges": [
            ("Punjab","Haryana"),
            ("Haryana","Delhi"),
            ("Haryana","UP"),
            ("Rajasthan","UP"),
            ("Punjab","Rajasthan")
        ]
    },

    "USA": {
        "nodes": ["CA","NV","AZ","UT","OR"],
        "edges": [
            ("CA","NV"),("CA","AZ"),
            ("NV","AZ"),("NV","UT"),
            ("OR","CA")
        ]
    },

    "Europe": {
        "nodes": ["France","Germany","Italy","Spain","Belgium"],
        "edges": [
            ("France","Germany"),
            ("France","Spain"),
            ("Germany","Belgium"),
            ("Italy","France"),
            ("Belgium","France")
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

if "history" not in st.session_state:
    st.session_state.history = []

# --------------------------
# INPUT
# --------------------------
st.subheader("🎯 Assign Colors")

col1, col2 = st.columns(2)

with col1:
    region = st.selectbox("Select Region", data["nodes"])

with col2:
    color = st.selectbox("Select Color", colors)

if st.button("Apply Color"):
    st.session_state.coloring[region] = color
    st.session_state.history.append(f"{region} → {color}")

# --------------------------
# CONFLICT CHECK
# --------------------------
def check_conflicts():
    conflicts = []
    for u,v in G.edges():
        if u in st.session_state.coloring and v in st.session_state.coloring:
            if st.session_state.coloring[u] == st.session_state.coloring[v]:
                conflicts.append((u,v))
    return conflicts

conflicts = check_conflicts()

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
            st.session_state.history.append(f"Placed {node} → {c}")
            result = backtrack(coloring)
            if result:
                return result
            del coloring[node]

    return None

if st.button("Solve Automatically"):
    st.session_state.history.clear()
    solution = backtrack({})
    if solution:
        st.session_state.coloring = solution

# --------------------------
# GRAPH (FIXED SIZE)
# --------------------------
st.subheader("🗺️ Map Visualization")

color_map = []
for node in G.nodes():
    if node in st.session_state.coloring:
        color_map.append(st.session_state.coloring[node].lower())
    else:
        color_map.append("gray")

plt.figure(figsize=(4,4))  # 👈 FIXED SMALL SIZE
pos = nx.spring_layout(G, seed=42)

nx.draw(
    G, pos,
    with_labels=True,
    node_color=color_map,
    node_size=1500,
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
# STATUS
# --------------------------
st.subheader("📊 Status")

if conflicts:
    st.markdown(f"<div class='block error'>❌ Conflict: {conflicts}</div>", unsafe_allow_html=True)
elif len(st.session_state.coloring) == len(G.nodes()):
    st.markdown("<div class='block success'>✅ Valid Coloring</div>", unsafe_allow_html=True)
else:
    st.markdown("<div class='block info'>⏳ Continue Coloring</div>", unsafe_allow_html=True)

# --------------------------
# HISTORY
# --------------------------
st.subheader("📜 Algorithm History")
st.text_area("", "\n".join(st.session_state.history), height=200)

# --------------------------
# EXPLANATION
# --------------------------
st.subheader("📘 Explanation")

st.markdown("""
- This is a **Constraint Satisfaction Problem (CSP)**  
- Each region must have a different color than its neighbors  
- If two connected regions have same color → ❌ Conflict  

### 🎯 Tips:
- Use **3 colors only**
- Always check neighbors before assigning color
- Try different combinations if conflict occurs
""")

# --------------------------
# RESET
# --------------------------
if st.button("Reset"):
    st.session_state.coloring = {}
    st.session_state.history = []
    st.rerun()
