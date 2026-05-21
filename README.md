# 🎮 PokéDex

A full-stack application featuring real-time REST API integration, dynamic UI rendering, and a turn-based combat engine built on live game data.

## Key Technical Highlights
- Real-time REST API integration with PokéAPI
- Dynamic UI state management using Streamlit session state
- Turn-based combat engine with damage calculation algorithms
- Move fetching with random sampling optimization
- Responsive two-column layout with live HP progress bars

## Features
- 🔍 Search any Pokémon by name
- 🎲 Random Pokémon generator from 1025+ Pokémon
- ⚔️ Turn-based battle system with real moves and stats

## How It Works

### Search
- Search any Pokémon by name to get full details
- Displays image, types, height, weight and all base stats with visual progress bars

### Random
- Generates a random Pokémon from all 1025 available Pokémon
- Displays full info card instantly

### Battle System
- Enter two Pokémon to start a battle
- Each Pokémon gets 4 randomly selected moves from their actual moveset
- Faster Pokémon (higher speed stat) attacks first each round
- Damage formula: (move power × attacker attack) / defender defense + random variance
- HP doubled from base stats for balanced battle length
- Full battle log tracks every move and damage dealt

## Tech Stack
- Python
- Streamlit
- PokéAPI (free, no key required)
- Groq AI (llama-3.3-70b)

## Run Locally
pip install -r requirements.txt
streamlit run pokedex.py
