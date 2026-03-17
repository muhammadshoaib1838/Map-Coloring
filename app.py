import math
import copy
from typing import Dict, List, Tuple, Optional

import gradio as gr
import matplotlib.pyplot as plt
import networkx as nx

# ============================================================
# MAP DATA
# ============================================================
# Each map contains:
# - nodes: list of region names
# - edges: neighboring regions (constraints)
# - pos: fixed positions for clean visualization
# NOTE: These are teaching/demo CSP maps with representative adjacencies.

MAPS = {
    "Australia": {
        "nodes": ["WA", "NT", "SA", "Q", "NSW", "V", "T"],
        "edges": [
            ("WA", "NT"), ("WA", "SA"),
            ("NT", "SA"), ("NT", "Q"),
            ("SA", "Q"), ("SA", "NSW"), ("SA", "V"),
            ("Q", "NSW"),
            ("NSW", "V"),
        ],
        "pos": {
            "WA": (0.08, 0.55),
            "NT": (0.35, 0.80),
            "SA": (0.35, 0.45),
            "Q": (0.68, 0.78),
            "NSW": (0.73, 0.45),
            "V": (0.56, 0.20),
            "T": (0.73, -0.10),
        },
    },
    "South America": {
        "nodes": ["Colombia", "Venezuela", "Brazil", "Peru", "Bolivia", "Chile", "Argentina", "Paraguay", "Uruguay", "Ecuador"],
        "edges": [
            ("Colombia", "Venezuela"), ("Colombia", "Brazil"), ("Colombia", "Peru"), ("Colombia", "Ecuador"),
            ("Venezuela", "Brazil"),
            ("Ecuador", "Peru"),
            ("Peru", "Brazil"), ("Peru", "Bolivia"), ("Peru", "Chile"),
            ("Brazil", "Bolivia"), ("Brazil", "Paraguay"), ("Brazil", "Argentina"), ("Brazil", "Uruguay"),
            ("Bolivia", "Chile"), ("Bolivia", "Argentina"), ("Bolivia", "Paraguay"),
            ("Chile", "Argentina"),
            ("Argentina", "Paraguay"), ("Argentina", "Uruguay"),
            ("Paraguay", "Brazil"), ("Paraguay", "Argentina"),
        ],
        "pos": {
            "Colombia": (0.18, 0.92),
            "Venezuela": (0.55, 0.95),
            "Ecuador": (0.10, 0.72),
            "Peru": (0.22, 0.55),
            "Brazil": (0.62, 0.60),
            "Bolivia": (0.38, 0.36),
            "Chile": (0.12, 0.14),
            "Paraguay": (0.56, 0.28),
            "Argentina": (0.36, 0.02),
            "Uruguay": (0.72, 0.10),
        },
    },
    "Europe (sample)": {
        "nodes": ["Portugal", "Spain", "France", "Belgium", "Germany", "Italy", "Switzerland", "Austria", "Poland", "Netherlands"],
        "edges": [
            ("Portugal", "Spain"),
            ("Spain", "France"),
            ("France", "Belgium"), ("France", "Germany"), ("France", "Italy"), ("France", "Switzerland"),
            ("Belgium", "Netherlands"), ("Belgium", "Germany"),
            ("Netherlands", "Germany"),
            ("Germany", "Switzerland"), ("Germany", "Austria"), ("Germany", "Poland"),
            ("Switzerland", "Italy"), ("Switzerland", "Austria"),
            ("Italy", "Austria"),
            ("Austria", "Poland"),
        ],
        "pos": {
            "Portugal": (0.02, 0.42),
            "Spain": (0.18, 0.40),
            "France": (0.38, 0.52),
            "Belgium": (0.50, 0.68),
            "Netherlands": (0.56, 0.82),
            "Germany": (0.66, 0.66),
            "Switzerland": (0.57, 0.38),
            "Italy": (0.70, 0.18),
            "Austria": (0.79, 0.44),
            "Poland": (0.92, 0.64),
        },
    },
    "India (sample states)": {
        "nodes": ["Punjab", "Rajasthan", "Gujarat", "Madhya Pradesh", "Uttar Pradesh", "Maharashtra", "Bihar", "West Bengal"],
        "edges": [
            ("Punjab", "Rajasthan"), ("Punjab", "Uttar Pradesh"),
            ("Rajasthan", "Gujarat"), ("Rajasthan", "Madhya Pradesh"), ("Rajasthan", "Uttar Pradesh"),
            ("Gujarat", "Maharashtra"), ("Gujarat", "Madhya Pradesh"),
            ("Madhya Pradesh", "Uttar Pradesh"), ("Madhya Pradesh", "Maharashtra"),
            ("Uttar Pradesh", "Bihar"),
            ("Bihar", "West Bengal"),
        ],
        "pos": {
            "Punjab": (0.18, 0.88),
            "Rajasthan": (0.20, 0.62),
            "Uttar Pradesh": (0.55, 0.72),
            "Gujarat": (0.08, 0.28),
            "Madhya Pradesh": (0.42, 0.46),
            "Maharashtra": (0.33, 0.16),
            "Bihar": (0.78, 0.62),
            "West Bengal": (0.95, 0.48),
        },
    },
    "USA (sample states)": {
        "nodes": ["California", "Oregon", "Nevada", "Arizona", "Utah", "Idaho", "Washington", "Colorado"],
        "edges": [
            ("Washington", "Oregon"), ("Washington", "Idaho"),
            ("Oregon", "California"), ("Oregon", "Nevada"), ("Oregon", "Idaho"),
            ("California", "Nevada"), ("California", "Arizona"),
            ("Nevada", "Idaho"), ("Nevada", "Utah"), ("Nevada", "Arizona"),
            ("Idaho", "Utah"),
            ("Utah", "Arizona"), ("Utah", "Colorado"),
            ("Arizona", "Colorado"),
        ],
        "pos": {
            "Washington": (0.10, 0.95),
            "Oregon": (0.12, 0.72),
            "California": (0.08, 0.32),
            "Idaho": (0.42, 0.78),
            "Nevada": (0.33, 0.45),
            "Utah": (0.58, 0.46),
            "Arizona": (0.42, 0.16),
            "Colorado": (0.82, 0.35),
        },
    },
}

