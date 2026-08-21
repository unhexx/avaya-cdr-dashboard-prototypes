#!/usr/bin/env bash
# Инициализация рабочего окружения Avaya CDR Dashboard на Linux.
# Поднимает локальный .venv и .agent; пакеты памяти — из шаблона контура, если он есть.
set -euo pipefail

WIZARD=false
QUIET=0
OUT_PROMPT=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --wizard) WIZARD=true; shift ;;
    --quiet|-q) QUIET=1; shift ;;
    --output-file) OUT_PROMPT="$2"; shift 2 ;;
    -h|--help)
      echo "Usage: bash Agent-Init.sh [--wizard] [--quiet] [--output-file PATH]"
      exit 0
      ;;
    *) echo "Unknown arg: $1"; exit 2 ;;
  esac
done

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

log() { [[ "$QUIET" == "1" ]] || echo "[Agent-Init] $*"; }

TEMPLATE=""
if [[ -d "$ROOT/../agentic_loop_template/memory" ]]; then
  TEMPLATE="$(cd "$ROOT/../agentic_loop_template" && pwd)"
elif [[ -d "$ROOT/agentic_loop_template/memory" ]]; then
  TEMPLATE="$(cd "$ROOT/agentic_loop_template" && pwd)"
fi

if [[ -n "$TEMPLATE" && ! -e "$ROOT/agentic_loop_template" ]]; then
  if [[ "$TEMPLATE" == "$(cd "$ROOT/.." && pwd)/agentic_loop_template" ]]; then
    ln -s "../agentic_loop_template" "$ROOT/agentic_loop_template"
  else
    ln -s "$TEMPLATE" "$ROOT/agentic_loop_template"
  fi
  log "symlink agentic_loop_template -> $(readlink "$ROOT/agentic_loop_template")"
elif [[ -L "$ROOT/agentic_loop_template" ]]; then
  log "symlink agentic_loop_template already present"
elif [[ -z "$TEMPLATE" ]]; then
  log "agentic_loop_template not found (optional); continuing with local .venv"
fi

log "root=$ROOT template=${TEMPLATE:-none} os=$(uname -s) arch=$(uname -m)"

if [[ ! -d .venv ]]; then
  log "creating .venv"
  if command -v uv >/dev/null 2>&1; then
    uv venv .venv
  else
    python3 -m venv .venv
  fi
fi

# shellcheck disable=SC1091
source .venv/bin/activate

if [[ -n "$TEMPLATE" ]]; then
  MARKER="# avaya-cdr-pythonpath"
  if ! grep -q "$MARKER" .venv/bin/activate 2>/dev/null; then
    printf '\n%s\nexport PYTHONPATH="%s${PYTHONPATH:+:$PYTHONPATH}"\n' "$MARKER" "$TEMPLATE" >> .venv/bin/activate
  fi
  export PYTHONPATH="${TEMPLATE}${PYTHONPATH:+:$PYTHONPATH}"
fi

if command -v uv >/dev/null 2>&1; then
  uv pip install -q pyyaml pytest jsonschema >/dev/null 2>&1 || true
else
  python -m pip install -U pip -q 2>/dev/null || true
  python -m pip install -q pyyaml pytest jsonschema 2>/dev/null || true
fi

mkdir -p .agent
if [[ ! -f .agent/project_config.json && -n "$TEMPLATE" && -f "$TEMPLATE/.agent/project_config.example.json" ]]; then
  cp "$TEMPLATE/.agent/project_config.example.json" .agent/project_config.json
  log "wrote .agent/project_config.json from example"
fi

if [[ -n "$TEMPLATE" ]]; then
  python -m memory state init 2>/dev/null || true
  python -m memory state compact >/dev/null 2>&1 || true
fi

chmod +x Agent-Init.sh 2>/dev/null || true

VERSION="0.2.0"
if [[ -n "$TEMPLATE" ]]; then
  VERSION="$(cat "$TEMPLATE/VERSION" 2>/dev/null || echo 3.5.0)"
fi

if [[ "$WIZARD" == true ]]; then
  echo ""
  echo "=== Avaya CDR Dashboard onboarding ==="
  echo "  Spec index: docs/PROJECT_SPECIFICATION.md"
  echo "  Next: source .venv/bin/activate"
  echo "        prompts/short_orchestrator_prompt.md"
else
  log "Env ready. source .venv/bin/activate"
  log "Tip: bash Agent-Init.sh --wizard for a short recap"
fi

PROMPT_PATH="${OUT_PROMPT:-$ROOT/.agent/starter_prompt_grok.txt}"
cat > "$PROMPT_PATH" <<EOP
You are running the development loop in /home/unhex/_PROJECT/avaya-cdr-dashboard-prototypes.

Cold-start:
1. Read .agent/TODO.md, .agent/PLAN.md, docs/STATUS.md, docs/TASKS.md, docs/ACCEPTANCE.md
2. Take the next unfinished INVEST item only
3. Product docs English; commits and code comments in natural Russian; identifiers English
4. Never reverse SysMonitor; IPO >=R11.1 encrypted recordings return 409 meta-only
5. Use fixtures for CI; do not require a live PBX

Begin as Orchestrator.
EOP

log "starter_prompt=$PROMPT_PATH"
log "template_version=$VERSION"
echo "AGENT_INIT_OK version=$VERSION prompt=$PROMPT_PATH"
