import streamlit as st
from html import escape

st.set_page_config(page_title="Map Coloring AI Visualizer", layout="wide")

# =========================================================
# CONFIG / DATA
# =========================================================

COLORS = {
    "Uncolored": "#D1D5DB",
    "Red": "#EF4444",
    "Green": "#22C55E",
    "Blue": "#3B82F6",
    "Yellow": "#F59E0B",
}

MAPS = {
    "Pakistan": {
        "title": "Pakistan Map Coloring",
        "regions": ["Balochistan", "Sindh", "Punjab", "KPK", "Islamabad"],
        # Neighboring regions must have different colors
        "adjacency": {
            "Balochistan": ["Sindh", "Punjab", "KPK"],
            "Sindh": ["Balochistan", "Punjab"],
            "Punjab": ["Balochistan", "Sindh", "KPK", "Islamabad"],
            "KPK": ["Balochistan", "Punjab", "Islamabad"],
            "Islamabad": ["Punjab", "KPK"],
        },
        # Simple SVG shapes (clean educational map-style version)
        "svg_regions": {
            "Balochistan": {
                "path": "M 40 220 L 120 120 L 210 110 L 250 165 L 220 245 L 135 280 L 60 265 Z",
                "label_x": 145,
                "label_y": 200,
            },
            "Sindh": {
                "path": "M 220 245 L 270 225 L 315 250 L 330 330 L 280 370 L 220 330 L 205 280 Z",
                "label_x": 275,
                "label_y": 305,
            },
            "Punjab": {
                "path": "M 250 165 L 340 130 L 410 155 L 420 230 L 360 270 L 315 250 L 270 225 L 220 245 Z",
                "label_x": 332,
                "label_y": 205,
            },
            "KPK": {
                "path": "M 235 95 L 305 70 L 350 95 L 340 130 L 250 165 L 210 110 Z",
                "label_x": 285,
                "label_y": 112,
            },
            "Islamabad": {
                "path": "M 355 145 L 375 138 L 388 152 L 380 168 L 360 170 L 350 156 Z",
                "label_x": 370,
                "label_y": 156,
            },
        },
        "viewbox": "0 0 470 420",
    },
    "Australia": {
        "title": "Australia Map Coloring",
        "regions": ["WA", "NT", "SA", "QLD", "NSW"],
        "adjacency": {
            "WA": ["NT", "SA"],
            "NT": ["WA", "SA", "QLD"],
            "SA": ["WA", "NT", "QLD", "NSW"],
            "QLD": ["NT", "SA", "NSW"],
            "NSW": ["SA", "QLD"],
        },
        "svg_regions": {
            "WA": {
                "path": "M 40 90 L 160 90 L 160 250 L 55 270 L 35 220 Z",
                "label_x": 98,
                "label_y": 175,
            },
            "NT": {
                "path": "M 160 90 L 260 90 L 260 180 L 160 180 Z",
                "label_x": 210,
                "label_y": 140,
            },
            "SA": {
                "path": "M 160 180 L 280 180 L 280 280 L 155 280 Z",
                "label_x": 220,
                "label_y": 235,
            },
            "QLD": {
                "path": "M 260 90 L 385 105 L 390 220 L 280 220 L 260 180 Z",
                "label_x": 330,
                "label_y": 155,
            },
            "NSW": {
                "path": "M 280 220 L 390 220 L 375 305 L 290 298 L 280 280 Z",
                "label_x": 334,
                "label_y": 262,
            },
        },
        "viewbox": "0 0 430 350",
    },
}

# =========================================================
# SESSION STATE
# =========================================================

if "selected_map" not in st.session_state:
    st.session_state.selected_map = "Pakistan"

if "coloring" not in st.session_state:
    st.session_state.coloring = {region: "Uncolored" for region in MAPS["Pakistan"]["regions"]}

if "history" not in st.session_state:
    st.session_state.history = ["App started. Select a region and color, then click Apply Color."]

if "status_html" not in st.session_state:
    st.session_state.status_html = "<div class='status info'>Ready to start coloring.</div>"

if "tip_html" not in st.session_state:
    st.session_state.tip_html = "<div class='tip'>Tip: neighboring regions must have different colors.</div>"


def reset_map_state(map_name: str):
    st.session_state.selected_map = map_name
    st.session_state.coloring = {region: "Uncolored" for region in MAPS[map_name]["regions"]}
    st.session_state.history = [f"Loaded {map_name} map."]
    st.session_state.status_html = "<div class='status info'>Map reset successfully.</div>"
    st.session_state.tip_html = "<div class='tip'>Tip: start with a central region, then color its neighbors with different colors.</div>"


# =========================================================
# CSP LOGIC
# =========================================================

def has_conflict(map_key: str, coloring: dict, region: str, color_name: str):
    """Return the conflicting neighbor if same color is already used by a neighbor."""
    neighbors = MAPS[map_key]["adjacency"][region]
    for neighbor in neighbors:
        if coloring.get(neighbor) == color_name:
            return neighbor
    return None