COLOR_HEX = {
    "Red": "#ef4444",
    "Green": "#22c55e",
    "Blue": "#3b82f6",
    "Yellow": "#f59e0b",
    "Purple": "#8b5cf6",
    "Orange": "#f97316",
}

DEFAULT_COLOR_SETS = {
    3: ["Red", "Green", "Blue"],
    4: ["Red", "Green", "Blue", "Yellow"],
    5: ["Red", "Green", "Blue", "Yellow", "Purple"],
}


# ============================================================
# CSP SOLVER UTILITIES
# ============================================================
def neighbors_of(map_name: str) -> Dict[str, List[str]]:
    data = MAPS[map_name]
    neighbors = {node: [] for node in data["nodes"]}
    for a, b in data["edges"]:
        neighbors[a].append(b)
        neighbors[b].append(a)
    return neighbors


def is_consistent(region: str, color: str, assignment: Dict[str, str], neighbors: Dict[str, List[str]]) -> bool:
    for nb in neighbors[region]:
        if assignment.get(nb) == color:
            return False
    return True


def select_unassigned_region(nodes: List[str], assignment: Dict[str, str], neighbors: Dict[str, List[str]]) -> str:
    # MRV-like simple heuristic: choose unassigned node with highest degree
    unassigned = [n for n in nodes if n not in assignment]
    unassigned.sort(key=lambda n: (-len(neighbors[n]), n))
    return unassigned[0]


def solve_with_steps(map_name: str, colors: List[str]) -> List[Dict]:
    data = MAPS[map_name]
    nodes = data["nodes"]
    neighbors = neighbors_of(map_name)
    assignment: Dict[str, str] = {}
    steps: List[Dict] = []

    def add_step(action: str, region: Optional[str] = None, color: Optional[str] = None, message: str = ""):
        steps.append(
            {
                "assignment": copy.deepcopy(assignment),
                "action": action,
                "region": region,
                "color": color,
                "message": message,
            }
        )

    add_step("start", message=f"Starting CSP map coloring for {map_name} using {len(colors)} colors.")

    def backtrack() -> bool:
        if len(assignment) == len(nodes):
            add_step("solved", message="Success! All regions are colored without conflicts.")
            return True

        region = select_unassigned_region(nodes, assignment, neighbors)

        for color in colors:
            add_step("try", region, color, f"Trying {color} for {region}.")
            if is_consistent(region, color, assignment, neighbors):
                assignment[region] = color
                add_step("place", region, color, f"Placed {color} on {region}.")
                if backtrack():
                    return True
                del assignment[region]
                add_step("remove", region, color, f"Backtracking: removed {color} from {region}.")
            else:
                add_step("conflict", region, color, f"Conflict: {region} cannot be {color} because a neighbor already has that color.")

        return False

    solved = backtrack()
    if not solved:
        add_step("failed", message="No valid coloring found with the selected number of colors.")

    return steps


