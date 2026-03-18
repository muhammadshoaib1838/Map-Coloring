import streamlit as st

st.set_page_config(page_title="Map Coloring AI", layout="wide")

# ---------------------------
# COLORS
# ---------------------------
COLORS = {
    "Red": "#EF4444",
    "Green": "#22C55E",
    "Blue": "#3B82F6",
    "Yellow": "#F59E0B",
    "Purple": "#8B5CF6",
    "None": "#D1D5DB"
}

COLOR_LIST = ["Red", "Green", "Blue", "Yellow", "Purple"]

# ---------------------------
# PAKISTAN MAP (5 REGIONS)
# ---------------------------
MAP = {
    "regions": ["Punjab", "Sindh", "Balochistan", "KPK", "Islamabad"],

    "neighbors": {
        "Punjab": ["Sindh", "KPK", "Islamabad", "Balochistan"],
        "Sindh": ["Punjab", "Balochistan"],
        "Balochistan": ["Sindh", "Punjab", "KPK"],
        "KPK": ["Punjab", "Balochistan", "Islamabad"],
        "Islamabad": ["Punjab", "KPK"]
    },

    # FIXED SHAPES (ALL VISIBLE NOW)
    "svg": {
        "Punjab": ("M 250 160 L 360 130 L 420 180 L 380 260 L 300 240 L 240 200 Z", 330, 200),
        "Sindh": ("M 260 240 L 330 260 L 360 350 L 300 400 L 240 350 L 220 280 Z", 300, 320),
        "Balochistan": ("M 40 240 L 150 140 L 250 160 L 240 200 L 180 260 L 80 280 Z", 160, 220),
        "KPK": ("M 200 100 L 300 80 L 360 130 L 250 160 L 150 140 Z", 260, 120),
        "Islamabad": ("M 320 150 L 350 145 L 360 170 L 330 180 Z", 340, 165)
    }
}

# ---------------------------
# SESSION STATE
# ---------------------------
if "colors" not in st.session_state:
    st.session_state.colors = {r: "None" for r in MAP["regions"]}

if "history" not in st.session_state:
    st.session_state.history = []

# ---------------------------
# FUNCTIONS
# ---------------------------
def conflict(region, color):
    for n in MAP["neighbors"][region]:
        if st.session_state.colors[n] == color:
            return n
    return None

def solve():
    regions = MAP["regions"]
    neighbors = MAP["neighbors"]
    history = []

    def valid(r, c, assign):
        for n in neighbors[r]:
            if assign.get(n) == c:
                return False
        return True

    def backtrack(assign):
        if len(assign) == len(regions):
            return assign

        for r in regions:
            if r not in assign:
                break

        for c in COLOR_LIST:
            history.append(f"Trying {r}={c}")
            if valid(r, c, assign):
                assign[r] = c
                res = backtrack(assign)
                if res:
                    return res
                del assign[r]
        return None

    return backtrack({}), history

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

    region = st.selectbox("Region", MAP["regions"])
    color = st.selectbox("Color", COLOR_LIST)

    if st.button("Apply Color"):
        c = conflict(region, color)
        if c:
            st.error(f"Conflict with {c}")
            st.session_state.history.append(f"Conflict: {region} vs {c}")
        else:
            st.session_state.colors[region] = color
            st.session_state.history.append(f"{region} = {color}")

    if st.button("Solve Automatically"):
        sol, hist = solve()
        if sol:
            st.session_state.colors = sol
            st.session_state.history += hist

    if st.button("Reset"):
        st.session_state.colors = {r: "None" for r in MAP["regions"]}
        st.session_state.history = []

# ---------------------------
# MAP (FIXED RENDERING)
# ---------------------------
with col2:
    st.subheader("Map")

    svg = '<svg viewBox="0 0 470 420" width="100%">'

    for r, (path, x, y) in MAP["svg"].items():
        fill = COLORS[st.session_state.colors.get(r, "None")]

        svg += f'''
        <path d="{path}" fill="{fill}" stroke="white" stroke-width="3"/>
        <text x="{x}" y="{y}" fill="white" font-size="14" text-anchor="middle">{r}</text>
        '''

    svg += "</svg>"

    # IMPORTANT FIX (no raw text now)
    st.markdown(svg, unsafe_allow_html=True)

# ---------------------------
# HISTORY
# ---------------------------
with col3:
    st.subheader("Algorithm History")
    st.text_area("", "\n".join(st.session_state.history), height=300)
