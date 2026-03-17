import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt

st.set_page_config(page_title="Map Coloring CSP", layout="wide")

# -----------------------------
# 🎨 PROFESSIONAL CSS
# -----------------------------
st.markdown("""
<style>
.block {
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 10px;
    color: white;
}

.card {
    background: #111827;
    padding: 15px;
    border-radius: 15px;
    margin-bottom: 15px;
}

.title {
    font-size: 28px;
    font-weight: bold;
    color: #38bdf8;
}

.small {
    font-size: 14px;
    color: #9ca3af;
}

.success {background:#16a34a;}
.error {background:#dc2626;}
.info {background:#2563eb;}
.tip {background:#f59e0b;}

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

colors = ["Red","Green","Blue"]

# -----------------------------
# STATE
# -----------------------------
if "coloring" not in st.session_state:
    st.session_state.coloring = {}

if "history" not in st.session_state:
    st.session_state.history = []

# -----------------------------
# LAYOUT (3 COLUMNS)
# -----------------------------
col1, col2, col3 = st.columns([1,1,1])

# =====================================================
# LEFT PANEL (CONTROLS)
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

    if st.button("Apply Color"):
        conflict = False
        for n in G.neighbors(region):
            if n in st.session_state.coloring and st.session_state.coloring[n] == color:
                conflict = True
                st.session_state.history.append(f"❌ Conflict: {region} cannot be {color}")
                st.markdown(f'<div class="block error">Conflict with {n}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="block tip">Try different color</div>', unsafe_allow_html=True)
                break

        if not conflict:
            st.session_state.coloring[region] = color
            st.session_state.history.append(f"✅ {region} → {color}")
            st.markdown(f'<div class="block success">Applied {color}</div>', unsafe_allow_html=True)

    if st.button("Solve"):
        st.session_state.history.append("Auto solving...")

    if st.button("Reset"):
        st.session_state.coloring = {}
        st.session_state.history = []

    st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# CENTER PANEL (GRAPH)
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

    plt.figure(figsize=(3.5,3.5))  # 👈 SMALL GRAPH
    pos = nx.spring_layout(G, seed=42, k=0.8)

    nx.draw(
        G, pos,
        with_labels=True,
        node_color=color_map,
        node_size=900,
        font_size=9,
        font_color="white"
    )

    plt.tight_layout()
    st.pyplot(plt)

    st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# RIGHT PANEL (STATUS + HISTORY)
# =====================================================
with col3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="title">📊 Status</div>', unsafe_allow_html=True)

    if len(st.session_state.coloring) == len(G.nodes()):
        st.markdown('<div class="block success">✅ Complete</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="block info">⏳ In Progress</div>', unsafe_allow_html=True)

    st.markdown('<div class="title">📜 History</div>', unsafe_allow_html=True)

    st.text_area("", "\n".join(st.session_state.history), height=250)

    st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# FOOTER EXPLANATION
# =====================================================
st.markdown("""
<div class="card">
<b>CSP Explanation:</b><br>
Regions = variables<br>
Colors = domain<br>
Constraint = neighbors must differ<br><br>

<b>Tips:</b><br>
- Start from center<br>
- Check neighbors<br>
- Avoid same color<br>
</div>
""", unsafe_allow_html=True)
