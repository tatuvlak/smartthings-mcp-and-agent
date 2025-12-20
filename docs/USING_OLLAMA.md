# Using SmartThings Agent with Local LLM (Ollama)

## Quick Start with Ollama (No API Key Required)

If you don't have an OpenAI or Anthropic API key, you can use Ollama to run LLMs locally on your computer.

### Step 1: Install Ollama

1. Visit https://ollama.ai
2. Download and install for your OS (Windows, Mac, or Linux)
3. Run Ollama (it will start a background service)

### Step 2: Download a Model

Open a terminal and run:
```bash
ollama pull llama2
```

This downloads the Llama 2 model (~4GB). Other options:
- `ollama pull mistral` (smaller, faster)
- `ollama pull neural-chat` (good for conversations)
- `ollama pull orca-mini` (fast)

### Step 3: Configure Your Project

Edit `.env` file:
```env
# Switch from OpenAI to Ollama
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

### Step 4: Run the Chat

```bash
python -m src.main chat
```

That's it! The chat will work exactly the same, but using your local Ollama model.

---

## LLM Provider Comparison

| Provider | Cost | Speed | Privacy | Setup Difficulty |
|----------|------|-------|---------|------------------|
| **Ollama (Local)** | Free | Medium | 100% Private | Easy |
| **OpenAI** | $$ | Fast | Cloud-based | Easy |
| **Anthropic** | $$ | Fast | Cloud-based | Easy |

---

## Troubleshooting Ollama

### Problem: "Connection refused" when starting chat
**Cause**: Ollama is not running  
**Fix**:
1. Make sure you installed Ollama
2. Start Ollama manually or restart computer
3. Check http://localhost:11434 in browser to verify it's running

### Problem: Chat is very slow
**Cause**: Using a large model on limited hardware  
**Fix**: Use a smaller model
```bash
# Download a faster model
ollama pull mistral

# Update .env
OLLAMA_MODEL=mistral

# Try again
python -m src.main chat
```

### Problem: "Model not found"
**Cause**: Model hasn't been downloaded  
**Fix**:
```bash
# List available models
ollama list

# Download the model from .env
ollama pull llama2
```

---

## Available Models

### Recommended (Good Balance)
- **mistral** (7B) - Fast and accurate, ~4GB
- **neural-chat** (7B) - Good at conversations, ~4GB

### Best Quality (Slower)
- **llama2** (7B/13B) - Reliable, ~4-13GB
- **orca-mini** (3B) - Good accuracy in small size, ~2GB

### Fastest (Less Accurate)
- **tinyllama** (1B) - Super fast, ~1GB
- **orca-mini** (3B) - Balance of speed/quality, ~2GB

### Try Multiple
```bash
ollama pull llama2          # Default
ollama pull mistral         # Faster alternative
ollama pull neural-chat     # Best for chat
```

---

## Switching Between Providers

### Switch from OpenAI to Ollama
1. Edit `.env`:
   ```env
   LLM_PROVIDER=ollama
   ```
2. No API key needed!

### Switch from Ollama to OpenAI
1. Edit `.env`:
   ```env
   LLM_PROVIDER=openai
   OPENAI_API_KEY=your_key_here
   ```
2. Get API key from https://platform.openai.com/account/api-keys

### Switch from Ollama to Anthropic
1. Edit `.env`:
   ```env
   LLM_PROVIDER=anthropic
   ANTHROPIC_API_KEY=your_key_here
   ```
2. Get API key from https://console.anthropic.com/

---

## Performance Tips

### Speed Up Ollama

1. **Use Ollama GPU Support** (if you have an NVIDIA GPU)
   ```bash
   # NVIDIA GPU support is automatic if installed
   # Check if GPU is being used in Ollama logs
   ```

2. **Use a Smaller Model**
   ```env
   OLLAMA_MODEL=mistral
   ```

3. **Increase Context Window** (more expensive but better conversations)
   ```env
   OLLAMA_MODEL=mistral
   # Add to .env or modify prompts
   ```

### Improve Quality

1. **Use a Larger Model**
   ```env
   OLLAMA_MODEL=llama2:13b
   ```
   Download with: `ollama pull llama2:13b`

2. **Use Better Models**
   - Try `neural-chat` for better conversation quality
   - Try `orca-mini` for better instruction following

---

## Resources

- **Ollama Website**: https://ollama.ai
- **Model Library**: https://ollama.ai/library
- **GitHub**: https://github.com/jmorganca/ollama

---

## Full Configuration Examples

### Minimal Setup (Just Want to Chat)
```env
SMARTTHINGS_PAT_TOKEN=your_token

# Local LLM - No API key needed!
LLM_PROVIDER=ollama
OLLAMA_MODEL=mistral
OLLAMA_BASE_URL=http://localhost:11434
```

### Premium Setup (OpenAI)
```env
SMARTTHINGS_PAT_TOKEN=your_token

# OpenAI for best quality
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-xxx...
LLM_MODEL=gpt-4-turbo-preview
```

### Privacy-First Setup (Local Everything)
```env
SMARTTHINGS_PAT_TOKEN=your_token

# Local LLM - all processing on your machine
LLM_PROVIDER=ollama
OLLAMA_MODEL=neural-chat
OLLAMA_BASE_URL=http://localhost:11434
```

---

## Next Steps

1. Install Ollama from https://ollama.ai
2. Download a model: `ollama pull mistral`
3. Update `.env` with `LLM_PROVIDER=ollama`
4. Run: `python -m src.main chat`
5. Start chatting!

No API keys, no monthly bills, full privacy! 🚀

---

**Date**: December 19, 2025  
**Status**: Ready to use
