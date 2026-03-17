import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt

st.set_page_config(page_title="Map Coloring CSP Solver", layout="wide")

# =========================================================
# MAP DATA
# 10 maps, each with max 5 regions for a clean demo
# =========================================================
MAPS = {
    "Pakistan": {
        "nodes": ["Lahore", "Karachi", "Islamabad", "Peshawar", "Quetta"],
        "edges": [
            ("Lahore", "Islamabad"),
            ("Islamabad", "Peshawar"),
            ("Islamabad", "Quetta"),
            ("Lahore", "Quetta"),
            ("Karachi", "Quetta"),
        ],
        "pos": {
            "Lahore": (0.56, 0.82),
            "Islamabad": (0.38, 0.57),
            "Peshawar": (0.14, 0.50),
            "Quetta": (0.68, 0.35),
            "Karachi": (0.94, 0.12),
        },
    },
    "Australia": {
        "nodes": ["WA", "NT", "SA", "Q", "NSW"],
        "edges": [
            ("WA", "NT"), ("WA", "SA"),
            ("NT", "SA"), ("NT", "Q"),
            ("SA", "Q"), ("SA", "NSW"),
            ("Q", "NSW"),
        ],
        "pos": {
            "WA": (0.12, 0.55),
            "NT": (0.38, 0.80),
            "SA": (0.40, 0.45),
            "Q": (0.72, 0.78),
            "NSW": (0.78, 0.38),
        },
    },
    "India": {
        "nodes": ["Punjab", "Delhi", "Haryana", "UP", "Rajasthan"],
        "edges": [
            ("Punjab", "Haryana"),
            ("Haryana", "Delhi"),
            ("Haryana", "UP"),
            ("Rajasthan", "Haryana"),
            ("Rajasthan", "UP"),
        ],
        "pos": {
            "Punjab": (0.18, 0.72),
            "Haryana": (0.42, 0.58),
            "Delhi": (0.50, 0.74),
            "UP": (0.80, 0.54),
            "Rajasthan": (0.20, 0.28),
        },
    },
    "USA": {
        "nodes": ["California", "Nevada", "Arizona", "Utah", "Oregon"],
        "edges": [
            ("California", "Nevada"),
            ("California", "Arizona"),
            ("California", "Oregon"),
            ("Nevada", "Arizona"),
            ("Nevada", "Utah"),
        ],
        "pos": {
            "Oregon": (0.16, 0.82),
            "California": (0.14, 0.42),
            "Nevada": (0.40, 0.56),
            "Utah": (0.68, 0.70),
            "Arizona": (0.60, 0.24),
        },
    },
    "Europe": {
        "nodes": ["France", "Germany", "Italy", "Spain", "Belgium"],
        "edges": [
            ("France", "Germany"),
            ("France", "Italy"),
            ("France", "Spain"),
            ("France", "Belgium"),
            ("Germany", "Belgium"),
        ],
        "pos": {
            "Spain": (0.10, 0.28),
            "France": (0.34, 0.52),
            "Belgium": (0.48, 0.78),
            "Germany": (0.72, 0.70),
            "Italy": (0.72, 0.18),
        },
    },
    "China": {
        "nodes": ["Xinjiang", "Tibet", "Sichuan", "Beijing", "Shanghai"],
        "edges": [
            ("Xinjiang", "Tibet"),
            ("Tibet", "Sichuan"),
            ("Sichuan", "Beijing"),
            ("Sichuan", "Shanghai"),
            ("Beijing", "Shanghai"),
        ],
        "pos": {
            "Xinjiang": (0.10, 0.70),
            "Tibet": (0.28, 0.34),
            "Sichuan": (0.50, 0.50),
            "Beijing": (0.82, 0.76),
            "Shanghai": (0.88, 0.28),
        },
    },
    "Brazil": {
        "nodes": ["Amazonas", "Para", "Bahia", "Sao Paulo", "Rio"],
        "edges": [
            ("Amazonas", "Para"),
            ("Para", "Bahia"),
            ("Bahia", "Sao Paulo"),
            ("Sao Paulo", "Rio"),
            ("Bahia", "Rio"),
        ],
        "pos": {
            "Amazonas": (0.10, 0.76),
            "Para": (0.40, 0.80),
            "Bahia": (0.72, 0.56),
            "Sao Paulo": (0.62, 0.18),
            "Rio": (0.88, 0.16),
        },
    },
    "Canada": {
        "nodes": ["BC", "Alberta", "Manitoba", "Ontario", "Quebec"],
        "edges": [
            ("BC", "Alberta"),
            ("Alberta", "Manitoba"),
            ("Manitoba", "Ontario"),
            ("Ontario", "Quebec"),
            ("Alberta", "Ontario"),
        ],
        "pos": {
            "BC": (0.08, 0.58),
            "Alberta": (0.28, 0.62),
            "Manitoba": (0.50, 0.58),
            "Ontario": (0.72, 0.54),
            "Quebec": (0.92, 0.56),
        },
    },
    "Germany": {
        "nodes": ["Bavaria", "Berlin", "Hamburg", "Hesse", "Saxony"],
        "edges": [
            ("Hamburg", "Berlin"),
            ("Berlin", "Saxony"),
            ("Saxony", "Bavaria"),
            ("Hesse", "Bavaria"),
            ("Hesse", "Hamburg"),
        ],
        "pos": {
            "Hamburg": (0.34, 0.88),
            "Berlin": (0.72, 0.82),
            "Hesse": (0.34, 0.50),
            "Saxony": (0.72, 0.48),
            "Bavaria": (0.56, 0.16),
        },
    },
    "South Africa": {
        "nodes": ["Western Cape", "Eastern Cape", "Gauteng", "KwaZulu-Natal", "Limpopo"],
        "edges": [
            ("Western Cape", "Eastern Cape"),
            ("Eastern Cape", "KwaZulu-Natal"),
            ("KwaZulu-Natal", "Gauteng"),
            ("Gauteng", "Limpopo"),
            ("Eastern Cape", "Gauteng"),
        ],
        "pos": {
            "Western Cape": (0.12, 0.18),
            "Eastern Cape": (0.40, 0.20),
            "Gauteng": (0.58, 0.56),
            "KwaZulu-Natal": (0.78, 0.28),
            "Limpopo": (0.74, 0.84),
        },
    },
}

