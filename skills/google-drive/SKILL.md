---
name: google-drive
description: "Read and write files in Google Drive using a Service Account. Use the `drive_tool.py` helper script to list, read, search, and upload files to the shared folder 'Cerebro_Proyecto_Gemini'."
metadata:
  {
    "openclaw":
      { "emoji": "📂", "requires": { "env": ["GOOGLE_SERVICE_ACCOUNT_JSON"] }, "primaryEnv": "GOOGLE_SERVICE_ACCOUNT_JSON" },
  }
---

# Google Drive Skill

Access Google Drive files using a Service Account. The credentials are stored in the environment variable `GOOGLE_SERVICE_ACCOUNT_JSON`.

## Setup (One-time, automatic in Codespaces)

The credentials are loaded from the `GOOGLE_SERVICE_ACCOUNT_JSON` environment variable (set via GitHub Secrets). On first use, run:

```bash
pip install google-auth google-api-python-client 2>/dev/null
echo "$GOOGLE_SERVICE_ACCOUNT_JSON" > /tmp/gsa_credentials.json
export GOOGLE_APPLICATION_CREDENTIALS="/tmp/gsa_credentials.json"
```

## Available Commands

All commands use the helper script `drive_tool.py` located in the skill directory.

### List files in Drive

```bash
python ~/.openclaw/skills/google-drive/drive_tool.py list
```

### Search files by name

```bash
python ~/.openclaw/skills/google-drive/drive_tool.py search "presupuesto"
```

### Read a text/markdown file content by name

```bash
python ~/.openclaw/skills/google-drive/drive_tool.py read "nombre_del_archivo.md"
```

### Upload a local file to Drive

```bash
python ~/.openclaw/skills/google-drive/drive_tool.py upload "/path/to/local/file.md"
```

### Create a new text file in Drive

```bash
python ~/.openclaw/skills/google-drive/drive_tool.py create "nombre_archivo.md" "Contenido del archivo aquí"
```

## Notes

- The Service Account only has access to the shared folder `Cerebro_Proyecto_Gemini`.
- It CANNOT access personal files outside that folder.
- Supported file types for reading: .md, .txt, .pdf (text only), Google Docs.
- Cost: 0€ (Google Drive API is free).
