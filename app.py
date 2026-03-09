import streamlit as st
import requests
import random
import time
from PIL import Image, ImageDraw
from openai import OpenAI
import re

# ----------------------------
# CONFIG
# ----------------------------

# Ollama's OpenAI-compatible endpoint
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

GRID_SIZE = 8
TILE = 60

AGENT_COUNT = 3
TRAP_COUNT = 6

# ----------------------------
# PIXEL ASSETS
# ----------------------------

def floor():
    img = Image.new("RGB",(TILE,TILE),"#f8edeb")
    return img

def trap():
    img = Image.new("RGB",(TILE,TILE),"#ffcad4")
    d = ImageDraw.Draw(img)
    d.polygon([(10,50),(30,10),(50,50)],fill="#9d0208")
    return img

def treasure():
    img = Image.new("RGB",(TILE,TILE),"#cdb4db")
    d = ImageDraw.Draw(img)
    d.rectangle([18,28,42,44],fill="#ffd166")
    d.rectangle([18,24,42,28],fill="#ffb703")
    return img

def agent(color):
    img = Image.new("RGB",(TILE,TILE),"#bde0fe")
    d = ImageDraw.Draw(img)
    d.rectangle([20,20,40,40],fill=color)
    d.rectangle([26,26,34,34],fill="#ffffff")
    return img

floor_tile = floor()
trap_tile = trap()
treasure_tile = treasure()

agent_colors = ["#023047","#3a86ff","#8338ec"]

agent_tiles = [agent(c) for c in agent_colors]

# ----------------------------
# INIT STATE
# ----------------------------

if "agents" not in st.session_state:

    agents = []

    # Assigning different models for variety
    models = ["gemma3:4b", "gemma3:4b", "llama3.2:latest"]

    for i in range(AGENT_COUNT):

        agents.append({
            "name": f"Agent {i+1}",
            "pos": [random.randint(0, 2), random.randint(0, 2)],
            "color": i,
            "model": models[i],
            "thought": "Starting exploration...",
            "active": True
        })

    traps=[]
    for _ in range(TRAP_COUNT):
        traps.append([random.randint(0,7),random.randint(0,7)])

    st.session_state.agents = agents
    st.session_state.traps = traps
    st.session_state.treasure = [random.randint(5,7),random.randint(5,7)]
    st.session_state.running=False

# ----------------------------
# DRAW GRID
# ----------------------------

def draw_grid():

    img = Image.new("RGB",(GRID_SIZE*TILE,GRID_SIZE*TILE),"#ffffff")

    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):

            tile=floor_tile

            if [x,y]==st.session_state.treasure:
                tile=treasure_tile

            if [x,y] in st.session_state.traps:
                tile=trap_tile

            for a in st.session_state.agents:
                if a["pos"]==[x,y]:
                    tile=agent_tiles[a["color"]]

            img.paste(tile,(x*TILE,y*TILE))

    return img

# ----------------------------
# LLM DECISION
# ----------------------------

# ----------------------------
# LLM DECISION
# ----------------------------

def ask_llm(agent):
    pos = agent["pos"]
    model_name = agent["model"]
    
    system_msg = "You are a grid move generator. Respond ONLY with one word: UP, DOWN, LEFT, or RIGHT. No sentences. No reasoning. No punctuation."
    user_prompt = f"Goal: {st.session_state.treasure}. Traps: {st.session_state.traps}. Position: {pos}. Grid: {GRID_SIZE}x{GRID_SIZE}. Next Move?"

    try:
        print(f"\n[DEBUG] {agent['name']} ({model_name}) calling Ollama...")
        completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0, 
            timeout=60.0,
            max_tokens=15 # Hard cutoff for any rambling
        )
        raw_text = completion.choices[0].message.content.strip().upper()
        print(f"[DEBUG] {agent['name']} raw response: {raw_text}")
        
        # Regex parsing: find the first occurrence of a direction word
        match = re.search(r"\b(UP|DOWN|LEFT|RIGHT)\b", raw_text)
        
        if match:
            move = match.group(1)
            return move, move
        else:
            return None, f"ERR: Bad Output"

    except Exception as e:
        print(f"[DEBUG] {agent['name']} error: {e}")
        return None, f"ERR: {str(e)[:15]}"

