import streamlit as st

st.set_page_config(page_title="Map Coloring AI", layout="wide")

# ---------------------------
# COLORS
# ---------------------------
COLORS = {
    "Red": "#EF4444",
    "Green": "#22C55E",
    "Blue": "#3B82F6",
    "None": "#D1D5DB"
}

# ---------------------------
# MAP DATA (Pakistan)
# ---------------------------
MAP = {
    "regions": ["Balochistan", "Sindh", "Punjab", "KPK", "Islamabad"],
    "neighbors": {
        "Balochistan": ["Sindh", "Punjab", "KPK"],
        "Sindh": ["Balochistan", "Punjab"],
        "Punjab": ["Balochistan", "Sindh", "KPK", "Islamabad"],
        "KPK": ["Balochistan", "Punjab", "Islamabad"],
        "Islamabad": ["Punjab", "KPK"]
    },
    "svg": {
        "Balochistan": "M 40 220 L 120 120 L 210 110 L 250 165 L 220 245 L 135 280 L 60 265 Z",
        "Sindh": "M 220 245 L 270 225 L 315 250 L 330 330 L 280 370 L 220 330 L 205 280 Z",
        "Punjab": "M 250 165 L 340 130 L 410 155 L 420 230 L 360 270 L 315 250 L 270 225 L 220 245 Z",
        "KPK": "M 235 95 L 305 70 L 350 95 L 340 130 L 250 165 L 210 110 Z",
        "Islamabad": "M 355 145 L 375 138 L 388 152 L 380 168 L 360 170 L 350 156 Z"
    }
}

# ---------------------------
# SESSION STATE
# ---------------------------
if "colors" not in st.session_state:
    st.session_state.colors = {r: "None" for r in MAP["regions"]}

if "history" not in st.session_state:
    st.session_state.history = []

if "status" not in st.session_state:
    st.session_state.status = "Ready"

# ---------------------------
# FUNCTIONS
# ---------------------------
def conflict(region, color):
    for n in MAP["neighbors"][region]:
        if st.session_state.colors[n] == color:
            return n
    return None

def solve():
    history = []

    def valid(region, color, assign):
        for n in MAP["neighbors"][region]:
            if assign.get(n) == color:
                return False
        return True

    def backtrack(assign):
        if len(assign) == len(MAP["regions"]):
            return assign

        for r in MAP["regions"]:
            if r not in assign:
                region = r
                break

        for c in ["Red", "Green", "Blue"]:
            history.append(f"Trying {region} = {c}")
            if valid(region, c, assign):
                assign[region] = c
                history.append(f"Placed {region} = {c}")
                result = backtrack(assign)
                if result:
                    return result
                history.append(f"Backtrack {region}")
                del assign[region]

        return None

    sol = backtrack({})
    return sol, history

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
    color = st.selectbox("Color", ["Red","Green","Blue"])

    if st.button("Apply Color"):
        c = conflict(region, color)

        if c:
            st.session_state.status = f"❌ Conflict with {c}"
            st.session_state.history.append(f"Conflict: {region} vs {c}")
        else:
            st.session_state.colors[region] = color
            st.session_state.status = f"✅ {region} colored {color}"
            st.session_state.history.append(f"{region} = {color}")

    if st.button("Solve Automatically"):
        sol, hist = solve()
        if sol:
            st.session_state.colors = sol
            st.session_state.history += hist
            st.session_state.status = "✅ Solved"

    if st.button("Reset"):
        st.session_state.colors = {r: "None" for r in MAP["regions"]}
        st.session_state.history = []
        st.session_state.status = "Reset Done"

# ---------------------------
# MAP
# ---------------------------
with col2:
    st.subheader("Map")

    svg = '<svg viewBox="0 0 470 420" width="100%">'

    for r, path in MAP["svg"].items():
        fill = COLORS[st.session_state.colors[r]]
        svg += f'<path d="{path}" fill="{fill}" stroke="white" stroke-width="3"/>'

    svg += "</svg>"

    st.markdown(svg, unsafe_allow_html=True)

# ---------------------------
# STATUS + HISTORY
# ---------------------------
with col3:
    st.subheader("Status")
    st.success(st.session_state.status)

    st.subheader("Algorithm History")
    st.text_area("", "\n".join(st.session_state.history), height=300)
