#!/bin/bash
# setup_openclaw_groq.sh
# Script para configurar LiteLLM y OpenClaw con soporte dual (Gemini/Groq)

echo "🛠️ Iniciando configuración de OpenClaw..."

# VALIDACIÓN 1: Verificar que GROQ_API_KEY existe
if [ -z "$GROQ_API_KEY" ]; then
    echo "❌ ERROR: GROQ_API_KEY no encontrada."
    echo "📖 Configúrala en: https://github.com/settings/codespaces"
    echo "   1. New secret → Nombre: GROQ_API_KEY"
    echo "   2. Valor: tu API key de console.groq.com"
    echo "   3. Reinicia el Codespace después de configurarla"
    exit 1
fi

# VALIDACIÓN 2: Verificar que LiteLLM está instalado
if ! command -v litellm &> /dev/null; then
    echo "❌ ERROR: LiteLLM no instalado."
    echo "Ejecutando instalación automática..."
    pip install litellm
fi

# BACKUP automático de configuración existente
if [ -f "litellm_config.yaml" ]; then
    BACKUP_FILE="litellm_config.yaml.backup.$(date +%s)"
    mv litellm_config.yaml "$BACKUP_FILE"
    echo "📦 Backup creado: $BACKUP_FILE"
fi

# 1. Crear litellm_config.yaml
cat > litellm_config.yaml <<EOF
model_list:
  - model_name: gemini-flash
    litellm_params:
      model: groq/llama-3.3-70b-versatile
      api_key: os.environ/GROQ_API_KEY
      drop_params: true
  - model_name: gemini-flash-backup
    litellm_params:
      model: gemini/gemini-2.5-flash
      api_key: os.environ/GEMINI_API_KEY
      drop_params: true
EOF

echo "✅ litellm_config.yaml creado (Prioridad: Groq)."

# 2. Crear ~/.openclaw/openclaw.json
mkdir -p ~/.openclaw
cat > ~/.openclaw/openclaw.json <<EOF
{
  "models": {
    "providers": {
      "local-proxy": {
        "baseUrl": "http://127.0.0.1:4000/v1",
        "apiKey": "sk-fake-key",
        "api": "openai-completions",
        "models": [
          {
            "id": "gemini-flash",
            "name": "Groq Llama 3.3 (via LiteLLM)",
            "contextWindow": 1000000,
            "maxTokens": 8192
          },
          {
            "id": "gemini-flash-backup",
            "name": "Gemini 2.5 Flash (Backup)",
            "contextWindow": 1000000,
            "maxTokens": 8192
          }
        ]
      }
    }
  },
  "agents": {
    "defaults": {
      "model": {
        "primary": "local-proxy/gemini-flash"
      }
    }
  },
  "gateway": {
    "mode": "local"
  }
}
EOF

echo "✅ ~/.openclaw/openclaw.json configurado."
echo "🚀 ¡Listo! Asegúrate de tener GROQ_API_KEY en tus secretos de Codespaces."
