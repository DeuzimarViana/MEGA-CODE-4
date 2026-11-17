#!/usr/bin/env python3
"""Launcher portatil do MEGA-CODE-4 (Windows, Linux e macOS).

Mesma logica do start.sh, em Python para funcionar no Windows sem depender de
rotinas de batch:
  * redireciona HOME/APPDATA/XDG_* para ./data;
  * guarda as configuracoes cifradas (AES-256-GCM + PBKDF2) em data/ai_settings.env,
    cifrando e decifrando EM MEMORIA (sem arquivo temporario em texto claro);
  * a senha mestra e a chave de API sao lidas sem eco (getpass) e nunca vao
    para argumentos de linha de comando;
  * gera data/config/opencode/opencode.json (formato oficial do OpenCode, validado com a
    1.19.5) a partir do opencode.jsonc, SEM a chave de API: ela vai para o engine pela
    variavel de ambiente COARENA_API_KEY ({env:COARENA_API_KEY} na configuracao);
  * aponta a pasta temporaria do engine (TMPDIR/TEMP/TMP) para ./data/tmp;
  * usa o engine em engine/opencode-<sistema>-<arq>/ ou, se nao existir, o `opencode` do PATH;
  * executa o engine OpenCode e devolve o codigo de saida dele.

Limitacoes conhecidas: so foi testado em Linux; a chave continua visivel ao engine (e a
quem puder ler o ambiente do processo) enquanto ele roda.
"""
import getpass
import os
import platform
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_opencode_config  # noqa: E402
import secure_env  # noqa: E402

ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_URL = "https://api.coarena.example/v1"
DEFAULT_MODEL = "Fable-5"
SETTING_KEYS = (
    "COARENA_API_KEY", "COARENA_BASE_URL", "COARENA_MODEL",
    "AI_PROVIDER", "OPENCODE_MODEL", "MCP_HEXSTRIKE", "MCP_CYBERSTRIKE",
)

USAGE = """Uso: launch.py [--dir PROJETO] [--setup] [--quick] [argumentos do opencode...]

  --dir PROJETO   trabalha em outra pasta
  --setup         (re)configura a Coarena e sai
  --quick         aceito por compatibilidade com o start.sh (sem efeito)
  --help          mostra esta ajuda
"""


def fail(message, code=1):
    print(f"[ERROR] {message}", file=sys.stderr)
    sys.exit(code)


def engine_candidates(root, system, machine):
    """Caminhos possiveis do engine, em ordem de preferencia (funcao pura, testavel)."""
    system = system.lower()
    machine = machine.lower()
    if system not in ("windows", "linux", "darwin"):
        raise ValueError(f"Sistema operacional nao suportado: {system}")
    if machine in ("x86_64", "amd64", "x64"):
        arch = "x64"
    elif machine in ("arm64", "aarch64"):
        arch = "arm64"
    else:
        raise ValueError(f"Arquitetura nao suportada: {machine}")
    exe = "opencode.exe" if system == "windows" else "opencode"
    return [Path(root) / "engine" / f"opencode-{system}-{arch}" / exe]


def find_engine(root):
    try:
        candidates = engine_candidates(root, platform.system(), platform.machine())
    except ValueError as exc:
        fail(str(exc))
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    # Fallback (como no START.bat antigo): qualquer engine/opencode-*/opencode[.exe]
    exe = candidates[0].name
    for found in sorted((Path(root) / "engine").glob(f"opencode-*/{exe}")):
        return found
    # Ultimo recurso: o `opencode` instalado no PATH (instalacao oficial feita pelo usuario).
    on_path = shutil.which("opencode")
    if on_path:
        print(f"[AVISO] Engine nao encontrado em engine/; usando o opencode do PATH: {on_path}", file=sys.stderr)
        return Path(on_path)
    fail(
        "OpenCode engine nao encontrado.\n"
        f"        Esperado: {candidates[0]}\n"
        "        Nem ha um `opencode` no PATH. O repositorio nao inclui os binarios;\n"
        "        instale o OpenCode por fonte oficial (opencode.ai) ou copie o binario para engine/."
    )


def get_master_password():
    password = os.environ.get("MEGA_MASTER_PASSWORD", "")
    if password:
        return password
    password = getpass.getpass("Master Password (protege o arquivo de credenciais): ")
    if not password:
        fail("Master Password vazia.")
    return password


def encrypt_bytes(data, password):
    if not secure_env.HAS_CRYPTOGRAPHY:
        fail("O pacote 'cryptography' e necessario. Instale: pip install cryptography")
    salt = os.urandom(16)
    nonce = os.urandom(12)
    key = secure_env.derive_key(password, salt)
    return salt + nonce + secure_env.AESGCM(key).encrypt(nonce, data, None)


def decrypt_bytes(blob, password):
    if not secure_env.HAS_CRYPTOGRAPHY:
        fail("O pacote 'cryptography' e necessario. Instale: pip install cryptography")
    if len(blob) < 28:
        raise ValueError("Arquivo cifrado invalido ou corrompido.")
    salt, nonce, encrypted = blob[:16], blob[16:28], blob[28:]
    key = secure_env.derive_key(password, salt)
    try:
        return secure_env.AESGCM(key).decrypt(nonce, encrypted, None)
    except Exception:
        raise ValueError("Senha incorreta ou arquivo adulterado.")


def serialize_settings(settings):
    # shlex.quote gera texto valido para o `source` do start.sh (mesmo formato de arquivo).
    lines = ["# MEGA-CODE-4 settings"]
    for key in SETTING_KEYS:
        lines.append(f"{key}={shlex.quote(str(settings.get(key, '')))}")
    return ("\n".join(lines) + "\n").encode("utf-8")


