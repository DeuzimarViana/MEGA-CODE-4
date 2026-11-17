# MEGA-CODE-4 — Notas de segurança

## Portabilidade

Os launchers redirecionam `HOME`, `XDG_*`, `APPDATA` e `LOCALAPPDATA` para `data/`, mas
isso não garante “zero rastros”: sistema operacional, swap, logs, antivírus, backup e
sincronização podem registrar ou copiar informações.

## Credenciais

O launcher grava chaves em texto claro em `data/ai_settings.env` e
`data/home/.opencode.json`, ambos com permissão `600` e ignorados pelo Git. Isso é
necessário para que o engine leia a configuração. O repositório não contém credenciais.

`tools/secure_env.py` (AES-GCM + PBKDF2-HMAC-SHA256) continua disponível para cifrar e
decifrar arquivos manualmente, mas não é exigido pelo launcher. Nunca passe senhas por
argumento de linha de comando.

## Provedores

NVIDIA NIM é o provedor validado. Coarena é apenas um exemplo. O endpoint `/v1/models`
é público: `403` indica chave inválida e `404` indica modelo não habilitado para a conta.

## Dashboard

O servidor escuta em `127.0.0.1:3000`. A API `/api/*` exige Bearer token; a rota
`/api/token` foi removida. Há CSP, bloqueio de path traversal, byte nulo e symlinks,
além de aceitar apenas GET/HEAD. Não exponha a porta em outras interfaces.

## MCP e ferramentas de segurança

HexStrike e CyberStrike permanecem desativados. `mcp_router.py` apenas classifica texto
e imprime sugestões em JSON; não inicia serviços nem encaminha comandos. Não ative
ferramentas de varredura, reconhecimento ou exploração sem autorização e escopo definidos.

## Container

O `Dockerfile` atual inicia somente um servidor HTTP estático para os arquivos do
painel. Não é uma sandbox para execução de código ou ferramentas MCP.