COLORS = ["Red", "Green", "Blue"]

# =========================================================
# SESSION STATE
# =========================================================
if "selected_map" not in st.session_state:
    st.session_state.selected_map = "Pakistan"
if "coloring" not in st.session_state:
    st.session_state.coloring = {}
if "history" not in st.session_state:
    st.session_state.history = []
if "status_type" not in st.session_state:
    st.session_state.status_type = "info"
if "status_msg" not in st.session_state:
    st.session_state.status_msg = "Choose a map, select a region, and apply a color."
if "tip_msg" not in st.session_state:
    st.session_state.tip_msg = "Tip: neighboring regions must have different colors."

# =========================================================
# HELPERS
# =========================================================
def reset_for_map():
    st.session_state.coloring = {}
    st.session_state.history = []
    st.session_state.status_type = "info"
    st.session_state.status_msg = f"Loaded {st.session_state.selected_map}. Start coloring."
    st.session_state.tip_msg = "Tip: try central regions first and avoid using the same color on neighbors."

def build_graph(map_name):
    data = MAPS[map_name]
    g = nx.Graph()
    g.add_nodes_from(data["nodes"])
    g.add_edges_from(data["edges"])
    return g

def conflicting_neighbor(graph, coloring, region, color):
    for neighbor in graph.neighbors(region):
        if coloring.get(neighbor) == color:
            return neighbor
    return None

def safe_colors(graph, coloring, region):
    used = set()
    for neighbor in graph.neighbors(region):
        if neighbor in coloring:
            used.add(coloring[neighbor])
    return [c for c in COLORS if c not in used]

