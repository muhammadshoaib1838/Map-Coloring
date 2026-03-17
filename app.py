import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt

st.set_page_config(page_title="Map Coloring CSP Solver", layout="wide")

# =========================================================
# CUSTOM CSS
# =========================================================
st.markdown("""
<style>
.main-title {
    font-size: 52px;
    font-weight: 800;
    color: #1f2937;
    margin-bottom: 10px;
}
.section-title {
    font-size: 30px;
    font-weight: 700;
    color: #111827;
    margin-top: 25px;
    margin-bottom: 10px;
}
.info-box {
    background: #dbeafe;
    color: #1e3a8a;
    padding: 14px;
    border-radius: 12px;
    font-size: 17px;
    margin-bottom: 10px;
    border-left: 6px solid #2563eb;
}
.success-box {
    background: #dcfce7;
    color: #166534;
    padding: 14px;
    border-radius: 12px;
    font-size: 17px;
    margin-bottom: 10px;
    border-left: 6px solid #16a34a;
}
.error-box {
    background: #fee2e2;
    color: #991b1b;
    padding: 14px;
    border-radius: 12px;
    font-size: 17px;
    margin-bottom: 10px;
    border-left: 6px solid #dc2626;
}
.tip-box {
    background: #fef3c7;
    color: #92400e;
    padding: 14px;
    border-radius: 12px;
    font-size: 16px;
    margin-bottom: 10px;
    border-left: 6px solid #f59e0b;
}
.history-box textarea {
    background: #ffffff !important;
    color: #000000 !important;
    font-size: 15px !important;
}
.small-note {
    color: #4b5563;
    font-size: 15px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🌍 Map Coloring CSP Solver</div>', unsafe_allow_html=True)

# =========================================================
# MAP DATA
# Maximum around 5 regions per country for clean demo
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
        ]
    },
    "Australia": {
        "nodes": ["WA", "NT", "SA", "Q", "NSW"],
        "edges": [
            ("WA", "NT"),
            ("WA", "SA"),
            ("NT", "SA"),
            ("NT", "Q"),
            ("SA", "Q"),
            ("SA", "NSW"),
            ("Q", "NSW")
        ]
    },
    "India": {
        "nodes": ["Punjab", "Haryana", "Delhi", "UP", "Rajasthan"],
        "edges": [
            ("Punjab", "Haryana"),
            ("Haryana", "Delhi"),
            ("Haryana", "UP"),
            ("Rajasthan", "Haryana"),
            ("Rajasthan", "UP")
        ]
    },
    "USA": {
        "nodes": ["California", "Nevada", "Arizona", "Utah", "Oregon"],
        "edges": [
            ("California", "Nevada"),
            ("California", "Arizona"),
            ("California", "Oregon"),
            ("Nevada", "Arizona"),
            ("Nevada", "Utah")
        ]
    },
    "Europe": {
        "nodes": ["France", "Germany", "Italy", "Spain", "Belgium"],
        "edges": [
            ("France", "Germany"),
            ("France", "Spain"),
            ("France", "Italy"),
            ("France", "Belgium"),
            ("Germany", "Belgium")
        ]
    }
}

COLORS = ["Red", "Green", "Blue"]

# =========================================================
# SESSION STATE
# =========================================================
if "selected_map" not in st.session_state:
    st.session_state.selected_map = list(MAPS.keys())[0]

if "coloring" not in st.session_state:
    st.session_state.coloring = {}

if "history" not in st.session_state:
    st.session_state.history = []

if "message_html" not in st.session_state:
    st.session_state.message_html = '<div class="info-box">Select a map, choose a region, and apply a color.</div>'

if "tip_html" not in st.session_state:
    st.session_state.tip_html = '<div class="tip-box">Tip: Neighboring regions must have different colors.</div>'

# =========================================================
# HELPERS
# =========================================================
def reset_for_new_map():
    st.session_state.coloring = {}
    st.session_state.history = []
    st.session_state.message_html = '<div class="info-box">New map loaded. Start assigning colors.</div>'
    st.session_state.tip_html = '<div class="tip-box">Tip: Use Red, Green, and Blue carefully so adjacent regions stay different.</div>'

def build_graph(map_name):
    data = MAPS[map_name]
    graph = nx.Graph()
    graph.add_nodes_from(data["nodes"])
    graph.add_edges_from(data["edges"])
    return graph

def check_conflicts(graph, coloring):
    conflicts = []
    for u, v in graph.edges():
        if u in coloring and v in coloring and coloring[u] == coloring[v]:
            conflicts.append((u, v))
    return conflicts

def get_conflicting_neighbor(graph, coloring, region, chosen_color):
    for neighbor in graph.neighbors(region):
        if neighbor in coloring and coloring[neighbor] == chosen_color:
            return neighbor
    return None

def available_colors_for_region(graph, coloring, region):
    used = set()
    for neighbor in graph.neighbors(region):
        if neighbor in coloring:
            used.add(coloring[neighbor])
    return [c for c in COLORS if c not in used]

def is_valid_assignment(graph, coloring, region, chosen_color):
    for neighbor in graph.neighbors(region):
        if neighbor in coloring and coloring[neighbor] == chosen_color:
            return False
    return True

def solve_map_backtracking(graph):
    history = []

    def backtrack(local_coloring):
        if len(local_coloring) == len(graph.nodes()):
            history.append("✅ Solution complete: all regions colored successfully.")
            return dict(local_coloring)

        uncolored = [node for node in graph.nodes() if node not in local_coloring]
        region = uncolored[0]

        for color in COLORS:
            history.append(f"Trying {region} = {color}")
            if is_valid_assignment(graph, local_coloring, region, color):
                local_coloring[region] = color
                history.append(f"Placed {region} = {color}")
                result = backtrack(local_coloring)
                if result is not None:
                    return result
                history.append(f"Backtracking from {region} = {color}")
                del local_coloring[region]
            else:
                history.append(f"Conflict: {region} cannot be {color}")

        return None

    solution = backtrack({})
    return solution, history

def draw_graph(graph, coloring, conflicts):
    color_map = []
    for node in graph.nodes():
        if node in coloring:
            color_map.append(coloring[node].lower())
        else:
            color_map.append("#9ca3af")  # gray

    fig, ax = plt.subplots(figsize=(4.2, 4.2))
    pos = nx.spring_layout(graph, seed=42, k=0.9)

    nx.draw(
        graph,
        pos,
        ax=ax,
        with_labels=True,
        node_color=color_map,
        node_size=1300,
        font_size=9,
        font_weight="bold",
        font_color="white",
        width=1.5,
        edge_color="#374151"
    )

    if conflicts:
        nx.draw_networkx_edges(
            graph,
            pos,
            ax=ax,
            edgelist=conflicts,
            edge_color="red",
            width=3
        )

    ax.set_axis_off()
    plt.tight_layout()
    return fig

# =========================================================
# MAP SELECTION
# =========================================================
selected_map = st.selectbox("Select Map", list(MAPS.keys()), key="selected_map", on_change=reset_for_new_map)
G = build_graph(selected_map)

# =========================================================
# INPUT AREA
# =========================================================
st.markdown('<div class="section-title">🎯 Assign Colors</div>', unsafe_allow_html=True)

left, right = st.columns(2)
with left:
    region = st.selectbox("Select Region", list(G.nodes()))
with right:
    color = st.selectbox("Select Color", COLORS)

button_col1, button_col2, button_col3 = st.columns([1, 1, 1])

with button_col1:
    apply_clicked = st.button("Apply Color", use_container_width=True)

with button_col2:
    solve_clicked = st.button("Solve Automatically", use_container_width=True)

with button_col3:
    reset_clicked = st.button("Reset", use_container_width=True)

# =========================================================
# BUTTON ACTIONS
# =========================================================
if apply_clicked:
    available = available_colors_for_region(G, st.session_state.coloring, region)

    if is_valid_assignment(G, st.session_state.coloring, region, color):
        st.session_state.coloring[region] = color
        st.session_state.history.append(f"✅ Applied {color} to {region}")

        st.session_state.message_html = f"""
        <div class="success-box">
            {region} was colored <b>{color}</b> successfully.
        </div>
        """

        if len(available) > 1:
            suggestion = ", ".join(available)
            st.session_state.tip_html = f"""
            <div class="tip-box">
                Good choice. Other safe colors for <b>{region}</b> were: {suggestion}
            </div>
            """
        else:
            st.session_state.tip_html = """
            <div class="tip-box">
                Good choice. Keep checking neighboring regions before applying the next color.
            </div>
            """
    else:
        bad_neighbor = get_conflicting_neighbor(G, st.session_state.coloring, region, color)
        st.session_state.history.append(
            f"❌ Conflict: could not apply {color} to {region} because neighboring region {bad_neighbor} already has {color}"
        )

        suggestions = available_colors_for_region(G, st.session_state.coloring, region)
        suggestion_text = ", ".join(suggestions) if suggestions else "No available colors"

        st.session_state.message_html = f"""
        <div class="error-box">
            Conflict occurred. <b>{region}</b> was <u>not colored</u> because neighboring region
            <b>{bad_neighbor}</b> already uses <b>{color}</b>.
        </div>
        """

        st.session_state.tip_html = f"""
        <div class="tip-box">
            Tip: Try a different color for <b>{region}</b>. Suggested safe colors: <b>{suggestion_text}</b>
        </div>
        """

if solve_clicked:
    solution, solve_history = solve_map_backtracking(G)
    if solution is not None:
        st.session_state.coloring = solution
        st.session_state.history.extend(solve_history)
        st.session_state.message_html = """
        <div class="success-box">
            Automatic CSP solution found successfully.
        </div>
        """
        st.session_state.tip_html = """
        <div class="tip-box">
            Tip: Observe the history to understand how backtracking tries colors, detects conflicts, and then corrects them.
        </div>
        """
    else:
        st.session_state.history.extend(solve_history)
        st.session_state.message_html = """
        <div class="error-box">
            No valid coloring exists for this map with the available colors.
        </div>
        """
        st.session_state.tip_html = """
        <div class="tip-box">
            Tip: Sometimes you may need more colors if a valid solution cannot be found.
        </div>
        """

if reset_clicked:
    reset_for_new_map()
    st.rerun()

# =========================================================
# STATUS + TIP
# =========================================================
st.markdown('<div class="section-title">📊 Status</div>', unsafe_allow_html=True)
st.markdown(st.session_state.message_html, unsafe_allow_html=True)
st.markdown(st.session_state.tip_html, unsafe_allow_html=True)

# =========================================================
# VISUALIZATION + HISTORY
# =========================================================
vis_col, hist_col = st.columns([1, 1])

with vis_col:
    st.markdown('<div class="section-title">🗺️ Map Visualization</div>', unsafe_allow_html=True)
    current_conflicts = check_conflicts(G, st.session_state.coloring)
    fig = draw_graph(G, st.session_state.coloring, current_conflicts)
    st.pyplot(fig)

with hist_col:
    st.markdown('<div class="section-title">📜 Algorithm History</div>', unsafe_allow_html=True)
    st.markdown('<div class="small-note">Every valid move, conflict, and solver step appears here.</div>', unsafe_allow_html=True)
    st.markdown('<div class="history-box">', unsafe_allow_html=True)
    st.text_area(
        "History",
        value="\n".join(st.session_state.history),
        height=320,
        key="history_area"
    )
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# EXPLANATION
# =========================================================
st.markdown('<div class="section-title">📘 Explanation</div>', unsafe_allow_html=True)
st.markdown("""
<div class="info-box">
<b>What is Map Coloring CSP?</b><br>
A map coloring problem is a Constraint Satisfaction Problem (CSP).<br><br>
<b>Variables:</b> Regions of the selected map<br>
<b>Domain:</b> Available colors = Red, Green, Blue<br>
<b>Constraint:</b> Two neighboring regions cannot have the same color
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="tip-box">
<b>Professional Suggestions:</b><br>
1. Start with a central region first.<br>
2. Check its neighbors before assigning the next color.<br>
3. If conflict happens, do not force the same color again.<br>
4. Use the algorithm history to understand each step.<br>
5. Try a different color when the app explains a conflict.
</div>
""", unsafe_allow_html=True)
