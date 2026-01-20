# Repository Scope and Purpose

## What This Repository Contains

This repository, **smartthings-mcp-and-agent**, is a **Python backend framework** for smart home automation. It provides:

### Core Components

1. **MCP (Model Context Protocol) Server**
   - Exposes smart home device controls as tools for LLMs
   - Implements the MCP specification
   - Allows AI assistants like Claude to control devices
   - Written in **Python 3.11+**

2. **Natural Language AI Agent**
   - Interprets user commands in natural language
   - Translates requests into device actions
   - Handles disambiguation and safety checks
   - Uses OpenAI, Anthropic, or local LLM models

3. **SmartThings Provider**
   - Python client for Samsung SmartThings API
   - Manages authentication and API calls
   - Caches device state for performance
   - Supports all SmartThings device types

4. **Provider Abstraction Layer**
   - Extensible design for multiple platforms
   - Stubs for Home Assistant, Matter, Alexa
   - Allows adding new smart home platforms

## What This Repository Does NOT Contain

### ❌ No Mobile Applications
- This is **NOT** an Android app
- This is **NOT** an iOS app
- This is **NOT** a mobile application of any kind

### ❌ No Frontend/UI Code
- This is **NOT** a web application
- This is **NOT** a user interface
- No HTML, CSS, JavaScript, React, etc.

### ❌ No TV Applications
- This is **NOT** a Samsung TV app
- This is **NOT** a Tizen app
- This is **NOT** an Android TV app

### ❌ No Weather App
- This is **NOT** a weather application
- SmartThings devices may report weather data (as a capability)
- But this repo doesn't provide weather services

## Technology Stack

### Languages
- **Python 3.11+** - Primary language for all code
- No Java, Kotlin, Swift, or mobile languages

### Key Dependencies
- `aiohttp` - Async HTTP client for API calls
- `pydantic` - Data validation and models
- `structlog` - Structured logging
- OpenAI/Anthropic/Ollama clients - LLM integration

### Platform
- Backend server/library
- Runs on Linux, macOS, Windows
- Designed for server deployment or CLI usage

## Repository Purpose

This repository enables **AI assistants to control smart home devices** through:

1. **Natural Language Processing**
   - "Turn on the living room lights"
   - "What's the temperature in the bedroom?"
   - "Set the thermostat to 72 degrees"

2. **Model Context Protocol Integration**
   - LLMs can discover available devices
   - LLMs can query device state
   - LLMs can execute commands
   - Works with Claude Desktop, custom MCP clients

3. **Smart Home Automation**
   - Control lights, thermostats, locks, sensors
   - Query device status and history
   - Manage locations and rooms
   - Execute scenes and automations

## Common Misconceptions

### "Why does it mention Samsung TVs?"
- SmartThings can control Samsung TVs
- TVs are one of many device types supported
- The repo controls TVs via SmartThings API
- It's not a TV-specific application

### "Why does test output show weather?"
- Samsung TVs have ambient mode with weather displays
- This is a device capability, not an app feature
- The repo reads device state, including weather capability
- It doesn't provide weather data itself

### "Why is the branch named 'update-weather-app-for-android'?"
- **This is a mistake/mislabeling**
- The branch name doesn't match the repository purpose
- No Android app work should be done in this repository
- The branch should be renamed or the work moved elsewhere

## Correct Use Cases

### ✅ Appropriate Work for This Repository
- Improving Python code quality
- Adding new SmartThings API features
- Enhancing the MCP server implementation
- Adding support for new device types
- Improving the AI agent's natural language understanding
- Adding new provider integrations (Home Assistant, etc.)
- Fixing bugs in the Python codebase
- Improving documentation
- Adding Python tests

### ❌ Inappropriate Work for This Repository
- Developing Android applications
- Creating mobile apps
- Building TV applications
- Developing weather apps
- Frontend/UI development
- Any non-Python work unrelated to backend automation

## Where Should Different Work Go?

If you need to work on:

- **Android App for SmartThings**: Create a separate repository (e.g., `smartthings-android-app`)
- **Samsung TV Weather App**: Create a separate repository (e.g., `samsung-tv-weather-app`)
- **Web Frontend**: Create a separate repository (e.g., `smartthings-web-ui`)
- **iOS App**: Create a separate repository (e.g., `smartthings-ios-app`)

## Summary

**This repository is strictly for:**
- Python backend code
- MCP server implementation
- AI agent for natural language control
- SmartThings API integration
- Smart home automation logic

**All other types of applications should be in separate repositories.**

---

**If you're unsure whether your work belongs here, ask:**
1. Is it Python code?
2. Does it relate to MCP server or AI agent functionality?
3. Is it backend smart home automation logic?

If the answer to all three is NO, it belongs in a different repository.
