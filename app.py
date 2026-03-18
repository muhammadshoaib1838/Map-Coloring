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

COLOR_LIST = ["Red","Green","Blue","Yellow","Purple"]

# ---------------------------
# REAL COUNTRY MAPS (5 REGIONS EACH)
# ---------------------------
COUNTRIES = {
    "Pakistan": {
        "regions": ["Punjab","Sindh","Balochistan","KPK","Islamabad"],
        "neighbors": {
            "Punjab":["Sindh","KPK","Islamabad","Balochistan"],
            "Sindh":["Punjab","Balochistan"],
            "Balochistan":["Sindh","Punjab","KPK"],
            "KPK":["Punjab","Balochistan","Islamabad"],
            "Islamabad":["Punjab","KPK"]
        },
        "svg": {
            "Punjab":("M 250 165 L 340 130 L 410 155 L 420 230 L 360 270 L 315 250 L 270 225 L 220 245 Z",320,200),
            "Sindh":("M 220 245 L 270 225 L 315 250 L 330 330 L 280 370 L 220 330 L 205 280 Z",280,300),
            "Balochistan":("M 40 220 L 120 120 L 210 110 L 250 165 L 220 245 L 135 280 L 60 265 Z",150,200),
            "KPK":("M 235 95 L 305 70 L 350 95 L 340 130 L 250 165 L 210 110 Z",290,110),
            "Islamabad":("M 355 145 L 375 138 L 388 152 L 380 168 L 360 170 L 350 156 Z",370,155)
        }
    },

    "India": {
        "regions": ["Punjab","Rajasthan","UP","Gujarat","Delhi"],
        "neighbors": {
            "Punjab":["Rajasthan","Delhi"],
            "Rajasthan":["Punjab","Gujarat","UP"],
            "UP":["Rajasthan","Delhi"],
            "Gujarat":["Rajasthan"],
            "Delhi":["Punjab","UP"]
        },
        "svg": {
            "Punjab":("M 100 100 L 180 90 L 200 140 L 120 160 Z",150,120),
            "Rajasthan":("M 120 160 L 200 140 L 260 200 L 180 240 Z",190,190),
            "UP":("M 200 140 L 280 130 L 300 200 L 260 200 Z",260,160),
            "Gujarat":("M 120 240 L 180 240 L 200 300 L 140 320 Z",170,280),
            "Delhi":("M 240 150 L 260 150 L 255 170 L 240 170 Z",250,160)
        }
    }
}

# ---------------------------
# SESSION
# ---------------------------
if "country" not in st.session_state:
    st.session_state.country = "Pakistan"

if "colors" not in st.session_state:
    st.session_state.colors = {}

if "history" not in st.session_state:
    st.session_state.history = []

def reset():
    regions = COUNTRIES[st.session_state.country]["regions"]
    st.session_state.colors = {r:"None" for r in regions}
    st.session_state.history = []

reset()

# ---------------------------
# FUNCTIONS
# ---------------------------
def conflict(region,color):
    for n in COUNTRIES[st.session_state.country]["neighbors"][region]:
        if st.session_state.colors[n]==color:
            return n
    return None

def solve():
    regions = COUNTRIES[st.session_state.country]["regions"]
    neighbors = COUNTRIES[st.session_state.country]["neighbors"]
    history=[]

    def valid(r,c,assign):
        for n in neighbors[r]:
            if assign.get(n)==c:
                return False
        return True

    def backtrack(assign):
        if len(assign)==len(regions):
            return assign

        for r in regions:
            if r not in assign:
                break

        for c in COLOR_LIST:
            history.append(f"Trying {r}={c}")
            if valid(r,c,assign):
                assign[r]=c
                res=backtrack(assign)
                if res: return res
                del assign[r]
        return None

    return backtrack({}), history

# ---------------------------
# UI
# ---------------------------
st.title("🌍 Map Coloring AI Visualizer")

col1,col2,col3 = st.columns([1,1.2,1])

# CONTROLS
with col1:
    st.subheader("Controls")

    country = st.selectbox("Country", list(COUNTRIES.keys()))
    st.session_state.country = country

    regions = COUNTRIES[country]["regions"]

    region = st.selectbox("Region", regions)
    color = st.selectbox("Color", COLOR_LIST)

    if st.button("Apply Color"):
        c = conflict(region,color)
        if c:
            st.error(f"Conflict with {c}")
            st.session_state.history.append(f"Conflict: {region} vs {c}")
        else:
            st.session_state.colors[region]=color
            st.session_state.history.append(f"{region}={color}")

    if st.button("Solve Automatically"):
        sol,hist = solve()
        if sol:
            st.session_state.colors = sol
            st.session_state.history += hist

    if st.button("Reset"):
        reset()

# MAP (NO RAW CODE NOW)
with col2:
    st.subheader("Map")

    svg = '<svg viewBox="0 0 470 420" width="100%">'

    for r,(path,x,y) in COUNTRIES[country]["svg"].items():
        fill = COLORS[st.session_state.colors.get(r,"None")]

        svg += f'''
        <path d="{path}" fill="{fill}" stroke="white" stroke-width="3"/>
        <text x="{x}" y="{y}" fill="white" font-size="14" text-anchor="middle">{r}</text>
        '''

    svg += "</svg>"

    st.markdown(svg, unsafe_allow_html=True)

# STATUS
with col3:
    st.subheader("Algorithm History")
    st.text_area("", "\n".join(st.session_state.history), height=300)
