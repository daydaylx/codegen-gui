#!/bin/bash

APP_NAME="CodeGen GUI"
ENTRY="main.py"
VENV_DIR=".venv"
PYTHON_BIN="python3"

cd "$(dirname "$0")"

echo "🚀 Starte $APP_NAME ..."

# Falls virtuelle Umgebung existiert → aktiviere
if [[ -d "$VENV_DIR" ]]; then
    echo "📦 Aktiviere virtuelle Umgebung ..."
    source "$VENV_DIR/bin/activate"
    PYTHON_BIN="python"
fi

# Prüfen ob Abhängigkeiten installiert sind
# 'httpx' wurde durch 'requests' ersetzt
REQUIRED_MODULES=("PySide6" "requests" "pygments")
MISSING=false

for module in "${REQUIRED_MODULES[@]}"; do
    $PYTHON_BIN -c "import $module" 2>/dev/null || {
        echo "❌ Modul fehlt: $module"
        MISSING=true
    }
done

if [ "$MISSING" = true ]; then
    echo "❗ Bitte installiere die Abhängigkeiten mit:"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Start der Anwendung
echo "🧠 Starte Python-Datei: $ENTRY"
$PYTHON_BIN $ENTRY