def safe_colors_for_region(map_key: str, coloring: dict, region: str):
    safe = []
    for color_name in ["Red", "Green", "Blue"]:
        if has_conflict(map_key, coloring, region, color_name) is None:
            safe.append(color_name)
    return safe


def solve_backtracking(map_key: str):
    regions = MAPS[map_key]["regions"]
    adjacency = MAPS[map_key]["adjacency"]
    logs = []

    def is_valid(region: str, color_name: str, assignment: dict):
        for neighbor in adjacency[region]:
            if assignment.get(neighbor) == color_name:
                return False
        return True

    def backtrack(assignment: dict):
        if len(assignment) == len(regions):
            logs.append("✅ Solution complete.")
            return dict(assignment)

        uncolored = [r for r in regions if r not in assignment]
        region = uncolored[0]

        for color_name in ["Red", "Green", "Blue"]:
            logs.append(f"Trying {region} = {color_name}")
            if is_valid(region, color_name, assignment):
                assignment[region] = color_name
                logs.append(f"Placed {region} = {color_name}")
                result = backtrack(assignment)
                if result is not None:
                    return result
                logs.append(f"Backtracking from {region} = {color_name}")
                del assignment[region]
            else:
                logs.append(f"Conflict: {region} cannot be {color_name}")

        return None

    solution = backtrack({})
    return solution, logs


# =========================================================
# SVG MAP RENDERER
# =========================================================

def render_svg_map(map_key: str, coloring: dict):
    map_data = MAPS[map_key]
    parts = []

    for region, info in map_data["svg_regions"].items():
        fill = COLORS.get(coloring.get(region, "Uncolored"), "#D1D5DB")
        parts.append(
            f"""
            <path d="{info['path']}"
                  fill="{fill}"
                  stroke="#FFFFFF"
                  stroke-width="3"
                  style="transition: fill 0.25s ease;" />
            <text x="{info['label_x']}" y="{info['label_y']}"
                  text-anchor="middle"
                  dominant-baseline="middle"
                  font-size="16"
                  font-weight="700"
                  fill="#ffffff">{escape(region)}</text>
            """
        )

    svg = f"""
    <div class="map-card">
      <svg viewBox="{map_data['viewbox']}" class="map-svg" xmlns="http://www.w3.org/2000/svg">
        <rect x="0" y="0" width="100%" height="100%" fill="#F8FAFC" rx="16" />
        {"".join(parts)}
      </svg>
    </div>
    """
    return svg


# =========================================================
# STYLES
# =========================================================

