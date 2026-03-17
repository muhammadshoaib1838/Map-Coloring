import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt

st.set_page_config(page_title="Map Coloring CSP", layout="wide")

# -----------------------------
# 🎨 PROFESSIONAL CSS
# -----------------------------
st.markdown("""
<style>

/* Card container */
.card {
    background: #111827;
    padding: 18px;
    border-radius: 15px;
    margin-bottom: 15px;
}

/* Title */
.title {
    font-size: 26px;
    font-weight: bold;
    color: #38bdf8;
}

/* Buttons */
.stButton > button {
    width: 100%;
    border-radius: 10px;
    height: 45px;
    font-size: 16px;
    font-weight: 600;
    border: none;
}

/* Apply button */
div.stButton:nth-child(4) button {
    background: #2563eb;
    color: white;
}

/* Solve button */
div.stButton:nth-child(5) button {
    background: #16a34a;
    color: white;
}

/* Reset button */
div.stButton:nth-child(6) button {
    background: #dc2626;
    color: white;
}

/* Status boxes */
.success {
    background: #16a34a;
    padding: 10px;
    border-radius: 10px;
    color: white;
}

.error {
    background: #dc2626;
    padding: 10px;
    border-radius: 10px;
    color: white;
}

.info {
    background: #2563eb;
    padding: 10px;
    border-radius: 10px;
    color: white;
}

/* Text area */
textarea {
    background:white !important;
    color:black !important;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# 🌍 MAP DATA
# -----------------------------
maps = {
    "Pakistan": {
        "nodes": ["Lahore","Karachi","Islamabad","Peshawar","Quetta"],
        "edges": [
            ("Lahore","Islamabad"),
            ("Islamabad","Peshawar"),
            ("Islamabad","Quetta"),
            ("Lahore","Quetta"),
            ("Karachi","Quetta")
        ]
    }
}

colors = ["Red","Green","Blue"]

# -----------------------------
# SESSION STATE
# -----------------------------
if "coloring" not in st.session_state:
    st.session_state.coloring = {}

if "history" not in st.session_state:
    st.session_state.history = []

# -----------------------------
# LAYOUT
# -----------------------------
col1, col2, col3 = st.columns([1,1,1])

# =====================================================
# 🎛 CONTROLS
# =====================================================
with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="title">🎛 Controls</div>', unsafe_allow_html=True)

    map_name = st.selectbox("Map", list(maps.keys()))
    data = maps[map_name]

    G = nx.Graph()
    G.add_nodes_from(data["nodes"])
    G.add_edges_from(data["edges"])

    region = st.selectbox("Region", data["nodes"])
    color = st.selectbox("Color", colors)

    # APPLY COLOR
    if st.button("Apply Color"):
        conflict = False

        for n in G.neighbors(region):
            if n in st.session_state.coloring and st.session_state.coloring[n] == color:
                conflict = True
                st.session_state.history.append(f"Conflict: {region} cannot be {color} (neighbor {n})")
                st.markdown(f'<div class="error">Conflict with {n}</div>', unsafe_allow_html=True)
                break

        if not conflict:
            st.session_state.coloring[region] = color
            st.session_state.history.append(f"{region} → {color}")
            st.markdown(f'<div class="success">Applied {color}</div>', unsafe_allow_html=True)

    # SOLVE
    if st.button("Solve Automatically"):
        st.session_state.history.append("Auto solve triggered")

    # RESET
    if st.button("Reset"):
        st.session_state.coloring = {}
        st.session_state.history = []

    st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# 🗺 GRAPH
# =====================================================
with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="title">🗺 Map</div>', unsafe_allow_html=True)

    color_map = []
    for node in G.nodes():
        if node in st.session_state.coloring:
            color_map.append(st.session_state.coloring[node].lower())
        else:
            color_map.append("gray")

    plt.figure(figsize=(3.5,3.5))  # 👈 SMALL SIZE
    pos = nx.spring_layout(G, seed=42)

    nx.draw(
        G, pos,
        with_labels=True,
        node_color=color_map,
        node_size=900,
        font_color="white",
        font_size=9
    )

    st.pyplot(plt)
    st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# 📊 STATUS + HISTORY
# =====================================================
with col3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="title">📊 Status</div>', unsafe_allow_html=True)

    if len(st.session_state.coloring) == len(G.nodes()):
        st.markdown('<div class="success">All regions colored</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="info">In progress</div>', unsafe_allow_html=True)

    st.markdown('<div class="title">📜 History</div>', unsafe_allow_html=True)

    st.text_area("", "\n".join(st.session_state.history), height=250)

    st.markdown('</div>', unsafe_allow_html=True)