def solve_csp(graph):
    solve_history = []

    def valid(region, color, partial):
        for neighbor in graph.neighbors(region):
            if partial.get(neighbor) == color:
                return False
        return True

    def backtrack(partial):
        if len(partial) == len(graph.nodes()):
            solve_history.append("Solution complete.")
            return dict(partial)

        region = [n for n in graph.nodes() if n not in partial][0]

        for color in COLORS:
            solve_history.append(f"Trying {region} = {color}")
            if valid(region, color, partial):
                partial[region] = color
                solve_history.append(f"Placed {region} = {color}")
                result = backtrack(partial)
                if result is not None:
                    return result
                solve_history.append(f"Backtracking from {region} = {color}")
                del partial[region]
            else:
                solve_history.append(f"Conflict: {region} cannot be {color}")

        return None

    return backtrack({}), solve_history

def draw_graph(graph, coloring, map_name):
    pos = MAPS[map_name]["pos"]
    node_colors = [coloring.get(node, "#9ca3af").lower() if node in coloring else "#9ca3af" for node in graph.nodes()]

    fig, ax = plt.subplots(figsize=(4.0, 4.0))
    nx.draw_networkx_edges(graph, pos, ax=ax, width=2.0, edge_color="#475569")
    nx.draw_networkx_nodes(
        graph, pos, ax=ax,
        node_color=node_colors,
        node_size=1450,
        linewidths=1.8,
        edgecolors="#ffffff"
    )
    nx.draw_networkx_labels(
        graph, pos, ax=ax,
        font_size=9,
        font_weight="bold",
        font_color="white"
    )
    ax.set_axis_off()
    ax.set_xlim(0, 1.02)
    ax.set_ylim(0, 1.02)
    fig.tight_layout(pad=0.5)
    return fig

# =========================================================
# CSS
# =========================================================
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"] {
    background: #f5f7fb;
}
.block-container {
    max-width: 1420px;
    padding-top: 1.2rem;
    padding-bottom: 1rem;
}
.app-title {
    font-size: 2.8rem;
    font-weight: 800;
    color: #1f2937;
    margin-bottom: 0.8rem;
}
.card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 18px;
    padding: 18px;
    box-shadow: 0 10px 25px rgba(15, 23, 42, 0.05);
    height: 100%;
}
.card-title {
    font-size: 1.35rem;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 12px;
}
.subtle {
    color: #6b7280;
    font-size: 0.95rem;
    margin-bottom: 8px;
}

/* neat select boxes */
div[data-baseweb="select"] > div {
    min-height: 46px !important;
    border-radius: 12px !important;
}

/* real button styling */
.stButton > button {
    width: 100%;
    min-height: 46px;
    border-radius: 12px;
    border: none;
    font-weight: 700;
    font-size: 15px;
    color: white;
    box-shadow: 0 8px 18px rgba(15, 23, 42, 0.12);
    transition: all 0.2s ease;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 12px 22px rgba(15, 23, 42, 0.16);
}

