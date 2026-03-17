import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt

st.set_page_config(page_title="Map Coloring CSP Solver", layout="wide")

# =========================================================
# DATA
# Each map uses up to 5 regions for a compact professional demo.
# =========================================================
MAPS = {
    "Pakistan": {
        "nodes": ["Lahore", "Karachi", "Islamabad", "Peshawar", "Quetta"],
        "edges": [
            ("Lahore", "Islamabad"),
            ("Islamabad", "Peshawar"),
            ("Islamabad", "Quetta"),
            ("Lahore", "Quetta"),
            ("Karachi", "Quetta")
        ],
        "pos": {
            "Lahore": (0.55, 0.78),
            "Islamabad": (0.38, 0.55),
            "Peshawar": (0.15, 0.50),
            "Quetta": (0.68, 0.34),
            "Karachi": (0.95, 0.12),
        }
    },
    "Australia": {
        "nodes": ["WA", "NT", "SA", "Q", "NSW"],
        "edges": [
            ("WA", "NT"), ("WA", "SA"),
            ("NT", "SA"), ("NT", "Q"),
            ("SA", "Q"), ("SA", "NSW"),
            ("Q", "NSW")
        ],
        "pos": {
            "WA": (0.12, 0.55),
            "NT": (0.38, 0.80),
            "SA": (0.40, 0.45),
            "Q": (0.72, 0.78),
            "NSW": (0.78, 0.38),
        }
    },
    "India": {
        "nodes": ["Punjab", "Delhi", "Haryana", "UP", "Rajasthan"],
        "edges": [
            ("Punjab", "Haryana"),
            ("Haryana", "Delhi"),
            ("Haryana", "UP"),
            ("Rajasthan", "Haryana"),
            ("Rajasthan", "UP")
        ],
        "pos": {
            "Punjab": (0.18, 0.72),
            "Haryana": (0.42, 0.58),
            "Delhi": (0.48, 0.75),
            "UP": (0.78, 0.55),
            "Rajasthan": (0.20, 0.28),
        }
    },
    "USA": {
        "nodes": ["California", "Nevada", "Arizona", "Utah", "Oregon"],
        "edges": [
            ("California", "Nevada"),
            ("California", "Arizona"),
            ("California", "Oregon"),
            ("Nevada", "Arizona"),
            ("Nevada", "Utah")
        ],
        "pos": {
            "Oregon": (0.18, 0.82),
            "California": (0.16, 0.42),
            "Nevada": (0.42, 0.55),
            "Utah": (0.68, 0.70),
            "Arizona": (0.60, 0.28),
        }
    },
    "Europe": {
        "nodes": ["France", "Germany", "Italy", "Spain", "Belgium"],
        "edges": [
            ("France", "Germany"),
            ("France", "Spain"),
            ("France", "Italy"),
            ("France", "Belgium"),
            ("Germany", "Belgium")
        ],
        "pos": {
            "Spain": (0.10, 0.30),
            "France": (0.35, 0.52),
            "Belgium": (0.48, 0.78),
            "Germany": (0.72, 0.70),
            "Italy": (0.70, 0.22),
        }
    },
    "China": {
        "nodes": ["Xinjiang", "Tibet", "Sichuan", "Beijing", "Shanghai"],
        "edges": [
            ("Xinjiang", "Tibet"),
            ("Tibet", "Sichuan"),
            ("Sichuan", "Beijing"),
            ("Sichuan", "Shanghai"),
            ("Beijing", "Shanghai")
        ],
        "pos": {
            "Xinjiang": (0.10, 0.70),
            "Tibet": (0.30, 0.38),
            "Sichuan": (0.52, 0.52),
            "Beijing": (0.82, 0.78),
            "Shanghai": (0.88, 0.32),
        }
    },
    "Brazil": {
        "nodes": ["Amazonas", "Para", "Bahia", "Sao Paulo", "Rio"],
        "edges": [
            ("Amazonas", "Para"),
            ("Para", "Bahia"),
            ("Bahia", "Sao Paulo"),
            ("Sao Paulo", "Rio"),
            ("Bahia", "Rio")
        ],
        "pos": {
            "Amazonas": (0.10, 0.75),
            "Para": (0.42, 0.78),
            "Bahia": (0.70, 0.56),
            "Sao Paulo": (0.62, 0.18),
            "Rio": (0.86, 0.16),
        }
    },
    "Canada": {
        "nodes": ["BC", "Alberta", "Ontario", "Quebec", "Manitoba"],
        "edges": [
            ("BC", "Alberta"),
            ("Alberta", "Manitoba"),
            ("Manitoba", "Ontario"),
            ("Ontario", "Quebec"),
            ("Alberta", "Ontario")
        ],
        "pos": {
            "BC": (0.08, 0.60),
            "Alberta": (0.28, 0.64),
            "Manitoba": (0.50, 0.58),
            "Ontario": (0.72, 0.54),
            "Quebec": (0.92, 0.56),
        }
    },
    "Germany": {
        "nodes": ["Bavaria", "Berlin", "Hamburg", "Hesse", "Saxony"],
        "edges": [
            ("Hamburg", "Berlin"),
            ("Berlin", "Saxony"),
            ("Saxony", "Bavaria"),
            ("Hesse", "Bavaria"),
            ("Hesse", "Hamburg")
        ],
        "pos": {
            "Hamburg": (0.35, 0.88),
            "Berlin": (0.72, 0.82),
            "Hesse": (0.32, 0.50),
            "Saxony": (0.72, 0.48),
            "Bavaria": (0.56, 0.16),
        }
    },
    "South Africa": {
        "nodes": ["Western Cape", "Eastern Cape", "Gauteng", "KwaZulu-Natal", "Limpopo"],
        "edges": [
            ("Western Cape", "Eastern Cape"),
            ("Eastern Cape", "KwaZulu-Natal"),
            ("KwaZulu-Natal", "Gauteng"),
            ("Gauteng", "Limpopo"),
            ("Eastern Cape", "Gauteng")
        ],
        "pos": {
            "Western Cape": (0.12, 0.20),
            "Eastern Cape": (0.40, 0.22),
            "KwaZulu-Natal": (0.75, 0.28),
            "Gauteng": (0.58, 0.58),
            "Limpopo": (0.72, 0.86),
        }
    },
}