# ============================================================
# RENDERING
# ============================================================
def render_graph(map_name: str, assignment: Dict[str, str], highlight_region: Optional[str] = None, action: str = ""):
    data = MAPS[map_name]
    graph = nx.Graph()
    graph.add_nodes_from(data["nodes"])
    graph.add_edges_from(data["edges"])
    pos = data["pos"]

    node_colors = []
    node_edgecolors = []
    node_sizes = []

    for node in data["nodes"]:
        color_name = assignment.get(node)
        fill = COLOR_HEX.get(color_name, "#e5e7eb")
        node_colors.append(fill)

        if node == highlight_region:
            if action in {"place", "manual_place"}:
                node_edgecolors.append("#22c55e")
            elif action in {"conflict", "manual_conflict"}:
                node_edgecolors.append("#ef4444")
            elif action in {"remove", "manual_remove", "try"}:
                node_edgecolors.append("#f59e0b")
            else:
                node_edgecolors.append("#111827")
            node_sizes.append(2300)
        else:
            node_edgecolors.append("#111827")
            node_sizes.append(1900)

    fig, ax = plt.subplots(figsize=(7.2, 5.6), dpi=120)
    fig.patch.set_facecolor("#0b1020")
    ax.set_facecolor("#0b1020")

    nx.draw_networkx_edges(graph, pos, ax=ax, width=2.0, edge_color="#94a3b8")
    nx.draw_networkx_nodes(
        graph,
        pos,
        ax=ax,
        node_color=node_colors,
        node_size=node_sizes,
        edgecolors=node_edgecolors,
        linewidths=3,
    )
    nx.draw_networkx_labels(graph, pos, ax=ax, font_size=10, font_weight="bold", font_color="#111827")

    ax.set_title(f"{map_name} Map Coloring", color="white", fontsize=15, fontweight="bold", pad=14)
    ax.axis("off")
    plt.tight_layout()
    return fig


def build_status_html(step_index: int, total_steps: int, message: str, action: str):
    badge_color = {
        "start": "#8b5cf6",
        "try": "#06b6d4",
        "place": "#22c55e",
        "remove": "#f97316",
        "conflict": "#ef4444",
        "solved": "#a855f7",
        "failed": "#111827",
        "manual_place": "#22c55e",
        "manual_remove": "#f97316",
        "manual_conflict": "#ef4444",
        "manual_start": "#8b5cf6",
    }.get(action, "#8b5cf6")

    return f"""
    <div class="status-card">
        <div class="pill" style="background:{badge_color};">{action.upper()}</div>
        <div class="step-title">Step {step_index} of {total_steps}</div>
        <div class="step-message">{message}</div>
    </div>
    """


def build_history_text(steps: List[Dict], current_index: int) -> str:
    if not steps:
        return ""
    return "\n".join(
        f"{i+1}. [{steps[i]['action'].upper()}] {steps[i]['message']}"
        for i in range(current_index + 1)
    )


def get_step_view(map_name: str, steps: List[Dict], index: int):
    if not steps:
        fig = render_graph(map_name, {})
        status = build_status_html(0, 0, "Click 'Generate CSP Steps' to begin.", "manual_start")
        return fig, status, "", "0 / 0"

    index = max(0, min(index, len(steps) - 1))
    step = steps[index]
    fig = render_graph(map_name, step["assignment"], step.get("region"), step.get("action", ""))
    status = build_status_html(index + 1, len(steps), step["message"], step["action"])
    history = build_history_text(steps, index)
    counter = f"{index + 1} / {len(steps)}"
    return fig, status, history, counter