def parse_settings(data):
    settings = {}
    for raw_line in data.decode("utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, raw_value = line.partition("=")
        key = key.strip()
        if key not in SETTING_KEYS:
            continue
        try:
            parts = shlex.split(raw_value)
        except ValueError:
            parts = [raw_value]
        settings[key] = parts[0] if parts else ""
    return settings


def prompt_new_settings():
    print("[~] Configure a Coarena (os valores abaixo sao exemplos; confirme com o provedor).")
    url = input(f"  URL da Coarena (ex.: {DEFAULT_URL}): ").strip() or DEFAULT_URL
    key = getpass.getpass("  Chave da API da Coarena (nao aparece ao digitar): ")
    model = input(f"  Modelo da Coarena (ex.: {DEFAULT_MODEL}): ").strip() or DEFAULT_MODEL
    return {
        "COARENA_API_KEY": key,
        "COARENA_BASE_URL": url,
        "COARENA_MODEL": model,
        "AI_PROVIDER": "coarena",
        "OPENCODE_MODEL": f"coarena/{model}",
        "MCP_HEXSTRIKE": "0",
        "MCP_CYBERSTRIKE": "0",
    }


def parse_args(argv):
    opts = {"dir": None, "setup": False, "passthrough": []}
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg in ("--help", "-h"):
            print(USAGE)
            sys.exit(0)
        elif arg == "--dir":
            if i + 1 >= len(argv) or not argv[i + 1]:
                fail("--dir precisa de um caminho")
            opts["dir"] = argv[i + 1]
            i += 2
            continue
        elif arg.startswith("--dir="):
            opts["dir"] = arg.split("=", 1)[1]
        elif arg == "--setup":
            opts["setup"] = True
        elif arg == "--quick":
            pass
        else:
            opts["passthrough"].append(arg)
        i += 1
    return opts


def main(argv):
    opts = parse_args(argv)
    project_dir = Path(opts["dir"]).resolve() if opts["dir"] else Path.cwd()
    if not project_dir.is_dir():
        fail(f"Diretorio do projeto nao encontrado: {project_dir}")

    data_dir = ROOT_DIR / "data"
    dirs = {
        "home": data_dir / "home",
        "config": data_dir / "config",
        "app_data": data_dir / "app_data",
        "local_app_data": data_dir / "local_app_data",
        "cache": data_dir / "cache",
        "logs": data_dir / "logs",
        "state": data_dir / "state",
        "tmp": data_dir / "tmp",
    }
    for directory in dirs.values():
        directory.mkdir(parents=True, exist_ok=True)
    env_file = data_dir / "ai_settings.env"

    # ---- configuracoes cifradas ----
    if opts["setup"] or not env_file.exists():
        password = get_master_password()
        settings = prompt_new_settings()
        secure_env.write_private(str(env_file), encrypt_bytes(serialize_settings(settings), password))
        print(f"[OK] Configuracao salva em {env_file}")
        if opts["setup"]:
            return 0
    else:
        password = get_master_password()
        try:
            settings = parse_settings(decrypt_bytes(env_file.read_bytes(), password))
        except ValueError as exc:
            fail(f"Falha ao descriptografar {env_file}: {exc}")

    engine = find_engine(ROOT_DIR)
    model = settings.get("COARENA_MODEL") or DEFAULT_MODEL
    try:
        cfg = gen_opencode_config.build_config(
            ROOT_DIR / "opencode.jsonc", settings.get("COARENA_BASE_URL") or DEFAULT_URL, model)
        gen_opencode_config.write_config(dirs["config"] / "opencode" / "opencode.json", cfg)
    except (OSError, ValueError, KeyError) as exc:
        fail(f"Nao foi possivel gerar a configuracao do OpenCode: {exc}")

    # ---- ambiente portatil do processo filho ----
    env = os.environ.copy()
    env.pop("MEGA_MASTER_PASSWORD", None)  # nao herdar a senha no engine
    env.update({
        "HOME": str(dirs["home"]),
        "USERPROFILE": str(dirs["home"]),
        "XDG_CONFIG_HOME": str(dirs["config"]),
        "XDG_DATA_HOME": str(dirs["app_data"]),
        "XDG_CACHE_HOME": str(dirs["cache"]),
        "XDG_STATE_HOME": str(dirs["state"]),
        "TMPDIR": str(dirs["tmp"]),
        "TEMP": str(dirs["tmp"]),
        "TMP": str(dirs["tmp"]),
        "APPDATA": str(dirs["app_data"]),
        "LOCALAPPDATA": str(dirs["local_app_data"]),
        # Referenciada como {env:COARENA_API_KEY} na configuracao; nunca gravada em disco.
        "COARENA_API_KEY": settings.get("COARENA_API_KEY", ""),
        "PATH": str(ROOT_DIR / "tools" / "bin") + os.pathsep + env.get("PATH", ""),
    })

    print("=" * 57)
    print("  MEGA-CODE-4 - Portable Cyber Coding Agent")
    print("=" * 57)
    print(f"  Engine  : {engine.name}")
    print(f"  Model   : {model}")
    print(f"  Project : {project_dir}")
    print(f"  Data    : {data_dir}")
    print("  MCP     : todos desativados (nenhum e habilitado pelo launcher)")
    print("=" * 57)
    print("\n  [~] Iniciando OpenCode...\n", flush=True)

    try:
        status = subprocess.call([str(engine)] + opts["passthrough"], cwd=str(project_dir), env=env)
    except KeyboardInterrupt:
        status = 130
    except OSError as exc:
        fail(f"Nao foi possivel executar o engine: {exc}")

    print(f"\n  Dados da sessao: {dirs['app_data'] / 'opencode'}")
    print(f"  Codigo de saida: {status}")
    return status


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
