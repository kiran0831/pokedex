import requests
import random
import streamlit as st
from groq import Groq

# Base URL for PokeAPI — all requests start with this
url = "https://pokeapi.co/api/v2"

st.title("🎮 Pokédex")

# ─────────────────────────────────────────
# SESSION STATE INITIALIZATION
# All variables that need to persist across reruns
# are initialized here — only on first run
# ─────────────────────────────────────────

# Which page to show: "search", "random", or "fight"
if "page" not in st.session_state:
    st.session_state.page = "search"

# Stores the random Pokémon ID when random button is clicked
if "random_pokemon" not in st.session_state:
    st.session_state.random_pokemon = None

# Stores the entire battle state dictionary during a fight
# None means no battle is active
if "battle" not in st.session_state:
    st.session_state.battle = None

# Stores fetched data for Pokémon 1 preview before battle starts
if "p1_preview" not in st.session_state:
    st.session_state.p1_preview = None

# Stores fetched data for Pokémon 2 preview before battle starts
if "p2_preview" not in st.session_state:
    st.session_state.p2_preview = None

# ─────────────────────────────────────────
# SIDEBAR NAVIGATION
# Buttons update session state to switch pages
# ─────────────────────────────────────────
with st.sidebar:
    st.header("Menu")

    # Switch to search page
    if st.button("🔍 Search"):
        st.session_state.page = "search"

    # Switch to random page and generate a random Pokémon ID (1–1025)
    if st.button("🎲 Random"):
        st.session_state.page = "random"
        st.session_state.random_pokemon = str(random.randint(1, 1025))

    # Switch to fight page and reset all battle/preview state
    if st.button("⚔️ Fight"):
        st.session_state.page = "fight"
        st.session_state.battle = None
        st.session_state.p1_preview = None
        st.session_state.p2_preview = None

# ─────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────

def get_stat(pokemon, stat_name):
    """
    Returns the base stat value for a given stat name.
    e.g. get_stat(pikachu, "attack") → 55
    Returns 50 as default if stat not found.
    """
    for s in pokemon["stats"]:
        if s["stat"]["name"] == stat_name:
            return s["base_stat"]
    return 50

def get_moves(pokemon):
    """
    Fetches up to 4 usable moves for a Pokémon.
    Samples 15 random moves from the Pokémon's move list,
    then filters for moves that have power (damage moves).
    Returns a list of dicts: {name, power, type}
    """
    move_list = []
    # Sample 15 random moves to avoid fetching all of them (too slow)
    sample = random.sample(pokemon["moves"], min(15, len(pokemon["moves"])))
    for m in sample:
        # Fetch full move details from the move's URL
        res = requests.get(m["move"]["url"]).json()
        # Only include moves that deal damage (have power)
        if res["power"]:
            move_list.append({
                "name": res["name"],
                "power": res["power"],
                "type": res["type"]["name"]
            })
        # Stop once we have 4 moves
        if len(move_list) == 4:
            break
    return move_list

def calc_damage(attacker, move, defender):
    """
    Calculates damage dealt by attacker using a move against defender.
    Formula: (move_power * attacker_attack / defender_defense) * random_factor
    Random factor (0.85–1.0) adds slight variation like real Pokémon games.
    Returns minimum 1 damage.
    """
    atk = get_stat(attacker, "attack")
    defense = get_stat(defender, "defense")
    dmg = max(1, int((move["power"] * atk / defense) * (0.85 + random.random() * 0.15)))
    return dmg

def show_pokemon(data):
    """
    Displays full Pokémon info card:
    - Image on the left
    - Name, ID, types, height, weight, stats with progress bars on the right
    """
    col1, col2 = st.columns(2)
    with col1:
        st.image(data["sprites"]["front_default"], width=200)
    with col2:
        st.subheader(f"#{data['id']} — {data['name'].capitalize()}")
        # Extract type names from nested list of dicts
        types = [t["type"]["name"] for t in data["types"]]
        st.write("**Types:**", ", ".join(types))
        # Height and weight are in decimetres/hectograms → convert to m/kg
        st.write(f"**Height:** {data['height']/10} m")
        st.write(f"**Weight:** {data['weight']/10} kg")
        st.write("**Stats:**")
        for stat in data["stats"]:
            st.write(stat['stat']['name'].capitalize())
            # 255 is the max possible base stat in Pokémon
            st.progress(stat['base_stat'] / 255)