/* style all three action buttons by column groups */
div[data-testid="column"]:nth-of-type(1) .stButton > button {
    background: linear-gradient(135deg, #2563eb, #38bdf8);
}
div[data-testid="column"]:nth-of-type(2) .stButton > button {
    background: linear-gradient(135deg, #16a34a, #22c55e);
}
div[data-testid="column"]:nth-of-type(3) .stButton > button {
    background: linear-gradient(135deg, #dc2626, #f87171);
}

/* status */
.status-success {
    background: #dcfce7;
    color: #166534;
    border-left: 6px solid #16a34a;
    padding: 14px;
    border-radius: 12px;
    font-weight: 600;
    margin-bottom: 10px;
}
.status-error {
    background: #fee2e2;
    color: #991b1b;
    border-left: 6px solid #dc2626;
    padding: 14px;
    border-radius: 12px;
    font-weight: 600;
    margin-bottom: 10px;
}
.status-info {
    background: #dbeafe;
    color: #1d4ed8;
    border-left: 6px solid #2563eb;
    padding: 14px;
    border-radius: 12px;
    font-weight: 600;
    margin-bottom: 10px;
}
.status-tip {
    background: #fef3c7;
    color: #92400e;
    border-left: 6px solid #d97706;
    padding: 14px;
    border-radius: 12px;
    font-weight: 600;
    margin-bottom: 10px;
}
.history-box textarea {
    background: #ffffff !important;
    color: #000000 !important;
    border-radius: 12px !important;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================
st.markdown('<div class="app-title">🌍 Map Coloring CSP Solver</div>', unsafe_allow_html=True)

# =========================================================
# LAYOUT
# =========================================================
left, center, right = st.columns([1.08, 1.0, 1.15], gap="large")

with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🎛 Controls</div>', unsafe_allow_html=True)

    st.selectbox(
        "Map",
        list(MAPS.keys()),
        key="selected_map",
        on_change=reset_for_map
    )

    graph = build_graph(st.session_state.selected_map)
    nodes = MAPS[st.session_state.selected_map]["nodes"]

    region = st.selectbox("Region", nodes)
    color = st.selectbox("Color", COLORS)

    b1, b2, b3 = st.columns(3)
    with b1:
        apply_pressed = st.button("Apply Color", key="apply_color")
    with b2:
        solve_pressed = st.button("Solve Automatically", key="solve_auto")
    with b3:
        reset_pressed = st.button("Reset", key="reset_map")

    if apply_pressed:
        bad_neighbor = conflicting_neighbor(graph, st.session_state.coloring, region, color)
        if bad_neighbor is None:
            st.session_state.coloring[region] = color
            st.session_state.history.append(f"Applied {color} to {region}")
            st.session_state.status_type = "success"
            st.session_state.status_msg = f"{region} was colored {color} successfully."
            st.session_state.tip_msg = "Good move. Continue coloring the remaining regions."
        else:
            options = safe_colors(graph, st.session_state.coloring, region)
            option_text = ", ".join(options) if options else "No safe color available"
            st.session_state.history.append(
                f"Conflict: {region} was not colored because neighbor {bad_neighbor} already uses {color}"
            )
            st.session_state.status_type = "error"
            st.session_state.status_msg = (
                f"Conflict occurred. {region} was not colored because neighboring region "
                f"{bad_neighbor} already uses {color}."
            )
            st.session_state.tip_msg = f"Try a different color. Suggested safe colors: {option_text}"

    if solve_pressed:
        solution, solve_history = solve_csp(graph)
        if solution is not None:
            st.session_state.coloring = solution
            st.session_state.history.extend(solve_history)
            st.session_state.status_type = "success"
            st.session_state.status_msg = "Automatic solution found successfully."
            st.session_state.tip_msg = "The solver used CSP backtracking. Review the history to understand the steps."
        else:
            st.session_state.history.extend(solve_history)
            st.session_state.status_type = "error"
            st.session_state.status_msg = "No valid coloring was found."
            st.session_state.tip_msg = "Try another map or change the available colors."

    if reset_pressed:
        reset_for_map()
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

with center:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🗺️ Map Visualization</div>', unsafe_allow_html=True)
    graph = build_graph(st.session_state.selected_map)
    fig = draw_graph(graph, st.session_state.coloring, st.session_state.selected_map)
    st.pyplot(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📊 Status</div>', unsafe_allow_html=True)

    if st.session_state.status_type == "success":
        st.markdown(f'<div class="status-success">{st.session_state.status_msg}</div>', unsafe_allow_html=True)
    elif st.session_state.status_type == "error":
        st.markdown(f'<div class="status-error">{st.session_state.status_msg}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="status-info">{st.session_state.status_msg}</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="status-tip">{st.session_state.tip_msg}</div>', unsafe_allow_html=True)

    st.markdown('<div class="card-title" style="margin-top:12px;">📜 Algorithm History</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtle">Every valid move, conflict, and solver step appears here.</div>', unsafe_allow_html=True)
    st.markdown('<div class="history-box">', unsafe_allow_html=True)
    st.text_area(
        "History",
        value="\n".join(st.session_state.history),
        height=315,
        key="history_area"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
