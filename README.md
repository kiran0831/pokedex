# 🎮 Pokédex

A full-featured Pokémon app built with Streamlit and PokéAPI.

## Features
- 🔍 Search any Pokémon by name
- 🎲 Random Pokémon generator
- ⚔️ Turn-based battle system with real moves and stats

## How It Works

### Search
- Type any Pokémon name to get full details
- Shows image, types, height, weight, and all base stats with progress bars

### Random
- Generates a random Pokémon from all 1025 available Pokémon
- Displays full info card

### Battle System
- Enter two Pokémon names to start a battle
- Each Pokémon gets 4 randomly selected moves from their actual moveset
- Faster Pokémon (higher speed stat) attacks first each round
- Damage formula: (move power × attacker attack) / defender defense + random factor
- HP is doubled from base stats for longer, more interesting battles
- Battle continues round by round until one Pokémon reaches 0 HP
- Full battle log tracks every move and damage dealt

## Tech Stack
- Python
- Streamlit
- PokéAPI (free, no API key needed)
- Groq AI (llama-3.3-70b)

## Run Locally
pip install -r requirements.txt
streamlit run poke.py
