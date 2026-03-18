import streamlit as st

st.set_page_config(page_title="Map Coloring AI", layout="wide")

# ---------------------------
# COLORS (5 PROFESSIONAL COLORS)
# ---------------------------
COLORS = {
    "Red": "#EF4444",
    "Green": "#22C55E",
    "Blue": "#3B82F6",
    "Yellow": "#F59E0B",
    "Purple": "#8B5CF6",
    "None": "#D1D5DB"
}

COLOR_LIST = ["Red","Green","Blue","Yellow","Purple"]

# ---------------------------
# 10 COUNTRIES (ALL SAME STRUCTURE FOR SIMPLICITY)
# ---------------------------
def get_map(name):
    return {
        "regions": ["Region1","Region2","Region3","Region4","Region5"],
        "neighbors": {
            "Region1": ["Region2","Region3"],
            "Region2": ["Region1","Region4"],
            "Region3": ["Region1","Region5"],
            "Region4": ["Region2","Region5"],
            "Region5": ["Region3","Region4"]
        },
        "svg": {
            "Region1": ("M 40 200 L 140 100 L 240 120 L 200 220 L 100 250 Z", 150, 180),
            "Region2": ("M 240 120 L 340 100 L 420 160 L 360 260 L 200 220 Z", 310, 180),
            "Region3": ("M 100 250 L 200 220 L 180 350 L 120 390 L 60 320 Z", 140, 310),
            "Region4": ("M 200 220 L 360 260 L 300 380 L 180 350 Z", 260, 300),
            "Region5": ("M 360 260 L 420 160 L 460 300 L 300 380 Z", 390, 290),
        }
    }

COUNTRIES = {
    "Pakistan": get_map("Pakistan"),
    "India": get_map("India"),
    "USA": get_map("USA"),
    "China": get_map("China"),
    "Brazil": get_map("Brazil"),
    "Canada": get_map("Canada"),
    "Germany": get_map("Germany"),
    "France": get_map("France"),
    "Australia": get_map("Australia"),
    "Japan": get_map("Japan"),
}

# ---------------------------
# SESSION STATE
# ---------------------------
if "country" not in st.session_state:
    st.session_state.country = "Pakistan"

if "colors" not in st.session_state:
    st.session_state.colors = {}

if "history" not in st.session_state:
    st.session_state.history = []

if "status" not in st.session_state:
    st.session_state.status = "Ready"

def reset():
    regions = COUNTRIES[st.session_state.country]["regions"]
    st.session_state.colors = {r: "None" for r in regions}
    st.session_state.history = []
    st.session_state.status = "Reset Done"

reset()

# ---------------------------
# FUNCTIONS
# ---------------------------
def conflict(region, color):
    neighbors = COUNTRIES[st.session_state.country]["neighbors"][region]
    for n in neighbors:
        if st.session_state.colors[n] == color:
            return n
    return None

def solve():
    regions = COUNTRIES[st.session_state.country]["regions"]
    neighbors = COUNTRIES[st.session_state.country]["neighbors"]
    history = []

    def valid(r,c,assign):
        for n in neighbors[r]:
            if assign.get(n) == c:
                return False
        return True

    def backtrack(assign):
        if len(assign)==len(regions):
            return assign

        for r in regions:
            if r not in assign:
                break

        for c in COLOR_LIST:
            history.append(f"Trying {r} = {c}")
            if valid(r,c,assign):
                assign[r]=c
                history.append(f"Placed {r} = {c}")
                res = backtrack(assign)
                if res: return res
                del assign[r]

        return None

    return backtrack({}), history

# ---------------------------
# CSS (PROFESSIONAL BUTTONS)
# ---------------------------
st.markdown("""
<style>
button {
    border-radius:10px !important;
    height:45px !important;
    font-weight:600 !important;
}

/* APPLY */
div.stButton:nth-of-type(1) button {
    background:#2563eb;
    color:white;
}

/* SOLVE */
div.stButton:nth-of-type(2) button {
    background:#16a34a;
    color:white;
}

/* RESET */
div.stButton:nth-of-type(3) button {
    background:#dc2626;
    color:white;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# UI
# ---------------------------
st.title("🌍 Map Coloring AI Visualizer")

col1, col2, col3 = st.columns([1,1.2,1])

# ---------------------------
# CONTROLS
# ---------------------------
with col1:
    st.subheader("Controls")

    country = st.selectbox("Country", list(COUNTRIES.keys()))
    st.session_state.country = country

    regions = COUNTRIES[country]["regions"]

    region = st.selectbox("Region", regions)
    color = st.selectbox("Color", COLOR_LIST)

    if st.button("Apply Color"):
        c = conflict(region, color)
        if c:
            st.session_state.status = f"❌ Conflict with {c}"
            st.session_state.history.append(f"Conflict: {region} vs {c}")
        else:
            st.session_state.colors[region] = color
            st.session_state.status = f"✅ {region} = {color}"
            st.session_state.history.append(f"{region} = {color}")

    if st.button("Solve Automatically"):
        sol, hist = solve()
        if sol:
            st.session_state.colors = sol
            st.session_state.history += hist
            st.session_state.status = "✅ Solved"

    if st.button("Reset"):
        reset()

# ---------------------------
# MAP (WITH REGION NAMES)
# ---------------------------
with col2:
    st.subheader("Map")

    svg = '<svg viewBox="0 0 500 420" width="100%">'

    for r,(path,x,y) in COUNTRIES[country]["svg"].items():
        fill = COLORS[st.session_state.colors.get(r,"None")]

        svg += f'''
        <path d="{path}" fill="{fill}" stroke="white" stroke-width="3"/>
        <text x="{x}" y="{y}" fill="white" font-size="14" text-anchor="middle">{r}</text>
        '''

    svg += "</svg>"

    st.markdown(svg, unsafe_allow_html=True)

# ---------------------------
# STATUS
# ---------------------------
with col3:
    st.subheader("Status")
    st.success(st.session_state.status)

    st.subheader("Algorithm History")
    st.text_area("", "\n".join(st.session_state.history), height=300)