def show_hp_bars(b):
    """
    Displays HP bars and images for both Pokémon during battle.
    b = battle dictionary from session state
    p1 uses front sprite, p2 uses back sprite (like real games)
    """
    col1, col2 = st.columns(2)
    with col1:
        st.image(b['p1']['sprites']['front_default'], width=150)
        st.write(f"**{b['p1']['name'].upper()}**")
        # progress() takes value between 0.0 and 1.0
        st.progress(max(0, b['p1_hp'] / b['p1_maxhp']))
        st.write(f"{max(0, b['p1_hp'])} / {b['p1_maxhp']} HP")
    with col2:
        st.image(b['p2']['sprites']['back_default'], width=150)
        st.write(f"**{b['p2']['name'].upper()}**")
        st.progress(max(0, b['p2_hp'] / b['p2_maxhp']))
        st.write(f"{max(0, b['p2_hp'])} / {b['p2_maxhp']} HP")

# ─────────────────────────────────────────
# PAGE: SEARCH
# ─────────────────────────────────────────
if st.session_state.page == "search":
    name = st.text_input("Enter Pokémon name").strip().lower()
    if name:
        res = requests.get(f"{url}/pokemon/{name}")
        # 200 = success, 404 = not found
        if res.status_code == 200:
            show_pokemon(res.json())
        else:
            st.error("Pokémon not found!")

# ─────────────────────────────────────────
# PAGE: RANDOM
# ─────────────────────────────────────────
elif st.session_state.page == "random":
    # random_pokemon is set when the sidebar button was clicked
    if st.session_state.random_pokemon:
        res = requests.get(f"{url}/pokemon/{st.session_state.random_pokemon}")
        if res.status_code == 200:
            show_pokemon(res.json())