# ============================================================
# MANUAL MODE
# ============================================================
def initial_manual_assignment(map_name: str):
    return {node: None for node in MAPS[map_name]["nodes"]}


def normalize_manual_assignment(assignment: Dict[str, Optional[str]], map_name: str):
    base = {node: None for node in MAPS[map_name]["nodes"]}
    if isinstance(assignment, dict):
        for key, value in assignment.items():
            if key in base:
                base[key] = value
    return base


def assignment_without_none(assignment: Dict[str, Optional[str]]) -> Dict[str, str]:
    return {k: v for k, v in assignment.items() if v is not None}


def manual_color_region(map_name: str, assignment: Dict[str, Optional[str]], history_text: str, region: str, color: str):
    assignment = normalize_manual_assignment(assignment, map_name)
    neighbors = neighbors_of(map_name)
    history = history_text.split("\n") if history_text.strip() else []

    if color == "Remove Color":
        assignment[region] = None
        message = f"Removed color from {region}."
        action = "manual_remove"
        history.append(message)
        fig = render_graph(map_name, assignment_without_none(assignment), region, action)
        status = build_status_html(len(history), len(MAPS[map_name]["nodes"]), message, action)
        return assignment, fig, status, "\n".join(history), f"{sum(v is not None for v in assignment.values())} / {len(MAPS[map_name]['nodes'])} regions colored"

    for nb in neighbors[region]:
        if assignment.get(nb) == color:
            message = f"Conflict: {region} cannot be {color} because neighboring region {nb} already has {color}."
            action = "manual_conflict"
            history.append(message)
            fig = render_graph(map_name, assignment_without_none(assignment), region, action)
            status = build_status_html(len(history), len(MAPS[map_name]["nodes"]), message, action)
            return assignment, fig, status, "\n".join(history), f"{sum(v is not None for v in assignment.values())} / {len(MAPS[map_name]['nodes'])} regions colored"

    assignment[region] = color
    colored_count = sum(v is not None for v in assignment.values())
    if colored_count == len(MAPS[map_name]["nodes"]):
        message = f"Correct! {region} is colored {color}. All regions are now colored without conflicts."
    else:
        message = f"Correct! {region} is colored {color}."
    action = "manual_place"
    history.append(message)
    fig = render_graph(map_name, assignment_without_none(assignment), region, action)
    status = build_status_html(len(history), len(MAPS[map_name]["nodes"]), message, action)
    return assignment, fig, status, "\n".join(history), f"{colored_count} / {len(MAPS[map_name]['nodes'])} regions colored"


# ============================================================
# UI HELPERS
# ============================================================
def map_info_text(map_name: str) -> str:
    data = MAPS[map_name]
    return (
        f"**Map:** {map_name}  \n"
        f"**Regions:** {len(data['nodes'])}  \n"
        f"**Constraints (neighbor pairs):** {len(data['edges'])}"
    )


def available_regions(map_name: str):
    return gr.update(choices=MAPS[map_name]["nodes"], value=MAPS[map_name]["nodes"][0])


def available_colors(num_colors: int):
    colors = DEFAULT_COLOR_SETS[int(num_colors)] + ["Remove Color"]
    return gr.update(choices=colors, value=colors[0])


def initialize_map(map_name: str, num_colors: int):
    fig = render_graph(map_name, {})
    status = build_status_html(0, 0, f"Ready. Choose manual coloring or generate CSP steps for {map_name}.", "manual_start")
    region_update = available_regions(map_name)
    colors = DEFAULT_COLOR_SETS[int(num_colors)] + ["Remove Color"]
    color_update = gr.update(choices=colors, value=colors[0])
    manual_assignment = initial_manual_assignment(map_name)
    return (
        fig,
        status,
        "",
        "0 / 0",
        map_info_text(map_name),
        region_update,
        color_update,
        [],
        0,
        manual_assignment,
        "",
        f"0 / {len(MAPS[map_name]['nodes'])} regions colored",
    )


# ============================================================
# AUTO MODE BUTTONS
# ============================================================
def generate_demo(map_name: str, num_colors: int):
    colors = DEFAULT_COLOR_SETS[int(num_colors)]
    steps = solve_with_steps(map_name, colors)
    fig, status, history, counter = get_step_view(map_name, steps, 0)
    return steps, 0, fig, status, history, counter