# ----------------------------
# MOVE AGENT
# ----------------------------

def move_agent(agent, move_dir):
    if not move_dir:
        return 

    x, y = agent["pos"]
    if move_dir == "UP": y -= 1
    elif move_dir == "DOWN": y += 1
    elif move_dir == "LEFT": x -= 1
    elif move_dir == "RIGHT": x += 1

    x = max(0, min(GRID_SIZE - 1, x))
    y = max(0, min(GRID_SIZE - 1, y))
    agent["pos"] = [x, y]

# ----------------------------
# STEP SIMULATION
# ----------------------------

def step():
    print("\n--- NEW SIMULATION STEP STARTED ---")
    for a in st.session_state.agents:
        if not a.get("active", True):
            continue
            
        # Update status to show active thinking
        old_thought = a["thought"]
        a["thought"] = "Thinking..."
        # Note: In Streamlit, this update won't show until the script finishes or a rerun happens.
        # But we use the terminal logs for real-time tracking.
        
        move_dir, result = ask_llm(a)
        move_agent(a, move_dir)
        a["thought"] = result

# ----------------------------
# UI
# ----------------------------

st.set_page_config(page_title="Pixel Raiders", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    .agent-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 10px;
        backdrop-filter: blur(10px);
    }
    .thought-bubble {
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.9em;
        color: #94a3b8;
        border-left: 3px solid #3b82f6;
        padding-left: 10px;
    }
    .error-text {
        color: #f87171;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.title("🏆 Pixel Raiders")

col1, col2 = st.columns([2, 1])

with col1:
    placeholder = st.empty()
    grid_img = draw_grid()
    placeholder.image(grid_img, use_column_width=True)

with col2:
    st.subheader("Agents Status")
    for a in st.session_state.agents:
        with st.container():
            is_active = a.get("active", True)
            status_color = "#94a3b8" if is_active and not ("ERR" in a["thought"]) else "#f87171"
            display_thought = a["thought"] if is_active else "ELIMINATED"
            card_opacity = "1.0" if is_active else "0.5"
            
            st.markdown(f"""
            <div class="agent-card" style="opacity:{card_opacity};">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h4 style="margin:0; color:{agent_colors[a['color']]};">{a['name']}</h4>
                    <span style="font-size:0.8em; color:{status_color}; font-weight:bold;">{display_thought}</span>
                </div>
                <div style="font-size:0.7em; color:#64748b; margin-top:2px;">Model: {a['model']} | Pos: {a['pos']}</div>
            </div>
            """, unsafe_allow_html=True)

# ----------------------------
# CONTROLS
# ----------------------------

st.divider()
c1, c2, c3, _ = st.columns([1, 1, 1, 3])

if c1.button("▶ Auto Play", use_container_width=True):
    st.session_state.running = True

if c2.button("⏸ Stop", use_container_width=True):
    st.session_state.running = False

if c3.button("Step Once", use_container_width=True):
    step()
    st.rerun()

# ----------------------------
# AUTO LOOP
# ----------------------------

if st.session_state.running:
    step()
    
    # Refresh Grid
    grid_img = draw_grid()
    placeholder.image(grid_img, use_column_width=True)

    for a in st.session_state.agents:
        if not a.get("active", True):
            continue

        if a["pos"] == st.session_state.treasure:
            st.balloons()
            st.success(f"🎉 {a['name']} found the treasure!")
            st.session_state.running = False
        
        if a["pos"] in st.session_state.traps:
            st.warning(f"⚠️ {a['name']} hit a trap at {a['pos']}!")
            a["active"] = False

    # Check if all agents are eliminated
    if all(not a.get("active", True) for a in st.session_state.agents):
        st.error("💀 MISSION FAILED: All raiders eliminated.")
        st.session_state.running = False

    time.sleep(0.5)
    st.rerun()