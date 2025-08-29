FROM ollama/ollama:latest

# Expose Ollama API
EXPOSE 11434

# Start Ollama and pull the model on boot
CMD bash -lc "ollama serve & sleep 5 && ollama pull llama3:8b-instruct || true && tail -f /dev/null"