COLORS = ["Red", "Green", "Blue"]

# =========================================================
# STATE
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
    st.session_state.status_msg = "Choose a map, then assign colors."

if "tip_msg" not in st.session_state:
    st.session_state.tip_msg = "Tip: adjacent regions must have different colors."

# =========================================================
# HELPERS
# =========================================================
def reset_state_for_map():
    st.session_state.coloring = {}
    st.session_state.history = []
    st.session_state.status_type = "info"
    st.session_state.status_msg = f"Loaded {st.session_state.selected_map}. Start assigning colors."
    st.session_state.tip_msg = "Tip: start from a central region and check its neighbors."

def build_graph(map_name: str):
    data = MAPS[map_name]
    g = nx.Graph()
    g.add_nodes_from(data["nodes"])
    g.add_edges_from(data["edges"])
    return g

def neighbor_with_same_color(graph, coloring, region, color):
    for neighbor in graph.neighbors(region):
        if coloring.get(neighbor) == color:
            return neighbor
    return None

def get_safe_colors(graph, coloring, region):
    blocked = set()
    for neighbor in graph.neighbors(region):
        if neighbor in coloring:
            blocked.add(coloring[neighbor])
    return [c for c in COLORS if c not in blocked]

def check_conflicts(graph, coloring):
    bad = []
    for u, v in graph.edges():
        if u in coloring and v in coloring and coloring[u] == coloring[v]:
            bad.append((u, v))
    return bad

