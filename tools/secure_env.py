#!/usr/bin/env python3
"""Cifra/decifra o arquivo de configuracao com AES-256-GCM + PBKDF2-HMAC-SHA256.

A senha NUNCA vem por argumento de linha de comando (ficaria visivel no `ps`).
Ela e lida da variavel de ambiente MEGA_SECURE_ENV_PASSWORD (definida apenas
para o processo filho, pelo launcher) ou, se ausente, pedida via getpass.
"""
import argparse
import getpass
import hashlib
import os
import sys
from pathlib import Path

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    HAS_CRYPTOGRAPHY = True
except Exception:
    HAS_CRYPTOGRAPHY = False

PASSWORD_ENV = "MEGA_SECURE_ENV_PASSWORD"


def derive_key(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000, dklen=32)


def get_password() -> str:
    password = os.environ.get(PASSWORD_ENV, "")
    if not password:
        password = getpass.getpass("Master Password: ")
    if not password:
        raise ValueError("Senha vazia.")
    return password


def write_private(path: str, data: bytes) -> None:
    """Grava o arquivo ja com permissao 0600 (sem janela com permissao ampla)."""
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
    finally:
        try:
            os.chmod(path, 0o600)
        except Exception:
            pass


def encrypt_file(input_path: str, output_path: str, password: str) -> None:
    if not HAS_CRYPTOGRAPHY:
        raise RuntimeError("cryptography is required. Install: pip install cryptography")

    data = Path(input_path).read_bytes()
    salt = os.urandom(16)
    nonce = os.urandom(12)
    key = derive_key(password, salt)
    ciphertext = AESGCM(key).encrypt(nonce, data, None)
    write_private(output_path, salt + nonce + ciphertext)


def decrypt_file(input_path: str, output_path: str, password: str) -> None:
    if not HAS_CRYPTOGRAPHY:
        raise RuntimeError("cryptography is required. Install: pip install cryptography")

    blob = Path(input_path).read_bytes()
    if len(blob) < 28:
        raise ValueError("Arquivo cifrado invalido ou corrompido.")

    salt = blob[:16]
    nonce = blob[16:28]
    encrypted = blob[28:]
    key = derive_key(password, salt)
    try:
        plain = AESGCM(key).decrypt(nonce, encrypted, None)
    except Exception:
        raise ValueError("Senha incorreta ou arquivo adulterado.")
    write_private(output_path, plain)


def main() -> int:
    parser = argparse.ArgumentParser(description="Encrypt/decrypt settings file using AES-256-GCM with PBKDF2")
    parser.add_argument("--encrypt", action="store_true")
    parser.add_argument("--decrypt", action="store_true")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    if args.encrypt and args.decrypt:
        parser.error("Escolha apenas uma operacao: --encrypt ou --decrypt")
    if not args.encrypt and not args.decrypt:
        parser.error("Informe --encrypt ou --decrypt")

    try:
        password = get_password()
        if args.encrypt:
            encrypt_file(args.input, args.output, password)
        else:
            decrypt_file(args.input, args.output, password)
    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
