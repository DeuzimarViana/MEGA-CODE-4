#!/usr/bin/env python3
"""Gera a configuracao do OpenCode (opencode.json) para os launchers (start.sh e launch.py).

Junta as REGRAS do projeto (opencode.jsonc: permissoes, agente, share, MCPs desativados) com o
provedor/endpoint/modelo escolhidos pelo usuario. O arquivo gerado NAO contem a chave de API:
ela e referenciada como {env:COARENA_API_KEY} e entregue ao engine por variavel de ambiente.
Os MCPs continuam todos desativados; este script nunca habilita nenhum.

Uso: gen_opencode_config.py --template opencode.jsonc --out data/config/opencode/opencode.json
                            --base-url https://... --model NOME
"""
import argparse
import json
import sys
from pathlib import Path

PROVIDER_ID = "coarena"


def strip_jsonc(text):
    """Remove comentarios // e /* */ sem mexer em strings (URLs como https://... sao preservadas)."""
    out = []
    i, n = 0, len(text)
    in_string = False
    while i < n:
        ch = text[i]
        if in_string:
            out.append(ch)
            if ch == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if ch == '"':
                in_string = False
            i += 1
            continue
        if ch == '"':
            in_string = True
            out.append(ch)
            i += 1
        elif ch == "/" and i + 1 < n and text[i + 1] == "/":
            while i < n and text[i] != "\n":
                i += 1
        elif ch == "/" and i + 1 < n and text[i + 1] == "*":
            end = text.find("*/", i + 2)
            i = n if end == -1 else end + 2
        else:
            out.append(ch)
            i += 1
    return "".join(out)


def load_jsonc(path):
    return json.loads(strip_jsonc(Path(path).read_text(encoding="utf-8")))


def validate_inputs(base_url, model):
    if not (base_url.startswith("https://") or base_url.startswith("http://")):
        raise ValueError("A URL da Coarena precisa comecar com https:// (ou http://).")
    if any(c in base_url for c in "\r\n\t "):
        raise ValueError("A URL da Coarena nao pode ter espacos ou quebras de linha.")
    if not model or any(c in model for c in "\r\n\t"):
        raise ValueError("Modelo vazio ou com caracteres invalidos.")


def build_config(template_path, base_url, model):
    validate_inputs(base_url, model)
    rules = load_jsonc(template_path)
    if "provider" in rules or "model" in rules:
        raise ValueError("o arquivo de regras nao deve definir provider/model (isso vem do launcher)")
    cfg = {
        "$schema": rules.pop("$schema", "https://opencode.ai/config.json"),
        "model": f"{PROVIDER_ID}/{model}",
        "provider": {
            PROVIDER_ID: {
                "npm": "@ai-sdk/openai-compatible",
                "name": "Coarena",
                "options": {
                    "baseURL": base_url,
                    # A chave NAO e gravada aqui: o engine a le da variavel de ambiente.
                    "apiKey": "{env:COARENA_API_KEY}",
                },
                "models": {model: {"name": model}},
            }
        },
    }
    cfg.update(rules)
    # Garantia: este gerador nunca habilita MCP.
    for server in cfg.get("mcp", {}).values():
        server["enabled"] = False
    return cfg


def write_config(out_path, cfg):
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Gera opencode.json a partir do modelo opencode.jsonc")
    parser.add_argument("--template", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--model", required=True)
    args = parser.parse_args(argv)
    try:
        write_config(args.out, build_config(args.template, args.base_url, args.model))
    except (OSError, ValueError, KeyError) as exc:
        print(f"[ERROR] Nao foi possivel gerar a configuracao do OpenCode: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