def solve_backtracking(graph):
    solver_history = []

    def is_valid(region, color, partial):
        for neighbor in graph.neighbors(region):
            if partial.get(neighbor) == color:
                return False
        return True

    def backtrack(partial):
        if len(partial) == len(graph.nodes()):
            solver_history.append("Solution complete.")
            return dict(partial)

        uncolored = [n for n in graph.nodes() if n not in partial]
        region = uncolored[0]

        for color in COLORS:
            solver_history.append(f"Trying {region} = {color}")
            if is_valid(region, color, partial):
                partial[region] = color
                solver_history.append(f"Placed {region} = {color}")
                result = backtrack(partial)
                if result is not None:
                    return result
                solver_history.append(f"Backtracking from {region} = {color}")
                del partial[region]
            else:
                solver_history.append(f"Conflict: {region} cannot be {color}")

        return None

    result = backtrack({})
    return result, solver_history

def draw_map(graph, coloring, map_name):
    node_colors = []
    for node in graph.nodes():
        if node in coloring:
            node_colors.append(coloring[node].lower())
        else:
            node_colors.append("#9ca3af")

    pos = MAPS[map_name]["pos"]
    fig, ax = plt.subplots(figsize=(4.2, 4.2))

    nx.draw_networkx_edges(
        graph,
        pos,
        ax=ax,
        width=2.0,
        edge_color="#475569"
    )

    nx.draw_networkx_nodes(
        graph,
        pos,
        ax=ax,
        node_color=node_colors,
        node_size=1500,
        linewidths=1.8,
        edgecolors="#ffffff"
    )

    nx.draw_networkx_labels(
        graph,
        pos,
        ax=ax,
        font_size=9,
        font_weight="bold",
        font_color="white"
    )

    ax.set_axis_off()
    ax.set_xlim(0, 1.02)
    ax.set_ylim(0, 1.02)
    fig.tight_layout(pad=0.6)
    return fig

