# MEGA-CODE-4 — status real de implementação

Última revisão: 2026-11-17.

## Resultado

O repositório agora é uma distribuição executável: engine empacotado, launchers com
rotinas completas e provedor NVIDIA NIM validado de ponta a ponta. Coarena permanece
como exemplo não validado.

| Componente | Estado | Observação |
|---|---|---|
| Engine OpenCode | Incluído | 5 binários em `engine/` (Linux x64/arm64, Windows x64, macOS x64/arm64) |
| Launcher Linux/macOS | Funcional | Setup, verificação de chave, geração de `.opencode.json` e launch. Testado com engine real e NVIDIA NIM. |
| Launcher Windows | Completo | Rotinas de setup, verificação, modelos e config reescritas; validação estática de labels e chamadas. Não executado em Windows real. |
| NVIDIA NIM | Validado | HTTP 200 na verificação de 1 token; modelo padrão `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning`. |
| Coarena | Placeholder | URL/modelo de exemplo; não testado. |
| Credenciais | Texto claro 0600 | `data/ai_settings.env` e `data/home/.opencode.json`, gitignored. `secure_env.py` opcional. |
| MCP router | Classificador | Sugere nomes em JSON; não inicia MCPs. |
| HexStrike / CyberStrike | Desativados | Nenhuma integração automática; config de exemplo sem ativação. |
| Dashboard | Funcional | Bearer token, sem `/api/token`, CSP e bloqueio de path traversal. |
| Dockerfile | Exemplo | Servidor HTTP estático; não é sandbox. |

## Testes executados nesta revisão

- `bash -n start.sh`: sintaxe OK.
- `./start.sh -p "Reply with exactly: PORTABLE_OK"`: exit 0 e resposta `PORTABLE_OK`.
- Verificação NVIDIA: HTTP 200 no modelo padrão.
- `START.bat`: todos os rótulos chamados por `call`/`goto` estão definidos; sem comandos soltos.
- Python: `py_compile` em `tools/*.py`; Node: `node --check` em `tools/*.js`.
- Scan de segredos: limpo no HEAD e no histórico.

## Pendente

- Executar `START.bat` em Windows real.
- Testar em macOS.
- Validar Coarena com endpoint e modelo reais.
- Substituir o Dockerfile por uma configuração de isolamento testada, se necessário.
