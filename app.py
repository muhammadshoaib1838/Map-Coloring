import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Map Coloring AI Visualizer", layout="wide")

# =========================================================
# CONFIG
# =========================================================
COLORS = {
    "None": "#D1D5DB",
    "Red": "#EF4444",
    "Green": "#22C55E",
    "Blue": "#3B82F6",
    "Yellow": "#F59E0B",
    "Purple": "#8B5CF6",
}
COLOR_LIST = ["Red", "Green", "Blue", "Yellow", "Purple"]

# =========================================================
# MAP TEMPLATES
# Each country has 5 real region names.
# Shapes are simplified SVG regions for assignment/demo use.
# =========================================================
COUNTRIES = {
    "Pakistan": {
        "regions": ["Punjab", "Sindh", "Balochistan", "KPK", "Islamabad"],
        "neighbors": {
            "Punjab": ["Sindh", "Balochistan", "KPK", "Islamabad"],
            "Sindh": ["Punjab", "Balochistan"],
            "Balochistan": ["Sindh", "Punjab", "KPK"],
            "KPK": ["Punjab", "Balochistan", "Islamabad"],
            "Islamabad": ["Punjab", "KPK"],
        },
        "svg": {
            "Punjab": (
                "M 250 160 L 360 130 L 420 180 L 380 260 L 300 240 L 240 200 Z",
                328, 198
            ),
            "Sindh": (
                "M 260 240 L 330 260 L 360 350 L 300 400 L 240 350 L 220 280 Z",
                296, 320
            ),
            "Balochistan": (
                "M 40 240 L 150 140 L 250 160 L 240 200 L 180 260 L 80 280 Z",
                150, 215
            ),
            "KPK": (
                "M 200 100 L 300 80 L 360 130 L 250 160 L 150 140 Z",
                258, 118
            ),
            "Islamabad": (
                "M 325 150 L 350 145 L 362 165 L 332 176 Z",
                343, 160
            ),
        },
        "viewbox": "0 0 470 430",
    },
    "India": {
        "regions": ["Punjab", "Rajasthan", "UP", "Gujarat", "Delhi"],
        "neighbors": {
            "Punjab": ["Rajasthan", "Delhi"],
            "Rajasthan": ["Punjab", "UP", "Gujarat", "Delhi"],
            "UP": ["Rajasthan", "Delhi"],
            "Gujarat": ["Rajasthan"],
            "Delhi": ["Punjab", "Rajasthan", "UP"],
        },
        "svg": {
            "Punjab": ("M 90 120 L 170 100 L 200 145 L 125 165 Z", 145, 130),
            "Rajasthan": ("M 120 165 L 205 145 L 260 220 L 180 260 L 105 220 Z", 175, 205),
            "UP": ("M 205 145 L 315 140 L 330 205 L 260 220 Z", 270, 175),
            "Gujarat": ("M 105 220 L 180 260 L 190 330 L 125 355 L 90 285 Z", 145, 290),
            "Delhi": ("M 230 160 L 248 158 L 252 178 L 232 180 Z", 242, 170),
        },
        "viewbox": "0 0 380 420",
    },
    "Australia": {
        "regions": ["WA", "NT", "SA", "Queensland", "NSW"],
        "neighbors": {
            "WA": ["NT", "SA"],
            "NT": ["WA", "SA", "Queensland"],
            "SA": ["WA", "NT", "Queensland", "NSW"],
            "Queensland": ["NT", "SA", "NSW"],
            "NSW": ["SA", "Queensland"],
        },
        "svg": {
            "WA": ("M 35 110 L 155 110 L 155 255 L 55 280 L 35 225 Z", 95, 185),
            "NT": ("M 155 110 L 270 110 L 270 195 L 155 195 Z", 212, 150),
            "SA": ("M 155 195 L 290 195 L 290 300 L 150 300 Z", 220, 245),
            "Queensland": ("M 270 110 L 395 125 L 400 235 L 290 235 L 270 195 Z", 338, 170),
            "NSW": ("M 290 235 L 400 235 L 385 320 L 300 315 L 290 300 Z", 345, 275),
        },
        "viewbox": "0 0 440 360",
    },
    "USA": {
        "regions": ["California", "Nevada", "Arizona", "Utah", "Oregon"],
        "neighbors": {
            "California": ["Nevada", "Arizona", "Oregon"],
            "Nevada": ["California", "Arizona", "Utah", "Oregon"],
            "Arizona": ["California", "Nevada", "Utah"],
            "Utah": ["Nevada", "Arizona"],
            "Oregon": ["California", "Nevada"],
        },
        "svg": {
            "Oregon": ("M 70 70 L 155 70 L 165 130 L 80 135 Z", 118, 102),
            "California": ("M 80 135 L 165 130 L 150 250 L 105 335 L 70 300 Z", 120, 235),
            "Nevada": ("M 165 130 L 245 120 L 255 220 L 180 235 Z", 210, 180),
            "Utah": ("M 245 120 L 320 120 L 322 225 L 255 220 Z", 285, 175),
            "Arizona": ("M 180 235 L 255 220 L 322 225 L 300 320 L 205 315 Z", 252, 275),
        },
        "viewbox": "0 0 380 380",
    },
    "China": {
        "regions": ["Xinjiang", "Tibet", "Sichuan", "Beijing", "Shanghai"],
        "neighbors": {
            "Xinjiang": ["Tibet", "Sichuan"],
            "Tibet": ["Xinjiang", "Sichuan"],
            "Sichuan": ["Xinjiang", "Tibet", "Beijing", "Shanghai"],
            "Beijing": ["Sichuan", "Shanghai"],
            "Shanghai": ["Sichuan", "Beijing"],
        },
        "svg": {
            "Xinjiang": ("M 35 120 L 145 95 L 175 175 L 90 220 L 30 185 Z", 95, 155),
            "Tibet": ("M 75 220 L 185 180 L 220 260 L 120 300 L 60 270 Z", 135, 245),
            "Sichuan": ("M 185 160 L 275 150 L 300 250 L 220 260 L 175 175 Z", 235, 205),
            "Beijing": ("M 305 120 L 350 115 L 360 155 L 315 160 Z", 333, 138),
            "Shanghai": ("M 320 220 L 355 215 L 360 255 L 325 262 Z", 341, 238),
        },
        "viewbox": "0 0 400 340",
    },
    "Brazil": {
        "regions": ["Amazonas", "Para", "Bahia", "Sao Paulo", "Rio"],
        "neighbors": {
            "Amazonas": ["Para"],
            "Para": ["Amazonas", "Bahia"],
            "Bahia": ["Para", "Sao Paulo", "Rio"],
            "Sao Paulo": ["Bahia", "Rio"],
            "Rio": ["Bahia", "Sao Paulo"],
        },
        "svg": {
            "Amazonas": ("M 40 120 L 155 90 L 205 160 L 135 220 L 55 205 Z", 120, 155),
            "Para": ("M 205 120 L 310 110 L 335 180 L 250 220 L 185 165 Z", 260, 160),
            "Bahia": ("M 250 220 L 335 180 L 355 275 L 290 320 L 235 270 Z", 298, 250),
            "Sao Paulo": ("M 220 305 L 285 300 L 290 345 L 235 355 Z", 255, 328),
            "Rio": ("M 290 315 L 335 312 L 340 350 L 300 355 Z", 315, 333),
        },
        "viewbox": "0 0 390 390",
    },
    "Canada": {
        "regions": ["BC", "Alberta", "Manitoba", "Ontario", "Quebec"],
        "neighbors": {
            "BC": ["Alberta"],
            "Alberta": ["BC", "Manitoba", "Ontario"],
            "Manitoba": ["Alberta", "Ontario"],
            "Ontario": ["Alberta", "Manitoba", "Quebec"],
            "Quebec": ["Ontario"],
        },
        "svg": {
            "BC": ("M 30 120 L 90 110 L 95 235 L 50 275 L 25 220 Z", 60, 190),
            "Alberta": ("M 95 110 L 160 105 L 160 245 L 98 245 Z", 128, 176),
            "Manitoba": ("M 160 105 L 225 108 L 225 245 L 160 245 Z", 192, 176),
            "Ontario": ("M 225 110 L 315 120 L 310 250 L 225 245 Z", 268, 178),
            "Quebec": ("M 315 120 L 385 135 L 378 248 L 310 250 Z", 348, 182),
        },
        "viewbox": "0 0 420 320",
    },
    "Germany": {
        "regions": ["Bavaria", "Berlin", "Hamburg", "Hesse", "Saxony"],
        "neighbors": {
            "Bavaria": ["Hesse", "Saxony"],
            "Berlin": ["Hamburg", "Saxony"],
            "Hamburg": ["Berlin", "Hesse"],
            "Hesse": ["Hamburg", "Bavaria"],
            "Saxony": ["Berlin", "Bavaria"],
        },
        "svg": {
            "Hamburg": ("M 140 55 L 185 55 L 190 95 L 145 95 Z", 165, 74),
            "Berlin": ("M 245 70 L 290 68 L 292 108 L 248 110 Z", 270, 88),
            "Hesse": ("M 135 145 L 205 140 L 210 225 L 140 228 Z", 173, 182),
            "Saxony": ("M 240 155 L 320 150 L 320 220 L 248 225 Z", 282, 186),
            "Bavaria": ("M 175 235 L 300 230 L 315 325 L 190 330 Z", 247, 282),
        },
        "viewbox": "0 0 360 380",
    },
    "France": {
        "regions": ["Brittany", "Normandy", "Paris", "Lyon", "Marseille"],
        "neighbors": {
            "Brittany": ["Normandy", "Paris"],
            "Normandy": ["Brittany", "Paris"],
            "Paris": ["Brittany", "Normandy", "Lyon"],
            "Lyon": ["Paris", "Marseille"],
            "Marseille": ["Lyon"],
        },
        "svg": {
            "Brittany": ("M 35 140 L 95 120 L 110 170 L 55 200 Z", 72, 156),
            "Normandy": ("M 100 110 L 175 108 L 182 165 L 118 170 Z", 142, 138),
            "Paris": ("M 155 165 L 225 160 L 228 225 L 160 228 Z", 192, 194),
            "Lyon": ("M 205 230 L 285 225 L 290 300 L 215 305 Z", 248, 265),
            "Marseille": ("M 245 305 L 320 300 L 322 350 L 260 355 Z", 286, 328),
        },
        "viewbox": "0 0 360 390",
    },
    "Japan": {
        "regions": ["Hokkaido", "Tohoku", "Kanto", "Kansai", "Kyushu"],
        "neighbors": {
            "Hokkaido": ["Tohoku"],
            "Tohoku": ["Hokkaido", "Kanto"],
            "Kanto": ["Tohoku", "Kansai"],
            "Kansai": ["Kanto", "Kyushu"],
            "Kyushu": ["Kansai"],
        },
        "svg": {
            "Hokkaido": ("M 270 45 L 335 40 L 350 95 L 285 110 L 248 78 Z", 300, 72),
            "Tohoku": ("M 235 120 L 295 115 L 300 205 L 240 210 Z", 268, 160),
            "Kanto": ("M 225 210 L 285 208 L 290 275 L 228 278 Z", 258, 243),
            "Kansai": ("M 170 255 L 225 245 L 235 302 L 182 315 Z", 203, 280),
            "Kyushu": ("M 100 295 L 165 282 L 172 345 L 112 352 Z", 137, 318),
        },
        "viewbox": "0 0 390 390",
    },
    "South Africa": {
        "regions": ["Western Cape", "Eastern Cape", "Gauteng", "KwaZulu-Natal", "Limpopo"],
        "neighbors": {
            "Western Cape": ["Eastern Cape"],
            "Eastern Cape": ["Western Cape", "Gauteng", "KwaZulu-Natal"],
            "Gauteng": ["Eastern Cape", "KwaZulu-Natal", "Limpopo"],
            "KwaZulu-Natal": ["Eastern Cape", "Gauteng"],
            "Limpopo": ["Gauteng"],
        },
        "svg": {
            "Western Cape": ("M 35 275 L 120 260 L 145 310 L 75 345 L 32 320 Z", 88, 302),
            "Eastern Cape": ("M 145 255 L 245 250 L 268 310 L 175 338 L 120 305 Z", 190, 292),
            "Gauteng": ("M 220 165 L 275 160 L 285 205 L 230 215 Z", 252, 188),
            "KwaZulu-Natal": ("M 280 210 L 340 205 L 350 295 L 295 302 Z", 316, 252),
            "Limpopo": ("M 250 85 L 340 82 L 355 150 L 275 155 Z", 304, 118),
        },
        "viewbox": "0 0 390 390",
    },
}