# =========================================================
# CSS
# =========================================================
st.markdown("""
<style>
:root {
    --bg: #f5f7fb;
    --card: #ffffff;
    --border: #e5e7eb;
    --text: #111827;
    --muted: #6b7280;
    --blue: #2563eb;
    --green: #16a34a;
    --red: #dc2626;
    --amber: #d97706;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg);
}

.block-container {
    padding-top: 1.2rem;
    padding-bottom: 1rem;
    max-width: 1380px;
}

.app-title {
    font-size: 2.7rem;
    font-weight: 800;
    color: #1f2937;
    margin-bottom: 0.9rem;
}

.card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 18px;
    box-shadow: 0 10px 25px rgba(15, 23, 42, 0.05);
    height: 100%;
}

.card-title {
    font-size: 1.35rem;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 10px;
}

.subtle {
    color: var(--muted);
    font-size: 0.95rem;
    margin-bottom: 10px;
}

/* cleaner select boxes */
div[data-baseweb="select"] > div {
    border-radius: 12px !important;
    min-height: 46px !important;
}

/* reliable button styling: all buttons polished */
.stButton > button {
    width: 100%;
    min-height: 46px;
    border-radius: 12px;
    border: none;
    font-weight: 700;
    font-size: 15px;
    box-shadow: 0 6px 16px rgba(15, 23, 42, 0.08);
    transition: all 0.2s ease;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 10px 20px rgba(15, 23, 42, 0.12);
}

/* custom colored action links as wrappers */
.btn-blue {
    background: linear-gradient(135deg, #2563eb, #38bdf8);
    color: white;
    padding: 10px 14px;
    border-radius: 12px;
    font-weight: 700;
    text-align: center;
    margin-bottom: 10px;
}
.btn-green {
    background: linear-gradient(135deg, #16a34a, #22c55e);
    color: white;
    padding: 10px 14px;
    border-radius: 12px;
    font-weight: 700;
    text-align: center;
    margin-bottom: 10px;
}
.btn-red {
    background: linear-gradient(135deg, #dc2626, #f87171);
    color: white;
    padding: 10px 14px;
    border-radius: 12px;
    font-weight: 700;
    text-align: center;
    margin-bottom: 10px;
}

/* status boxes */
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

/* tighter page */
[data-testid="stVerticalBlock"] {
    gap: 0.7rem;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================
st.markdown('<div class="app-title">🌍 Map Coloring CSP Solver</div>', unsafe_allow_html=True)

# =========================================================
# MAIN LAYOUT
# =========================================================
left, center, right = st.columns([1.05, 1.1, 1.15], gap="large")

with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🎛 Controls</div>', unsafe_allow_html=True)

    st.selectbox(
        "Map",
        list(MAPS.keys()),
        key="selected_map",
        on_change=reset_state_for_map
    )

    current_graph = build_graph(st.session_state.selected_map)
    current_nodes = MAPS[st.session_state.selected_map]["nodes"]

    region = st.selectbox("Region", current_nodes, key="region_select")
    color = st.selectbox("Color", COLORS, key="color_select")

    st.markdown('<div class="btn-blue">Apply a selected color to the chosen region</div>', unsafe_allow_html=True)
    if st.button("Apply Color", key="apply_btn"):
        conflict_neighbor = neighbor_with_same_color(
            current_graph,
            st.session_state.coloring,
            region,
            color
        )

        if conflict_neighbor is None:
            st.session_state.coloring[region] = color
            st.session_state.history.append(f"Applied {color} to {region}")
            safe_alternatives = get_safe_colors(current_graph, st.session_state.coloring, region)

            st.session_state.status_type = "success"
            st.session_state.status_msg = f"{region} was colored {color} successfully."
            st.session_state.tip_msg = "Good move. Continue coloring the remaining regions."
        else:
            safe_choices = get_safe_colors(current_graph, st.session_state.coloring, region)
            safe_text = ", ".join(safe_choices) if safe_choices else "No safe color available right now"

            st.session_state.history.append(
                f"Conflict: {region} was not colored {color} because neighbor {conflict_neighbor} already uses {color}"
            )
            st.session_state.status_type = "error"
            st.session_state.status_msg = (
                f"Conflict occurred. {region} was not colored because neighboring region "
                f"{conflict_neighbor} already uses {color}."
            )
            st.session_state.tip_msg = f"Try a different color. Suggested safe colors: {safe_text}"

    st.markdown('<div class="btn-green">Use CSP backtracking to color the entire map automatically</div>', unsafe_allow_html=True)
    if st.button("Solve Automatically", key="solve_btn"):
        solution, solve_history = solve_backtracking(current_graph)
        if solution is not None:
            st.session_state.coloring = solution
            st.session_state.history.extend(solve_history)
            st.session_state.status_type = "success"
            st.session_state.status_msg = "Automatic solution found successfully."
            st.session_state.tip_msg = "The solver used CSP backtracking. Check the history to understand the steps."
        else:
            st.session_state.history.extend(solve_history)
            st.session_state.status_type = "error"
            st.session_state.status_msg = "No valid coloring was found with the available colors."
            st.session_state.tip_msg = "Try another map or allow more colors."

    st.markdown('<div class="btn-red">Clear all colors and restart the current map</div>', unsafe_allow_html=True)
    if st.button("Reset", key="reset_btn"):
        reset_state_for_map()
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

with center:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🗺️ Map Visualization</div>', unsafe_allow_html=True)
    current_graph = build_graph(st.session_state.selected_map)
    fig = draw_map(current_graph, st.session_state.coloring, st.session_state.selected_map)
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

    st.markdown('<div class="card-title" style="margin-top:10px;">📜 Algorithm History</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtle">Every valid move, conflict, and solver step appears here.</div>', unsafe_allow_html=True)
    st.markdown('<div class="history-box">', unsafe_allow_html=True)
    st.text_area(
        "History",
        value="\n".join(st.session_state.history),
        height=300,
        key="history_area"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
