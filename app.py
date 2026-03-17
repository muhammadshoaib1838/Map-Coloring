import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt

st.set_page_config(page_title="Map Coloring CSP", layout="wide")

# -------------------------
# CSS (PROFESSIONAL)
# -------------------------
st.markdown("""
<style>
.block-container {padding-top: 1rem;}

.card {
    background: white;
    padding: 18px;
    border-radius: 16px;
    border: 1px solid #e5e7eb;
}

.title {
    font-size: 22px;
    font-weight: 700;
    margin-bottom: 10px;
}

button[kind="primary"] {
    border-radius: 10px !important;
    height: 45px !important;
    font-weight: 600 !important;
}

/* BUTTON COLORS */
.apply-btn button {background:#2563eb !important; color:white;}
.solve-btn button {background:#16a34a !important; color:white;}
.reset-btn button {background:#dc2626 !important; color:white;}

.status-success {background:#dcfce7; padding:10px; border-radius:10px;}
.status-error {background:#fee2e2; padding:10px; border-radius:10px;}
.status-info {background:#dbeafe; padding:10px; border-radius:10px;}

textarea {background:white !important; color:black !important;}
</style>
""", unsafe_allow_html=True)

# -------------------------
# MAP DATA
# -------------------------
MAPS = {
    "Pakistan": {
        "nodes": ["Lahore","Karachi","Islamabad","Peshawar","Quetta"],
        "edges": [
            ("Lahore","Islamabad"),
            ("Islamabad","Peshawar"),
            ("Islamabad","Quetta"),
            ("Lahore","Quetta"),
            ("Karachi","Quetta")
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
    }
}

COLORS = ["Red","Green","Blue"]

# -------------------------
# STATE
# -------------------------
if "coloring" not in st.session_state:
    st.session_state.coloring = {}

if "history" not in st.session_state:
    st.session_state.history = []

if "status" not in st.session_state:
    st.session_state.status = ("info", "Start coloring map")

# -------------------------
# FUNCTIONS
# -------------------------
def add_history(msg):
    st.session_state.history.append(msg)

def check_conflict(G, region, color):
    for n in G.neighbors(region):
        if st.session_state.coloring.get(n) == color:
            return n
    return None

def solve_csp(G):
    history = []

    def valid(node, c, assign):
        for n in G.neighbors(node):
            if assign.get(n) == c:
                return False
        return True

    def backtrack(assign):
        if len(assign) == len(G.nodes()):
            return assign

        node = [n for n in G.nodes() if n not in assign][0]

        for c in COLORS:
            history.append(f"Trying {node} = {c}")
            if valid(node, c, assign):
                assign[node] = c
                history.append(f"Placed {node} = {c}")
                res = backtrack(assign)
                if res:
                    return res
                history.append(f"Backtrack {node}")
                del assign[node]
        return None

    sol = backtrack({})
    return sol, history

# -------------------------
# LAYOUT
# -------------------------
col1, col2, col3 = st.columns([1,1,1])

# -------------------------
# CONTROLS
# -------------------------
with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="title">Controls</div>', unsafe_allow_html=True)

    map_name = st.selectbox("Map", list(MAPS.keys()))
    data = MAPS[map_name]

    G = nx.Graph()
    G.add_nodes_from(data["nodes"])
    G.add_edges_from(data["edges"])

    region = st.selectbox("Region", data["nodes"])
    color = st.selectbox("Color", COLORS)

    # APPLY
    st.markdown('<div class="apply-btn">', unsafe_allow_html=True)
    if st.button("Apply Color"):
        conflict = check_conflict(G, region, color)

        if conflict:
            msg = f"Conflict: {region} cannot be {color} (neighbor {conflict})"
            st.session_state.status = ("error", msg)
            add_history(msg)
        else:
            st.session_state.coloring[region] = color
            msg = f"{region} → {color}"
            st.session_state.status = ("success", msg)
            add_history(msg)
    st.markdown('</div>', unsafe_allow_html=True)

    # SOLVE
    st.markdown('<div class="solve-btn">', unsafe_allow_html=True)
    if st.button("Solve Automatically"):
        sol, hist = solve_csp(G)
        if sol:
            st.session_state.coloring = sol
            st.session_state.status = ("success", "Solved successfully")
            st.session_state.history.extend(hist)
    st.markdown('</div>', unsafe_allow_html=True)

    # RESET
    st.markdown('<div class="reset-btn">', unsafe_allow_html=True)
    if st.button("Reset"):
        st.session_state.coloring = {}
        st.session_state.history = []
        st.session_state.status = ("info", "Reset done")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# GRAPH
# -------------------------
with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="title">Map</div>', unsafe_allow_html=True)

    color_map = [
        st.session_state.coloring.get(n, "gray").lower()
        for n in G.nodes()
    ]

    plt.figure(figsize=(3.5,3.5))
    pos = nx.spring_layout(G, seed=42)

    nx.draw(G, pos,
            with_labels=True,
            node_color=color_map,
            node_size=900,
            font_color="white")

    st.pyplot(plt)
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# STATUS + HISTORY
# -------------------------
with col3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="title">Status</div>', unsafe_allow_html=True)

    status_type, msg = st.session_state.status

    if status_type == "success":
        st.markdown(f'<div class="status-success">{msg}</div>', unsafe_allow_html=True)
    elif status_type == "error":
        st.markdown(f'<div class="status-error">{msg}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="status-info">{msg}</div>', unsafe_allow_html=True)

    st.markdown('<div class="title">Algorithm History</div>', unsafe_allow_html=True)

    st.text_area("", "\n".join(st.session_state.history), height=300)

    st.markdown('</div>', unsafe_allow_html=True)