# =========================================================
# STATE
# =========================================================
if "selected_country" not in st.session_state:
    st.session_state.selected_country = "Pakistan"

if "region_colors" not in st.session_state:
    st.session_state.region_colors = {r: "None" for r in COUNTRIES["Pakistan"]["regions"]}

if "history" not in st.session_state:
    st.session_state.history = ["App started. Select a region and color, then click Apply Color."]

if "status_msg" not in st.session_state:
    st.session_state.status_msg = "Ready"

if "tip_msg" not in st.session_state:
    st.session_state.tip_msg = "Tip: neighboring regions must have different colors."

def reset_country(country_name: str):
    st.session_state.selected_country = country_name
    st.session_state.region_colors = {r: "None" for r in COUNTRIES[country_name]["regions"]}
    st.session_state.history = [f"Loaded {country_name} map."]
    st.session_state.status_msg = "Map reset successfully."
    st.session_state.tip_msg = "Tip: start from a central region and use different colors for its neighbors."

# =========================================================
# HELPERS
# =========================================================
def conflict_neighbor(country_name: str, region: str, color_name: str):
    for neighbor in COUNTRIES[country_name]["neighbors"][region]:
        if st.session_state.region_colors.get(neighbor) == color_name:
            return neighbor
    return None

def safe_color_suggestions(country_name: str, region: str):
    safe = []
    for color_name in COLOR_LIST:
        if conflict_neighbor(country_name, region, color_name) is None:
            safe.append(color_name)
    return safe