def next_step(map_name: str, steps: List[Dict], index: int):
    fig, status, history, counter = get_step_view(map_name, steps, index + 1)
    return steps, min(index + 1, max(len(steps) - 1, 0)), fig, status, history, counter


def prev_step(map_name: str, steps: List[Dict], index: int):
    fig, status, history, counter = get_step_view(map_name, steps, index - 1)
    return steps, max(index - 1, 0), fig, status, history, counter


def final_step(map_name: str, steps: List[Dict], index: int):
    last_index = len(steps) - 1 if steps else 0
    fig, status, history, counter = get_step_view(map_name, steps, last_index)
    return steps, last_index, fig, status, history, counter


def reset_auto(map_name: str):
    fig, status, history, counter = get_step_view(map_name, [], 0)
    return [], 0, fig, status, history, counter


# ============================================================
# CSS
# ============================================================
CUSTOM_CSS = """
:root{
  --bg1:#0f1020;
  --bg2:#1a1d38;
  --bg3:#05060f;
  --text:#f8f9ff;
}

body, .gradio-container {
  background: radial-gradient(circle at top left, #1d1f47 0%, #0b0c19 40%, #05060f 100%) !important;
  color: var(--text) !important;
  font-family: Inter, ui-sans-serif, system-ui, sans-serif;
}

.hero{
  padding: 20px 24px;
  border-radius: 24px;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.12);
  backdrop-filter: blur(14px);
  box-shadow: 0 12px 40px rgba(0,0,0,0.25);
  margin-bottom: 18px;
}

.main-title{
  font-size: 2.3rem;
  font-weight: 800;
  line-height: 1.1;
  background: linear-gradient(90deg, #8b5cf6, #06b6d4, #ec4899);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 10px;
}

.sub-title{
  color: #d7dcff;
  font-size: 1rem;
}

button {
  border-radius: 18px !important;
  font-weight: 700 !important;
  padding: 12px !important;
  border: none !important;
  transition: all 0.3s ease !important;
}

button:hover {
  transform: translateY(-2px) scale(1.02);
  box-shadow: 0 8px 25px rgba(0,0,0,0.35);
}

.gr-button-primary {
  background: linear-gradient(135deg, #ff7a18, #ff3d77) !important;
  color: white !important;
}

.status-card{
  padding: 18px;
  border-radius: 20px;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.16);
  box-shadow: 0 8px 28px rgba(0,0,0,0.22);
  color: white;
}

.pill{
  display:inline-block;
  padding: 6px 12px;
  border-radius: 999px;
  font-weight: 700;
  font-size: 0.85rem;
  margin-bottom: 10px;
}

.step-title{
  font-size: 1.1rem;
  font-weight: 800;
  margin-bottom: 6px;
}

.step-message{
  color: #eef2ff;
  font-size: 1rem;
  line-height: 1.5;
}

textarea {
  color: black !important;
  background: #ffffff !important;
}

label {
  color: white !important;
}
"""


