#!/usr/bin/env bash
set -u
umask 077

# ==============================================================================
# MEGA-CODE-4 - Portable launcher
# Redirects all runtime env to ./data and keeps host untouched.
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$SCRIPT_DIR"
DATA_DIR="$ROOT_DIR/data"
HOME_DIR="$DATA_DIR/home"
CONFIG_HOME="$DATA_DIR/config"
APP_DATA="$DATA_DIR/app_data"
LOCAL_APP_DATA="$DATA_DIR/local_app_data"
CACHE_DIR="$DATA_DIR/cache"
LOG_DIR="$DATA_DIR/logs"
OC_DATA_DIR="$DATA_DIR/opencode"
ENV_FILE="$DATA_DIR/ai_settings.env"
SECURE_ENV="$ROOT_DIR/tools/secure_env.py"
TMP_FILE=""
trap 'rm -f "${TMP_FILE:-}"' EXIT

mkdir -p "$HOME_DIR" "$CONFIG_HOME" "$APP_DATA" "$LOCAL_APP_DATA" "$CACHE_DIR" "$LOG_DIR" "$OC_DATA_DIR" "$ROOT_DIR/tools"

export HOME="$HOME_DIR"
export USERPROFILE="$HOME_DIR"
export XDG_CONFIG_HOME="$CONFIG_HOME"
export XDG_DATA_HOME="$APP_DATA"
export XDG_CACHE_HOME="$CACHE_DIR"
export APPDATA="$APP_DATA"
export LOCALAPPDATA="$LOCAL_APP_DATA"
export PATH="$ROOT_DIR/tools:$PATH"

if [ -t 1 ]; then
  BOLD='\033[1m'; DIM='\033[2m'; CYAN='\033[36m'; GREEN='\033[32m'; RED='\033[31m'; YELLOW='\033[33m'; BLUE='\033[34m'; RESET='\033[0m';
else
  BOLD=''; DIM=''; CYAN=''; GREEN=''; RED=''; YELLOW=''; BLUE=''; RESET='';
fi

# ---------- crypto helpers ----------
ensure_crypto_tool() {
  [ -f "$SECURE_ENV" ] || {
    echo -e "${RED}[ERROR] Missing crypto helper: $SECURE_ENV${RESET}"
    exit 1
  }
}

prompt_master_password() {
  if [ -n "${MEGA_MASTER_PASSWORD:-}" ]; then
    MASTER_PASSWORD="$MEGA_MASTER_PASSWORD"
    return 0
  fi
  echo -e "${YELLOW}[~] Digite a Master Password para proteger o arquivo de credenciais.${RESET}"
  read -s -r MASTER_PASSWORD
  echo
  [ -n "$MASTER_PASSWORD" ] || { echo -e "${RED}[ERROR] Master Password vazia.${RESET}"; exit 1; }
}

load_encrypted_settings() {
  if [ ! -f "$ENV_FILE" ]; then
    return 0
  fi

  ensure_crypto_tool
  prompt_master_password

  # Temporario dentro de data/, com umask 077; removido logo apos o uso (e no trap EXIT).
  # A senha vai por variavel de ambiente so deste processo, nunca por argumento (visivel no ps).
  TMP_FILE="$(mktemp "$DATA_DIR/.settings.XXXXXX")"
  MEGA_SECURE_ENV_PASSWORD="$MASTER_PASSWORD" python3 "$SECURE_ENV" --decrypt --input "$ENV_FILE" --output "$TMP_FILE" || {
    echo -e "${RED}[ERROR] Falha ao descriptografar $ENV_FILE${RESET}"
    exit 1
  }

  if [ -s "$TMP_FILE" ]; then
    set -a
    . "$TMP_FILE"
    set +a
  fi

  rm -f "$TMP_FILE"
  TMP_FILE=""
}