def solve_backtracking(country_name: str):
    regions = COUNTRIES[country_name]["regions"]
    adjacency = COUNTRIES[country_name]["neighbors"]
    logs = []

    def is_valid(region, color_name, assignment):
        for neighbor in adjacency[region]:
            if assignment.get(neighbor) == color_name:
                return False
        return True

    def backtrack(assignment):
        if len(assignment) == len(regions):
            logs.append("Solution complete.")
            return dict(assignment)

        uncolored = [r for r in regions if r not in assignment]
        region = uncolored[0]

        for color_name in COLOR_LIST:
            logs.append(f"Trying {region}={color_name}")
            if is_valid(region, color_name, assignment):
                assignment[region] = color_name
                logs.append(f"Placed {region}={color_name}")
                result = backtrack(assignment)
                if result is not None:
                    return result
                logs.append(f"Backtracking from {region}={color_name}")
                del assignment[region]
            else:
                logs.append(f"Conflict: {region} cannot be {color_name}")

        return None

    return backtrack({}), logs

def render_svg(country_name: str):
    data = COUNTRIES[country_name]
    svg_parts = []

    for region, (path_data, tx, ty) in data["svg"].items():
        fill_color = COLORS[st.session_state.region_colors.get(region, "None")]
        svg_parts.append(
            f"""
            <path d="{path_data}" fill="{fill_color}" stroke="#ffffff" stroke-width="3"></path>
            <text x="{tx}" y="{ty}" fill="white" font-size="14" font-weight="700"
                  text-anchor="middle" dominant-baseline="middle">{region}</text>
            """
        )

    return f"""
    <html>
      <body style="margin:0; background:#F8FAFC;">
        <div style="display:flex; justify-content:center; align-items:center; padding:10px;">
          <svg viewBox="{data['viewbox']}" width="100%" style="max-width:520px; height:auto;">
            <rect x="0" y="0" width="100%" height="100%" fill="#F8FAFC" rx="16"></rect>
            {''.join(svg_parts)}
          </svg>
        </div>
      </body>
    </html>
    """