# ─────────────────────────────────────────
# PAGE: FIGHT
# ─────────────────────────────────────────
elif st.session_state.page == "fight":
    st.header("⚔️ Pokémon Fight!")
    # Shorthand reference to battle state
    b = st.session_state.battle

    # ── PHASE 1: SETUP ──
    # battle is None means no battle started yet
    if b is None:
        col1, col2 = st.columns(2)
        with col1:
            p1_name = st.text_input("Pokémon 1").strip().lower()
            # Fetch and store p1 data as user types
            if p1_name:
                r1 = requests.get(f"{url}/pokemon/{p1_name}")
                if r1.status_code == 200:
                    st.session_state.p1_preview = r1.json()
        with col2:
            p2_name = st.text_input("Pokémon 2").strip().lower()
            # Fetch and store p2 data as user types
            if p2_name:
                r2 = requests.get(f"{url}/pokemon/{p2_name}")
                if r2.status_code == 200:
                    st.session_state.p2_preview = r2.json()

        # Show preview images if either Pokémon is loaded
        if st.session_state.p1_preview or st.session_state.p2_preview:
            col1, col2 = st.columns(2)
            with col1:
                if st.session_state.p1_preview:
                    st.image(st.session_state.p1_preview["sprites"]["front_default"], width=150)
                    st.write(f"**{st.session_state.p1_preview['name'].upper()}**")
            with col2:
                if st.session_state.p2_preview:
                    st.image(st.session_state.p2_preview["sprites"]["back_default"], width=150)
                    st.write(f"**{st.session_state.p2_preview['name'].upper()}**")

        if st.button("⚔️ Start Battle!"):
            if st.session_state.p1_preview and st.session_state.p2_preview:
                p1 = st.session_state.p1_preview
                p2 = st.session_state.p2_preview
                with st.spinner("Loading moves..."):
                    p1_moves = get_moves(p1)
                    p2_moves = get_moves(p2)
                # Initialize the entire battle state in session state
                st.session_state.battle = {
                    "p1": p1,                          # full Pokémon data
                    "p2": p2,
                    "p1_hp": get_stat(p1, "hp") * 2,  # double HP for longer battles
                    "p2_hp": get_stat(p2, "hp") * 2,
                    "p1_maxhp": get_stat(p1, "hp") * 2,
                    "p2_maxhp": get_stat(p2, "hp") * 2,
                    "p1_moves": p1_moves,              # list of 4 move dicts
                    "p2_moves": p2_moves,
                    "log": [],                         # battle history messages
                    "round": 1,
                    "p1_move": None,                   # index of selected move (None = not chosen yet)
                    "p2_move": None,
                }
                st.rerun()  # rerun to enter battle phase
            else:
                st.error("Enter both Pokémon names!")

    # ── PHASE 2: BATTLE ──
    # Both Pokémon are alive — battle continues
    elif b["p1_hp"] > 0 and b["p2_hp"] > 0:
        st.subheader(f"Round {b['round']}")
        show_hp_bars(b)

        # Show battle log in collapsible section
        if b["log"]:
            with st.expander("Battle Log"):
                for entry in b["log"]:
                    st.write(entry)

        # Move selection buttons for both Pokémon
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**{b['p1']['name'].upper()} moves:**")
            for i, m in enumerate(b["p1_moves"]):
                # Each button stores the move index in session state when clicked
                if st.button(f"{m['name']} (⚡{m['power']})", key=f"p1_m{i}"):
                    st.session_state.battle["p1_move"] = i

        with col2:
            st.write(f"**{b['p2']['name'].upper()} moves:**")
            for i, m in enumerate(b["p2_moves"]):
                if st.button(f"{m['name']} (⚡{m['power']})", key=f"p2_m{i}"):
                    st.session_state.battle["p2_move"] = i

        # Execute the round only when BOTH players have selected a move
        if b["p1_move"] is not None and b["p2_move"] is not None:
            m1 = b["p1_moves"][b["p1_move"]]
            m2 = b["p2_moves"][b["p2_move"]]

            # Faster Pokémon attacks first (speed stat)
            spd1 = get_stat(b["p1"], "speed")
            spd2 = get_stat(b["p2"], "speed")
            log_entries = []

            if spd1 >= spd2:
                # p1 attacks first
                dmg = calc_damage(b["p1"], m1, b["p2"])
                st.session_state.battle["p2_hp"] -= dmg
                log_entries.append(f"🔴 {b['p1']['name']} used {m1['name']} → {dmg} damage!")
                # p2 only attacks back if still alive
                if st.session_state.battle["p2_hp"] > 0:
                    dmg = calc_damage(b["p2"], m2, b["p1"])
                    st.session_state.battle["p1_hp"] -= dmg
                    log_entries.append(f"🔵 {b['p2']['name']} used {m2['name']} → {dmg} damage!")
            else:
                # p2 attacks first
                dmg = calc_damage(b["p2"], m2, b["p1"])
                st.session_state.battle["p1_hp"] -= dmg
                log_entries.append(f"🔵 {b['p2']['name']} used {m2['name']} → {dmg} damage!")
                if st.session_state.battle["p1_hp"] > 0:
                    dmg = calc_damage(b["p1"], m1, b["p2"])
                    st.session_state.battle["p2_hp"] -= dmg
                    log_entries.append(f"🔴 {b['p1']['name']} used {m1['name']} → {dmg} damage!")

            # Save log, advance round, reset move selections
            st.session_state.battle["log"].extend(log_entries)
            st.session_state.battle["round"] += 1
            st.session_state.battle["p1_move"] = None
            st.session_state.battle["p2_move"] = None
            st.rerun()  # rerun to show updated HP bars

    # ── PHASE 3: WINNER ──
    # One Pokémon's HP has reached 0
    else:
        show_hp_bars(b)
        st.balloons()  # celebration animation
        if b["p1_hp"] > 0:
            st.success(f"🏆 {b['p1']['name'].upper()} WINS!")
        else:
            st.success(f"🏆 {b['p2']['name'].upper()} WINS!")

        # Show complete battle history
        with st.expander("Full Battle Log"):
            for entry in b["log"]:
                st.write(entry)

        # Reset everything to play again
        if st.button("🔄 Play Again"):
            st.session_state.battle = None
            st.session_state.p1_preview = None
            st.session_state.p2_preview = None
            st.rerun()