save_encrypted_settings() {
  ensure_crypto_tool
  prompt_master_password

  TMP_FILE="$(mktemp "$DATA_DIR/.settings.XXXXXX")"
  {
    echo "# MEGA-CODE-4 settings"
    printf 'COARENA_API_KEY=%q\n' "${COARENA_API_KEY:-}"
    printf 'COARENA_BASE_URL=%q\n' "${COARENA_BASE_URL:-https://api.coarena.example/v1}"
    printf 'COARENA_MODEL=%q\n' "${COARENA_MODEL:-Fable-5}"
    printf 'AI_PROVIDER=%q\n' "${AI_PROVIDER:-coarena}"
    printf 'OPENCODE_MODEL=%q\n' "${OPENCODE_MODEL:-coarena/Fable-5}"
    printf 'MCP_HEXSTRIKE=%q\n' "${MCP_HEXSTRIKE:-0}"
    printf 'MCP_CYBERSTRIKE=%q\n' "${MCP_CYBERSTRIKE:-0}"
  } > "$TMP_FILE"

  MEGA_SECURE_ENV_PASSWORD="$MASTER_PASSWORD" python3 "$SECURE_ENV" --encrypt --input "$TMP_FILE" --output "$ENV_FILE" || {
    echo -e "${RED}[ERROR] Falha ao cifrar credenciais.${RESET}"
    rm -f "$TMP_FILE"
    TMP_FILE=""
    exit 1
  }
  chmod 600 "$ENV_FILE" 2>/dev/null || true
  rm -f "$TMP_FILE"
  TMP_FILE=""
}

ensure_coarena_defaults() {
  export COARENA_BASE_URL="${COARENA_BASE_URL:-https://api.coarena.example/v1}"
  export COARENA_MODEL="${COARENA_MODEL:-Fable-5}"
  export COARENA_API_KEY="${COARENA_API_KEY:-}"
  export AI_PROVIDER="${AI_PROVIDER:-coarena}"
  export OPENCODE_MODEL="${OPENCODE_MODEL:-coarena/${COARENA_MODEL}}"
  export MCP_HEXSTRIKE="${MCP_HEXSTRIKE:-0}"
  export MCP_CYBERSTRIKE="${MCP_CYBERSTRIKE:-0}"
}

ascii_banner() {
  echo -e "${CYAN}"
  echo "  __  __   ___   ____   ____   _   _   ____  _____  ____   ____   ____  "
  echo " |  \\/  | / _ \\ / ___| / ___| | | | | / ___|| ____|/ ___| / ___||  _ \\ "
  echo " | |\\/| || | | |\\___ \\| |     | |_| | \\___ \\|  _|  \\___ \\| |    | |_) |"
  echo " | |  | || |_| | ___) | |___  |  _  |  ___) | |___  ___) | |___ |  __/ "
  echo " |_|  |_| \\___/ |____/ \\_____| |_| |_| |____/ |_____|____/ \\_____|_|    "
  echo -e "     ${BOLD}MEGA-CODE-4${RESET}${CYAN}"
  echo "     Portable Cyber Coding Agent"
  echo -e "${RESET}"
}

usage() {
  echo "Uso: ./start.sh [--dir PROJECT] [--setup] [--quick] [opencode args...]"
  echo ""
  echo "  --dir PROJECT   trabalha em outra pasta"
  echo "  --setup         configura Coarena e sai"
  echo "  --quick         inicia imediatamente"
  echo "  --help          mostra ajuda"
}

PROJECT_DIR="$PWD"
SETUP_ONLY=0
QUICK_MODE=0
PASS_ARGS=()

while [ $# -gt 0 ]; do
  case "$1" in
    --dir)
      [ -n "${2:-}" ] || { echo -e "${RED}[ERROR] --dir precisa de um caminho${RESET}"; exit 1; }
      PROJECT_DIR="$2"
      shift 2
      ;;
    --dir=*)
      PROJECT_DIR="${1#*=}"
      shift
      ;;
    --setup)
      SETUP_ONLY=1
      shift
      ;;
    --quick)
      QUICK_MODE=1
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      PASS_ARGS+=("$1")
      shift
      ;;
  esac
done

[ -d "$PROJECT_DIR" ] || { echo -e "${RED}[ERROR] Diretório do projeto não encontrado: $PROJECT_DIR${RESET}"; exit 1; }
PROJECT_DIR="$(cd "$PROJECT_DIR" && pwd)"

# Load any encrypted settings first; if the file doesn't exist, prompt the user to create it.
load_encrypted_settings
ensure_coarena_defaults

if [ ! -f "$ENV_FILE" ]; then
  echo -e "${YELLOW}[~] Nenhuma configuração cifrada encontrada. Configure a Coarena para continuar.${RESET}"
  prompt_master_password
  read -r -p "  URL da Coarena (ex.: https://api.coarena.example/v1): " COARENA_BASE_URL
  COARENA_BASE_URL="${COARENA_BASE_URL:-https://api.coarena.example/v1}"
  read -s -r -p "  Chave da API da Coarena (nao aparece ao digitar): " COARENA_API_KEY
  echo
  read -r -p "  Modelo da Coarena (ex.: Fable-5): " COARENA_MODEL
  COARENA_MODEL="${COARENA_MODEL:-Fable-5}"
  AI_PROVIDER="coarena"
  OPENCODE_MODEL="coarena/${COARENA_MODEL}"
  MCP_HEXSTRIKE=0
  MCP_CYBERSTRIKE=0
  save_encrypted_settings
