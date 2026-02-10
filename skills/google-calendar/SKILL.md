---
name: google-calendar
description: "Manage Google Calendar events using a Service Account. Use the `calendar_tool.py` helper script to list upcoming events and create new appointments."
metadata:
  {
    "openclaw":
      { "emoji": "📅", "requires": { "env": ["GOOGLE_SERVICE_ACCOUNT_JSON"] }, "primaryEnv": "GOOGLE_SERVICE_ACCOUNT_JSON" },
  }
---

# Google Calendar Skill

Access and manage Google Calendar events using a Service Account. The credentials are stored in the environment variable `GOOGLE_SERVICE_ACCOUNT_JSON`.

**Prerequisites:**

1. Google Calendar API enabled in Google Cloud Project.
2. The user's calendar must be shared with the Service Account email.

## Setup (Automatic in Codespaces)

The credentials are loaded from `GOOGLE_SERVICE_ACCOUNT_JSON`. Dependencies (`google-auth`, `google-api-python-client`) should already be installed from the Drive skill setup.

```bash
# Verify credentials file exists (created by drive skill or manual step)
if [ ! -f /tmp/gsa_credentials.json ]; then
    echo "$GOOGLE_SERVICE_ACCOUNT_JSON" > /tmp/gsa_credentials.json
fi
export GOOGLE_APPLICATION_CREDENTIALS="/tmp/gsa_credentials.json"
```

## Available Commands

All commands use the helper script `calendar_tool.py` located in the skill directory.

### List upcoming 10 events

```bash
python ~/.openclaw/skills/google-calendar/calendar_tool.py list
```

### Show today's agenda

```bash
python ~/.openclaw/skills/google-calendar/calendar_tool.py today
```

### Create a new event

Format: `create "YYYY-MM-DD" "HH:MM" "Duration(mins)" "Title"`

```bash
python ~/.openclaw/skills/google-calendar/calendar_tool.py create "2026-02-11" "10:00" "60" "Reunión de estrategia"
```

## Notes

- The Service Account acts as a "delegate". It can only see/modify calendars shared with it.
- Timezone handling: Defaults to 'Europe/Madrid' (CET/CEST) unless specified in code.
- Cost: 0€ (Google Calendar API is free).
