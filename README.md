# 🏆 Pixel Raiders

A high-stakes, multi-agent LLM treasure hunting arena. Watch different local AI models (Gemma, Llama, Qwen) compete in a grid-based world filled with traps and riches.

![Pixel Raiders Gameplay Preview](https://github.com/user-attachments/assets/76054f9d-06e8-470f-b45a-297229413819)

## 🚀 Vision
Pixel Raiders is a benchmarking playground for local LLMs. It tests the ability of small-parameter models (3B-14B) to follow strict spatial instructions, avoid obstacles, and reach a goal using a minimalist state-representation.

## 🛠 Tech Stack
- **Frontend/UI**: [Streamlit](https://streamlit.io/)
- **AI Backend**: [Ollama](https://ollama.com/) (OpenAI-compatible API)
- **Graphics**: Python Imaging Library (PIL)
- **Logic**: Python 3.12+

## 🏗 Architecture

The system uses a **Step-Based Simulation Loop**:

1. **State Observation**: The current grid state, trap locations, and agent positions are serialized into a minimalist text prompt.
2. **Multi-Model Dispatch**: Each agent is assigned a unique Ollama model. The system calls them sequentially.
3. **Regex Extraction**: Chatty responses are parsed using regex `\b(UP|DOWN|LEFT|RIGHT)\b` to extract the move.
4. **Collision Physics**: The engine checks for traps (elimination) or treasure (victory).
5. **State Sync**: Streamlit triggers a UI rerun to reflect the new positions.

### Code Snippet: The Decision Engine
```python
def ask_llm(agent):
    system_msg = "You are a grid move generator. Respond ONLY with: UP, DOWN, LEFT, or RIGHT."
    user_prompt = f"Goal: {target}. Position: {pos}. Grid: 8x8. Next Move?"

    completion = client.chat.completions.create(
        model=agent["model"],
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=15
    )
    # Robust regex extraction
    match = re.search(r"\b(UP|DOWN|LEFT|RIGHT)\b", raw_text)
    return match.group(1)
```

## 🚥 Getting Started

1. **Install Ollama**: Ensure [Ollama](https://ollama.com/) is running locally.
2. **Pull Models**:
   ```bash
   ollama pull gemma3:4b
   ollama pull llama3.2:latest
   ```
3. **Install Dependencies**:
   ```bash
   pip install streamlit requests pillow openai
   ```
4. **Run the Arena**:
   ```bash
   streamlit run app.py
   ```

## 🤝 Contributing
We welcome contributions! Here's the roadmap:
- [ ] **Heuristic Mode**: Compare LLM moves against A* pathfinding.
- [ ] **Multiplayer**: Allow users to control one agent via keyboard.
- [ ] **Map Editor**: Click tiles to place custom traps.
- [ ] **VRAM Optimization**: Parallelize calls for models already loaded in memory.