fi

# ---------- resolve OpenCode binary ----------
OS_NAME="$(uname -s | tr '[:upper:]' '[:lower:]')"
ARCH="$(uname -m)"
case "$OS_NAME" in
    linux) PLATFORM="linux" ;;
    darwin) PLATFORM="darwin" ;;
    *)
        echo -e "${RED}[ERROR] Sistema operacional não suportado: $OS_NAME${RESET}"
        exit 1
        ;;
esac

case "$ARCH" in
    x86_64|amd64) NODE_ARCH="x64" ;;
    arm64|aarch64) NODE_ARCH="arm64" ;;
    *)
        echo -e "${RED}[ERROR] Arquitetura não suportada: $ARCH${RESET}"
        exit 1
        ;;
esac

OC_BIN="$ROOT_DIR/engine/opencode-${PLATFORM}-${NODE_ARCH}/opencode"
[ -x "$OC_BIN" ] || {
  echo -e "${RED}[ERROR] OpenCode engine não encontrado em $OC_BIN${RESET}"
  exit 1
}

# ---------- render opencode config ----------
# O schema do OpenCode ainda NAO foi validado (ver docs/IMPLEMENTATION_STATUS.md).
# A chave de API e escrita em texto claro neste arquivo (permissao 0600): limitacao conhecida.
# HexStrike fica sempre desativado; os valores vem do ambiente, nunca de texto interpolado.
python3 - "$HOME_DIR/.opencode.json" "$OC_DATA_DIR" <<'PYCFG'
import json, os, sys

out, data_dir = sys.argv[1], sys.argv[2]
model = os.environ.get("COARENA_MODEL", "Fable-5")
cfg = {
    "data": {"directory": data_dir},
    "providers": {
        "coarena": {
            "apiKey": os.environ.get("COARENA_API_KEY", ""),
            "baseURL": os.environ.get("COARENA_BASE_URL", "https://api.coarena.example/v1"),
            "models": [model],
        }
    },
    "agents": {"mega": {"model": "coarena/" + model}},
    "mcp": {
        "lazyLoad": True,
        "servers": {
            "hexstrike": {"enabled": False, "host": "127.0.0.1", "port": 8889},
            "cyberstrike": {
                "enabled": os.environ.get("MCP_CYBERSTRIKE", "0") == "1",
                "host": "127.0.0.1",
                "port": 8890,
            },
        },
    },
}
fd = os.open(out, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
with os.fdopen(fd, "w", encoding="utf-8") as handle:
    json.dump(cfg, handle, indent=2)
PYCFG
chmod 600 "$HOME_DIR/.opencode.json" 2>/dev/null || true

ascii_banner

echo -e "${BLUE}=========================================================${RESET}"
echo -e "  ${BOLD}MEGA-CODE-4${RESET} ${DIM}- Portable Cyber Coding Agent${RESET}"
echo -e "${BLUE}=========================================================${RESET}"
echo -e "  ${BOLD}Engine${RESET}  : ${GREEN}$(basename "$OC_BIN")${RESET}"
echo -e "  ${BOLD}Model${RESET}   : ${GREEN}${COARENA_MODEL:-Fable-5}${RESET}"
echo -e "  ${BOLD}Project${RESET} : ${GREEN}${PROJECT_DIR}${RESET}"
echo -e "  ${BOLD}Data${RESET}    : ${DIM}${DATA_DIR}${RESET}"
echo -e "  ${BOLD}MCP${RESET}     : ${DIM}HexStrike desativado | CyberStrike ${MCP_CYBERSTRIKE:-0} (configurado, nao verificado)${RESET}"
echo -e "${BLUE}=========================================================${RESET}"

if [ "$SETUP_ONLY" -eq 1 ]; then
  echo -e "${GREEN}[OK] Configuração salva em $ENV_FILE${RESET}"
  exit 0
fi

echo ""
echo -e "  ${CYAN}[~] Iniciando OpenCode...${RESET}"
cd "$PROJECT_DIR" || exit 1
"$OC_BIN" "${PASS_ARGS[@]+"${PASS_ARGS[@]}"}"
STATUS=$?

echo ""
echo -e "  ${DIM}Dados da sessão: $OC_DATA_DIR${RESET}"
echo -e "  ${DIM}Código de saída: $STATUS${RESET}"
exit $STATUS
