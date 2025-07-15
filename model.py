import requests
import pandas as pd
import json

# CSV-Export
url = "https://openrouter.ai/api/v1/models"
response = requests.get(url)
data = response.json()['data']

# DataFrame und CSV
df = pd.DataFrame([{
    "Modellname": m.get('name', ''),
    "Provider": m.get('id', '').split('/')[0],
    "Beschreibung": m.get('description', ''),
    "Typische Anwendungsfälle": ", ".join(m.get('use_cases', [])) if m.get('use_cases') else '',
    "Stärken": ", ".join(m.get('strengths', [])) if m.get('strengths') else '',
    "Schwächen": ", ".join(m.get('weaknesses', [])) if m.get('weaknesses') else '',
    "Preis Prompt (USD/1k Tokens)": m.get('pricing', {}).get('prompt', ''),
    "Preis Completion (USD/1k Tokens)": m.get('pricing', {}).get('completion', ''),
    "Kontextlänge": m.get('context_length', ''),
    "Tags/Fähigkeiten": ", ".join(m.get('supported_parameters', []))
} for m in data])
df.to_csv("openrouter_models_complete_listing.csv", index=False)

# JSON-Export
with open("openrouter_models_complete_listing.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

