# MEGA-CODE-4 — status real de implementação

Última revisão: 2026-11-16.

## Resultado da auditoria

**Este repositório ainda não está pronto para ser considerado funcional ou seguro para uso operacional.** Os arquivos atuais contêm uma base documental/prototípica, mas não uma entrega completa do agente.

| Componente | Estado verificado | O que falta |
|---|---|---|
| Engine OpenCode | Ausente neste repositório | O launcher procura binários em `engine/`, mas a árvore atual não contém esse diretório nem os executáveis. |
| Launcher Linux/macOS | Corrigido e testado só com engine falso | Fluxo de senha, temporários e configuração revisado e testado em Linux com um engine de mentira. Não foi testado com o OpenCode real nem em macOS. |
| Launcher Windows | Incompleto | `START.bat` chama rotinas que não existem (`ask_key`, `verify_key`, `pick_model`, `finalize_native` e outras) e cita `tools/build_engine.sh`, que não está no repositório. Precisa ser reescrito. |
| Coarena | Não validada | Endpoint e nomes de modelos são exemplos; confirmar URL, modelo e esquema de configuração com a Coarena. |
| Cifragem de credenciais | Corrigida e testada | `tools/secure_env.py` lê a senha por variável de ambiente do processo filho ou `getpass`; a opção `--password` foi removida. Ainda existe um arquivo temporário em texto claro (em `data/`, permissão 0600, removido logo após o uso) e a chave de API é gravada em texto claro em `data/home/.opencode.json` (0600). |
| MCP router | Classificador apenas | `tools/mcp_router.py` imprime sugestões JSON. Não inicia MCPs, não faz lazy loading integrado ao OpenCode e não controla disponibilidade. |
| HexStrike AI | Não implementado/validado | Há apenas uma referência de configuração de exemplo. O launcher agora gera a configuração com HexStrike sempre desativado. |
| CyberStrike | Não implementado/validado | Há referências de configuração de exemplo, sem conectores reais confirmados. Os nomes de pacotes MCP não foram verificados e não devem ser executados como estão. |
| Dashboard | Corrigido e testado localmente | A rota `/api/token` foi removida; a API exige Bearer token; arquivos estáticos são públicos em `127.0.0.1`; o status MCP/modelo é `unknown` (não há health check real). |
| Dockerfile | Não é sandbox de ferramentas | Executa apenas um servidor HTTP estático (`python -m http.server`) sem a autenticação do dashboard Node; não instala, inicia nem isola OpenCode, HexStrike ou CyberStrike. |

## Alterações desta revisão

- Dashboard: remoção da rota que devolvia o token; autenticação Bearer só na API; comparação de token por hash; bloqueio de path traversal, byte nulo e symlink fora de `tools/web`; apenas GET/HEAD; sem badges "ON" fixos; front-end com `textContent`.
- `secure_env.py`: senha fora do argumento de linha de comando; arquivos gravados com permissão 0600; erro genérico para senha incorreta ou arquivo adulterado.
- `start.sh`: chave de API lida sem eco; temporários em `data/` com `umask 077` e limpeza em `trap`; `printf %q` ao gravar as configurações; `.opencode.json` gerado com `json.dump`; HexStrike sempre desativado; token do dashboard não é mais impresso; expansão segura de array vazio com `set -u`.

## Testes executados nesta revisão

Ambiente: Linux (container), Python 3 com `cryptography` 50.0.2, Node.js v22.23.4, bash. Execução manual, sem suíte automatizada.

- `secure_env.py`: cifrar/decifrar com a mesma senha (ok); senha errada (falha, código 1); arquivo adulterado (falha, código 1); `--password` rejeitado como argumento desconhecido; arquivos gerados com permissão 600.
- `start.sh` com um engine falso: configuração inicial, segunda execução carregando a configuração cifrada, senha errada (código 1), repasse de argumentos com espaço, código de saída do engine preservado, nenhum temporário restante em `data/`, `.opencode.json` com JSON válido e chave com aspas/`$`/espaço preservada, HexStrike desativado.
- Dashboard: `/` e `/app.js` retornam 200; `/api/token` não existe mais (401 sem token, 404 com token); `/api/health` retorna 401 sem token, com token errado e com token de outro tamanho, e 200 com o token certo; tentativas de path traversal retornam 403/404; POST retorna 405; symlink para fora de `tools/web` retorna 404; token vindo de `MEGA_DASHBOARD_TOKEN` não aparece no log.

## Não testado / pendente

- Execução com o engine OpenCode real (ele não está no repositório) e validação do schema de configuração.
- macOS, Windows e bash anterior à 4.4 (a correção do array vazio não foi reproduzida em bash antigo).
- Navegador: o front-end do dashboard (campo de token e badges) foi escrito e o servidor foi testado por `curl`, mas a página não foi aberta num navegador.
- Cifragem: o formato do arquivo não é versionado e a senha ainda passa por variável de ambiente do processo filho; um arquivo temporário em texto claro ainda é criado durante carga e gravação.
- Visibilidade: o repositório está **público**, mas `docs/CLAUDE_CODE_PROMPT.md` e `docs/CLAUDE_CODE_SAFE_IMPLEMENTATION_PROMPT.md` ainda dizem que ele é privado. Esses textos não foram alterados nesta revisão.

## CyberStrike e HexStrike: decisão de implementação

- **CyberStrike:** pode ser integrado futuramente para tarefas defensivas de repositório, como revisão de código e dependências, depois de verificar a documentação e a origem oficial dos servidores MCP. Não há integração funcional neste commit.
- **HexStrike AI:** não será iniciado automaticamente nem roteado a partir de texto livre para reconhecimento/varredura de alvos. A configuração existente é apenas referência e está desativada. Uma integração futura deve ser opt-in, limitada a escopo autorizado e validada em sandbox antes do uso.
- O roteador atual não é uma barreira de segurança, autorização ou controle de acesso.
- O `systemPrompt` em `opencode.jsonc` ainda manda usar HexStrike para "scan de rede", o que contradiz esta decisão. Essa inconsistência não foi corrigida nesta revisão.

## Próximos requisitos antes de declarar pronto

1. Definir e testar a versão compatível do engine e a instalação verificável de seus binários.
2. Reescrever o `START.bat` e testar em Windows; testar o launcher Linux/macOS com o engine real.
3. Validar o formato de configuração e o endpoint/modelo fornecidos pela Coarena.
4. Eliminar o arquivo temporário em texto claro e a chave em texto claro no `.opencode.json`, se o engine permitir.
5. Só integrar MCPs existentes depois de validar projeto upstream, transporte, argumentos e permissões; remover `npx -y` e fixar versões.
6. Fazer o dashboard refletir health checks reais.
7. Substituir o Dockerfile de exemplo por uma configuração de isolamento realmente testada, sem mounts do host por padrão.
8. Adicionar testes automatizados e CI antes de rotular uma versão como pronta.

## Conclusão

O repositório recebeu correções de segurança pontuais, mas continua sendo um protótipo. Não use os launchers com credenciais reais nem habilite os MCPs de exemplo até a conclusão dos itens acima.