st.markdown(
    """
    <style>
    :root {
        --bg: #F3F6FB;
        --card: #FFFFFF;
        --border: #E5E7EB;
        --text: #111827;
        --muted: #6B7280;
        --blue: #2563EB;
        --blue2: #38BDF8;
        --green: #16A34A;
        --green2: #22C55E;
        --red: #DC2626;
        --red2: #F87171;
        --amber: #D97706;
    }

    html, body, [data-testid="stAppViewContainer"] {
        background: var(--bg);
    }

    .block-container {
        max-width: 1450px;
        padding-top: 1.1rem;
        padding-bottom: 1rem;
    }

    .app-title {
        font-size: 2.6rem;
        font-weight: 800;
        color: #0F172A;
        margin-bottom: 0.9rem;
    }

    .app-subtitle {
        font-size: 1rem;
        color: var(--muted);
        margin-top: -0.3rem;
        margin-bottom: 1rem;
    }

    .panel {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 18px;
        box-shadow: 0 10px 24px rgba(15, 23, 42, 0.05);
        height: 100%;
    }

    .panel-title {
        font-size: 1.35rem;
        font-weight: 800;
        color: #0F172A;
        margin-bottom: 12px;
    }

    .status {
        padding: 14px;
        border-radius: 12px;
        font-weight: 600;
        margin-bottom: 12px;
        border-left: 6px solid transparent;
    }

    .status.success {
        background: #DCFCE7;
        color: #166534;
        border-left-color: #16A34A;
    }

    .status.error {
        background: #FEE2E2;
        color: #991B1B;
        border-left-color: #DC2626;
    }

    .status.info {
        background: #DBEAFE;
        color: #1D4ED8;
        border-left-color: #2563EB;
    }

    .tip {
        background: #FEF3C7;
        color: #92400E;
        border-left: 6px solid #D97706;
        padding: 14px;
        border-radius: 12px;
        font-weight: 600;
        margin-bottom: 12px;
    }

    .map-card {
        background: #FFFFFF;
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 10px;
        display: flex;
        justify-content: center;
        align-items: center;
    }

    .map-svg {
        width: 100%;
        max-width: 520px;
        height: auto;
        display: block;
    }

    div[data-baseweb="select"] > div {
        min-height: 46px !important;
        border-radius: 12px !important;
    }

    .history-note {
        color: var(--muted);
        font-size: 0.95rem;
        margin-bottom: 10px;
    }

    .history-box textarea {
        background: #FFFFFF !important;
        color: #000000 !important;
        border-radius: 12px !important;
    }

    /* Professional button styling */
    .stButton > button {
        width: 100%;
        min-height: 48px;
        border-radius: 12px;
        border: none;
        font-size: 15px;
        font-weight: 700;
        color: white;
        box-shadow: 0 8px 18px rgba(15, 23, 42, 0.10);
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 12px 22px rgba(15, 23, 42, 0.14);
    }

    /* Color the three action buttons by their stable keys order inside the row */
    [data-testid="column"] .stButton:nth-of-type(1) button {
        background: linear-gradient(135deg, var(--blue), var(--blue2));
    }
    [data-testid="column"] .stButton:nth-of-type(2) button {
        background: linear-gradient(135deg, var(--green), var(--green2));
    }
    [data-testid="column"] .stButton:nth-of-type(3) button {
        background: linear-gradient(135deg, var(--red), var(--red2));
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# HEADER
# =========================================================

st.markdown('<div class="app-title">🌍 Map Coloring AI Visualizer</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="app-subtitle">Real-region coloring using SVG shapes, conflict checking, and CSP backtracking logs.</div>',
    unsafe_allow_html=True,
)

# =========================================================
# MAIN LAYOUT
# =========================================================

left, center, right = st.columns([1.05, 1.1, 1.15], gap="large")

with left:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">🎛 Controls</div>', unsafe_allow_html=True)

    selected_map = st.selectbox(
        "Map",
        list(MAPS.keys()),
        index=list(MAPS.keys()).index(st.session_state.selected_map),
        key="map_selector",
    )

    if selected_map != st.session_state.selected_map:
        reset_map_state(selected_map)
        st.rerun()

    current_regions = MAPS[st.session_state.selected_map]["regions"]
    region = st.selectbox("Region", current_regions, key="region_selector")
    color = st.selectbox("Color", ["Red", "Green", "Blue"], key="color_selector")

    b1, b2, b3 = st.columns(3)

    with b1:
        apply_clicked = st.button("Apply Color", key="apply_btn")

    with b2:
        solve_clicked = st.button("Solve Automatically", key="solve_btn")

    with b3:
        reset_clicked = st.button("Reset", key="reset_btn")

    current_graph = build_graph(st.session_state.selected_map)

    if apply_clicked:
        conflict_neighbor = has_conflict(
            st.session_state.selected_map,
            st.session_state.coloring,
            region,
            color,
        )

        if conflict_neighbor is None:
            st.session_state.coloring[region] = color
            st.session_state.history.append(f"Applied {color} to {region}")
            st.session_state.status_html = f"<div class='status success'>{region} was colored {color} successfully.</div>"
            st.session_state.tip_html = "<div class='tip'>Good move. Continue coloring the remaining regions.</div>"
        else:
            options = safe_colors_for_region(
                st.session_state.selected_map,
                st.session_state.coloring,
                region,
            )
            option_text = ", ".join(options) if options else "No safe colors available"
            st.session_state.history.append(
                f"Conflict: {region} was not colored because neighboring region {conflict_neighbor} already uses {color}"
            )
            st.session_state.status_html = (
                f"<div class='status error'>Conflict occurred. "
                f"{region} was not colored because neighboring region "
                f"{conflict_neighbor} already uses {color}.</div>"
            )
            st.session_state.tip_html = f"<div class='tip'>Try a different color. Suggested safe colors: {option_text}</div>"

    if solve_clicked:
        solution, logs = solve_backtracking(st.session_state.selected_map)
        if solution is not None:
            st.session_state.coloring = {region_name: solution.get(region_name, "Uncolored") for region_name in current_regions}
            st.session_state.history.extend(logs)
            st.session_state.status_html = "<div class='status success'>Automatic solution found successfully.</div>"
            st.session_state.tip_html = "<div class='tip'>The solver used backtracking. Review the history to understand each step.</div>"
        else:
            st.session_state.history.extend(logs)
            st.session_state.status_html = "<div class='status error'>No valid coloring was found for this map.</div>"
            st.session_state.tip_html = "<div class='tip'>Try another map or modify the available colors.</div>"

    if reset_clicked:
        reset_map_state(st.session_state.selected_map)
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

with center:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">🗺️ Map Visualization</div>', unsafe_allow_html=True)
    st.markdown(
        render_svg_map(st.session_state.selected_map, st.session_state.coloring),
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">📊 Status</div>', unsafe_allow_html=True)
    st.markdown(st.session_state.status_html, unsafe_allow_html=True)
    st.markdown(st.session_state.tip_html, unsafe_allow_html=True)

    st.markdown('<div class="panel-title" style="margin-top:10px;">📜 Algorithm History</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="history-note">Every valid move, conflict, and solver step appears here.</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="history-box">', unsafe_allow_html=True)
    st.text_area(
        "History",
        value="\n".join(st.session_state.history),
        height=320,
        key="history_area",
    )
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