# ============================================================
# APP
# ============================================================
with gr.Blocks(css=CUSTOM_CSS) as demo:
    gr.HTML(
        """
        <div class="hero">
            <div class="main-title">CSP Map Coloring Solver</div>
            <div class="sub-title">
                Select a world map sample, solve it with constraint satisfaction, or color it manually and learn CSP step by step.
            </div>
        </div>
        """
    )

    steps_state = gr.State([])
    index_state = gr.State(0)
    manual_assignment_state = gr.State(initial_manual_assignment("Australia"))
    manual_history_state = gr.State("")

    with gr.Row():
        map_dropdown = gr.Dropdown(choices=list(MAPS.keys()), value="Australia", label="Choose Map")
        color_count = gr.Dropdown(choices=[3, 4, 5], value=3, label="Number of Colors")
        map_info = gr.Markdown(map_info_text("Australia"))

    with gr.Tabs():
        with gr.Tab("🤖 Auto CSP Solver"):
            with gr.Row():
                with gr.Column(scale=1):
                    generate_btn = gr.Button("Generate CSP Steps", variant="primary")
                    prev_btn = gr.Button("⬅ Previous Step")
                    next_btn = gr.Button("Next Step ➡")
                    final_btn = gr.Button("Show Final Solution")
                    reset_btn = gr.Button("Reset Auto Solver")
                    step_counter = gr.Markdown("0 / 0")

                with gr.Column(scale=2):
                    graph_output = gr.Plot(render_graph("Australia", {}))

                with gr.Column(scale=2):
                    status_output = gr.HTML(
                        build_status_html(0, 0, "Ready. Click 'Generate CSP Steps' to begin.", "manual_start")
                    )
                    history_output = gr.Textbox(label="Algorithm History", lines=18, interactive=False)

        with gr.Tab("🎮 Manual Coloring"):
            with gr.Row():
                with gr.Column(scale=1):
                    region_dropdown = gr.Dropdown(choices=MAPS["Australia"]["nodes"], value=MAPS["Australia"]["nodes"][0], label="Select Region")
                    color_dropdown = gr.Dropdown(choices=DEFAULT_COLOR_SETS[3] + ["Remove Color"], value="Red", label="Choose Color")
                    apply_btn = gr.Button("Apply Color", variant="primary")
                    reset_manual_btn = gr.Button("Reset Manual Mode")
                    manual_counter = gr.Markdown(f"0 / {len(MAPS['Australia']['nodes'])} regions colored")

                with gr.Column(scale=2):
                    manual_graph_output = gr.Plot(render_graph("Australia", {}))

                with gr.Column(scale=2):
                    manual_status_output = gr.HTML(
                        build_status_html(0, 0, "Choose a region and a color, then click Apply Color.", "manual_start")
                    )
                    manual_history_output = gr.Textbox(label="Manual Coloring History", lines=18, interactive=False)

    # Map and color count changes
    map_dropdown.change(
        initialize_map,
        inputs=[map_dropdown, color_count],
        outputs=[
            graph_output,
            status_output,
            history_output,
            step_counter,
            map_info,
            region_dropdown,
            color_dropdown,
            steps_state,
            index_state,
            manual_assignment_state,
            manual_history_state,
            manual_counter,
        ],
    )

    color_count.change(
        initialize_map,
        inputs=[map_dropdown, color_count],
        outputs=[
            graph_output,
            status_output,
            history_output,
            step_counter,
            map_info,
            region_dropdown,
            color_dropdown,
            steps_state,
            index_state,
            manual_assignment_state,
            manual_history_state,
            manual_counter,
        ],
    )

    # Auto mode
    generate_btn.click(
        generate_demo,
        inputs=[map_dropdown, color_count],
        outputs=[steps_state, index_state, graph_output, status_output, history_output, step_counter],
    )
    prev_btn.click(
        prev_step,
        inputs=[map_dropdown, steps_state, index_state],
        outputs=[steps_state, index_state, graph_output, status_output, history_output, step_counter],
    )
    next_btn.click(
        next_step,
        inputs=[map_dropdown, steps_state, index_state],
        outputs=[steps_state, index_state, graph_output, status_output, history_output, step_counter],
    )
    final_btn.click(
        final_step,
        inputs=[map_dropdown, steps_state, index_state],
        outputs=[steps_state, index_state, graph_output, status_output, history_output, step_counter],
    )
    reset_btn.click(
        reset_auto,
        inputs=[map_dropdown],
        outputs=[steps_state, index_state, graph_output, status_output, history_output, step_counter],
    )

    # Manual mode
    apply_btn.click(
        manual_color_region,
        inputs=[map_dropdown, manual_assignment_state, manual_history_state, region_dropdown, color_dropdown],
        outputs=[manual_assignment_state, manual_graph_output, manual_status_output, manual_history_output, manual_counter],
    ).then(
        lambda text: text,
        inputs=[manual_history_output],
        outputs=[manual_history_state],
    )

    reset_manual_btn.click(
        lambda map_name: (
            initial_manual_assignment(map_name),
            render_graph(map_name, {}),
            build_status_html(0, 0, "Manual mode reset. Choose a region and a color.", "manual_start"),
            "",
            f"0 / {len(MAPS[map_name]['nodes'])} regions colored",
            "",
        ),
        inputs=[map_dropdown],
        outputs=[
            manual_assignment_state,
            manual_graph_output,
            manual_status_output,
            manual_history_output,
            manual_counter,
            manual_history_state,
        ],
    )

if __name__ == "__main__":
    demo.launch()