# =========================================================
# CSS
# =========================================================
st.markdown(
    """
    <style>
    .stButton > button {
    width: 100%;
    min-height: 46px;
    border-radius: 12px;
    border: none;
    font-size: 15px;
    font-weight: 700;
    color: white;
    margin-top: 4px;
    
    background-color: #3d4154;   /* ✅ GREEN COLOR */
}
# .stButton > button:active {
#     background-color:#0b228f !important;  /* click color */
# }
    html, body, [data-testid="stAppViewContainer"] {
        background: #F3F6FB;
    }
    .block-container {
        max-width: 1450px;
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    .title-main {
        font-size: 2.8rem;
        font-weight: 800;
        color: #1F2937;
        margin-bottom: 1rem;
    }
    .panel {
        background: white;
        border: 1px solid #E5E7EB;
        border-radius: 18px;
        padding: 18px;
        box-shadow: 0 10px 24px rgba(15, 23, 42, 0.05);
        height: 100%;
    }
    .panel-title {
        font-size: 1.35rem;
        font-weight: 800;
        color: #111827;
        margin-bottom: 12px;
    }
    .status-box {
        background: #DCFCE7;
        color: #166534;
        border-left: 6px solid #16A34A;
        padding: 14px;
        border-radius: 12px;
        font-weight: 600;
        margin-bottom: 12px;
    }
    .tip-box {
        background: #FEF3C7;
        color: #92400E;
        border-left: 6px solid #D97706;
        padding: 14px;
        border-radius: 12px;
        font-weight: 600;
        margin-bottom: 12px;
    }
    .error-box {
        background: #FEE2E2;
        color: #991B1B;
        border-left: 6px solid #DC2626;
        padding: 14px;
        border-radius: 12px;
        font-weight: 600;
        margin-bottom: 12px;
    }
    div[data-baseweb="select"] > div {
        min-height: 46px !important;
        border-radius: 12px !important;
    }
    .stButton > button {
        width: 100%;
        min-height: 46px;
        border-radius: 12px;
        border: none;
        font-size: 15px;
        font-weight: 700;
        color: white;
        margin-top: 4px;
    }
    .history-box textarea {
        background: #FFFFFF !important;
        color: #000000 !important;
        border-radius: 12px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# HEADER
# =========================================================
st.markdown('<div class="title-main">🌍 Map Coloring AI Visualizer</div>', unsafe_allow_html=True)

# =========================================================
# LAYOUT
# =========================================================
left, center, right = st.columns([1.05, 1.15, 1.1], gap="large")

with left:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Controls</div>', unsafe_allow_html=True)

    country = st.selectbox("Country", list(COUNTRIES.keys()), index=list(COUNTRIES.keys()).index(st.session_state.selected_country))
    if country != st.session_state.selected_country:
        reset_country(country)
        st.rerun()

    region = st.selectbox("Region", COUNTRIES[country]["regions"])
    color = st.selectbox("Color", COLOR_LIST)

    c1, c2, c3 = st.columns(3)
    with c1:
        apply_btn = st.button("Apply Color", use_container_width=True)
    with c2:
        solve_btn = st.button("Solve Automatically", use_container_width=True)
    with c3:
        reset_btn = st.button("Reset", use_container_width=True)

    if apply_btn:
        bad_neighbor = conflict_neighbor(country, region, color)
        if bad_neighbor is None:
            st.session_state.region_colors[region] = color
            st.session_state.history.append(f"{region}={color}")
            st.session_state.status_msg = f"{region} was colored {color} successfully."
            st.session_state.tip_msg = "Good move. Continue coloring the remaining regions."
        else:
            suggestions = safe_color_suggestions(country, region)
            suggestion_text = ", ".join(suggestions) if suggestions else "No safe colors"
            st.session_state.history.append(f"Conflict: {region} vs {bad_neighbor}")
            st.session_state.status_msg = f"Conflict: {region} cannot use {color} because {bad_neighbor} already uses it."
            st.session_state.tip_msg = f"Try a different color. Suggested safe colors: {suggestion_text}"

    if solve_btn:
        solution, logs = solve_backtracking(country)
        if solution:
            st.session_state.region_colors = solution
            st.session_state.history.extend(logs)
            st.session_state.status_msg = "Solved successfully."
            st.session_state.tip_msg = "Backtracking completed. Review the algorithm history."
        else:
            st.session_state.history.extend(logs)
            st.session_state.status_msg = "No valid coloring found."
            st.session_state.tip_msg = "Try a different map or different color set."

    if reset_btn:
        reset_country(country)
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

with center:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Map</div>', unsafe_allow_html=True)
    components.html(render_svg(country), height=470, scrolling=False)
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Status</div>', unsafe_allow_html=True)

    if st.session_state.status_msg.lower().startswith("conflict"):
        st.markdown(f'<div class="error-box">{st.session_state.status_msg}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="status-box">{st.session_state.status_msg}</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="tip-box">{st.session_state.tip_msg}</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel-title" style="margin-top:12px;">Algorithm History</div>', unsafe_allow_html=True)
    st.markdown('<div class="history-box">', unsafe_allow_html=True)
    st.text_area("", "\n".join(st.session_state.history), height=320)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
