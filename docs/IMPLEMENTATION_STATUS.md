# MEGA-CODE-4 — status real de implementação

Última revisão: 2026-11-16 (terceira rodada de correções).

## Resultado da auditoria

**Este repositório ainda não está pronto para ser considerado funcional ou seguro para uso operacional.** Os arquivos atuais contêm uma base documental/prototípica, mas não uma entrega completa do agente.

| Componente | Estado verificado | O que falta |
|---|---|---|
| Engine OpenCode | Ausente neste repositório | O launcher procura binários em `engine/`, mas a árvore atual não contém esse diretório nem os executáveis. |
| Launcher Linux/macOS | Fluxo testado só com engine falso; **a config que ele gera é ignorada pelo OpenCode real** | Senha, temporários e geração de arquivo foram testados com um engine de mentira. Testando com o OpenCode 1.19.5 real, o `~/.opencode.json` que o `start.sh` gera **não é lido**: o engine procura `opencode.json[c]` na raiz do projeto ou em `$XDG_CONFIG_HOME/opencode/` e usa o schema `provider`, não `providers`. Falta gerar a configuração no formato oficial. Sem teste em macOS. |
| Launcher Windows | Reescrito, **não testado em Windows** | `START.bat` agora só localiza o Python e chama `tools/launch.py`, que tem a mesma lógica do `start.sh` (config cifrada em memória, senha e chave sem eco, `.opencode.json` com HexStrike desativado). O `launch.py` foi testado em Linux com engine falso; o próprio `START.bat` e o caminho `opencode-windows-x64\opencode.exe` nunca foram executados em Windows. O `.opencode.json` que ele gera também não é lido pelo OpenCode real (ver linha anterior). |
| Coarena | Não validada | Endpoint e nomes de modelos são placeholders; confirmar URL e modelos com a Coarena. O formato do provedor no `opencode.jsonc` (adaptador `@ai-sdk/openai-compatible`) foi validado com o OpenCode, mas nenhuma chamada real a um modelo foi feita. |
| `opencode.jsonc` | Validado só quanto ao formato | Reescrito no schema oficial; carrega sem erro no OpenCode 1.19.5 (Linux x64): provedor, modelos, agente `mega`, permissões e MCPs desativados. A versão anterior era **inválida** e o engine recusava carregá-la. Só tem efeito se estiver na raiz do projeto aberto ou em `$XDG_CONFIG_HOME/opencode/`; os launchers ainda não o instalam nesse local. |
| Cifragem de credenciais | Corrigida e testada | `tools/secure_env.py` lê a senha por variável de ambiente do processo filho ou `getpass`; a opção `--password` foi removida. No `start.sh` ainda existe um arquivo temporário em texto claro (em `data/`, permissão 0600, removido logo após o uso); o `launch.py` cifra e decifra em memória. Em ambos, a chave de API é gravada em texto claro em `data/home/.opencode.json` (0600), arquivo que o OpenCode real nem lê. |
| MCP router | Classificador apenas | `tools/mcp_router.py` imprime sugestões JSON. Não inicia MCPs, não faz lazy loading integrado ao OpenCode e não controla disponibilidade. |
| HexStrike AI | Não implementado/validado | Não há entrada de HexStrike no `opencode.jsonc`, nem regra de roteamento, e o prompt do agente diz que ele não faz parte do projeto. Os launchers ainda geram um `.opencode.json` com HexStrike desativado, mas esse arquivo é ignorado pelo engine real. |
| CyberStrike | Não implementado/validado | Há três entradas `mcp` no formato oficial (`type: local`, `enabled: false`); o OpenCode as lista como desativadas e não as executa. Sem conectores reais confirmados: os nomes de pacotes não foram verificados e não devem ser executados como estão. |
| Dashboard | Corrigido e testado localmente | A rota `/api/token` foi removida; a API exige Bearer token; arquivos estáticos são públicos em `127.0.0.1`; o status MCP/modelo é `unknown` (não há health check real). |
| Dockerfile | Não é sandbox de ferramentas | Executa apenas um servidor HTTP estático (`python -m http.server`) sem a autenticação do dashboard Node; não instala, inicia nem isola OpenCode, HexStrike ou CyberStrike. |

## Alterações desta revisão

### Terceira rodada

- `opencode.jsonc` reescrito no formato oficial do OpenCode: `provider` com o adaptador `@ai-sdk/openai-compatible` e `models` como objeto; chave via `{env:COARENA_API_KEY}` (não escrita no arquivo); agente `mega` com `prompt` único; `permission` com `edit`, `bash` e `webfetch` em `ask`; `share: disabled`; MCPs no formato `type`/`command`/`enabled`, todos desativados. Removidos: `providers`, `agents`, `routing`, `security`, `version`, `mcp.router`/`enabled`/`lazyLoad`/`defaultTimeoutMs` (o engine recusava ou ignorava), a entrada de HexStrike e o `npx -y`.
- `README.md`, `SECURITY.md`, `MCP_ROUTING.md` e este arquivo alinhados com o que foi validado.

### Segunda rodada

- `START.bat` reescrito: deixa de ter lógica própria (tinha rotinas inexistentes) e delega a `tools/launch.py`.
- `tools/launch.py` (novo): launcher multiplataforma; cifra/decifra as configurações em memória (sem arquivo temporário), lê senha e chave com `getpass`, gera `.opencode.json` com `json.dump`, preserva o código de saída do engine e não repassa `MEGA_MASTER_PASSWORD` ao engine. Usa o mesmo formato de `ai_settings.env` do `start.sh`.
- `opencode.jsonc` (depois substituído na terceira rodada): o prompt do agente não manda mais usar HexStrike para "scan de rede" e informa que ele está desativado; a regra de roteamento que ativava HexStrike por texto livre foi removida; avisos de que schema, sintaxe `${VAR:-padrão}` e pacotes `npx -y` não foram verificados.
- `CLAUDE_CODE_PROMPT.md` e `CLAUDE_CODE_SAFE_IMPLEMENTATION_PROMPT.md`: o aviso de acesso agora diz que o repositório é público; o segundo avisa que `mcp_manager.py` ainda não existe.
- `README.md` e `SECURITY.md` alinhados com os launchers.

### Primeira rodada

- Dashboard: remoção da rota que devolvia o token; autenticação Bearer só na API; comparação de token por hash; bloqueio de path traversal, byte nulo e symlink fora de `tools/web`; apenas GET/HEAD; sem badges "ON" fixos; front-end com `textContent`.
- `secure_env.py`: senha fora do argumento de linha de comando; arquivos gravados com permissão 0600; erro genérico para senha incorreta ou arquivo adulterado.
- `start.sh`: chave de API lida sem eco; temporários em `data/` com `umask 077` e limpeza em `trap`; `printf %q` ao gravar as configurações; `.opencode.json` gerado com `json.dump`; HexStrike sempre desativado; token do dashboard não é mais impresso; expansão segura de array vazio com `set -u`.

## Testes executados nesta revisão

Ambiente: Linux (container), Python 3 com `cryptography` 50.0.2, Node.js v22.23.4, bash. Execução manual, sem suíte automatizada.

- `secure_env.py`: cifrar/decifrar com a mesma senha (ok); senha errada (falha, código 1); arquivo adulterado (falha, código 1); `--password` rejeitado como argumento desconhecido; arquivos gerados com permissão 600.
- `start.sh` com um engine falso: configuração inicial, segunda execução carregando a configuração cifrada, senha errada (código 1), repasse de argumentos com espaço, código de saída do engine preservado, nenhum temporário restante em `data/`, `.opencode.json` com JSON válido e chave com aspas/`$`/espaço preservada, HexStrike desativado.
- Dashboard: `/` e `/app.js` retornam 200; `/api/token` não existe mais (401 sem token, 404 com token); `/api/health` retorna 401 sem token, com token errado e com token de outro tamanho, e 200 com o token certo; tentativas de path traversal retornam 403/404; POST retorna 405; symlink para fora de `tools/web` retorna 404; token vindo de `MEGA_DASHBOARD_TOKEN` não aparece no log.

### Testes da segunda rodada (`tools/launch.py`)

Mesmo ambiente (Linux, Python 3 + `cryptography` 50.0.2), com engine falso: primeira execução (configura, cifra e executa), segunda execução carregando a config, senha errada (código 1), arquivo `ai_settings.env` sem texto claro e com permissão 600, `.opencode.json` válido com chave contendo `"`, `$` e espaço, nenhum temporário em `data/`, `MEGA_MASTER_PASSWORD` não herdada pelo engine, `--setup`, `--dir` (existente e inexistente), `--help`, engine ausente (código 1), código de saída e argumentos com espaço preservados, **compatibilidade nos dois sentidos** entre `start.sh` e `launch.py` (um abre a config criada pelo outro) e seleção do caminho do engine para Windows/Linux/macOS e arquitetura x64/arm64 (função pura).

### Testes da terceira rodada (OpenCode real)

Engine: pacote npm `opencode-ai` 1.19.5, Linux x64, instalado numa pasta de teste, com `HOME`/`XDG_*`/`TMPDIR` isolados e chave falsa. Só configuração foi exercitada; nenhuma chamada a modelo.

- `.opencode.json` gerado pelos launchers (em `$HOME`): ignorado; o provedor `coarena` não aparece em `opencode debug config`.
- `opencode.jsonc` antigo na raiz do projeto: **recusado** (`Configuration is invalid`: `mcp.enabled`, `mcp.lazyLoad`, `mcp.defaultTimeoutMs` e `mcp.router` não são servidores MCP válidos).
- `opencode.jsonc` novo: carrega sem erro; `opencode models coarena` lista os 3 modelos; a chave aparece mascarada (`***`); `opencode debug agent mega` mostra o prompt e o modelo `coarena/Fable-5`; `opencode mcp list` mostra os 3 MCPs como `disabled`.
- Validação estrita: valores inválidos de `share` e `permission` são rejeitados, o que indica que o validador de fato checa essas chaves.
- Config no local global (`$XDG_CONFIG_HOME/opencode/opencode.jsonc`): lida a partir de outra pasta.
- Pasta temporária do engine: `/tmp/opencode` por padrão (fora de `data/`); vai para `$TMPDIR/opencode` quando `TMPDIR` é redirecionado.
- Permissões do agente: na lista resolvida, `edit`/`bash`/`webfetch` = `ask` aparecem depois da regra padrão `*` = `allow`; o comportamento interativo não foi exercitado.

## Não testado / pendente

- Execução completa com o engine OpenCode real (ele não está no repositório): só a validação da configuração foi feita, em Linux x64, sem chamada a modelo, sem a interface interativa e sem exercitar o efeito das permissões `ask`. Windows e macOS com o engine real continuam sem teste.
- **Windows**: o `START.bat` (detecção de `py -3`/`python`, repasse de argumentos, `pause` em código diferente de 0) e a execução de `launch.py` com `opencode.exe` nunca rodaram em Windows. Também sem teste em macOS e em bash anterior à 4.4.
- Navegador: o front-end do dashboard (campo de token e badges) foi escrito e o servidor foi testado por `curl`, mas a página não foi aberta num navegador.
- Cifragem: o formato do arquivo não é versionado e, no `start.sh`, a senha ainda passa por variável de ambiente do processo filho e um arquivo temporário em texto claro é criado durante carga e gravação (o `launch.py` não faz isso).
- Launchers: ainda geram o `.opencode.json` obsoleto (ignorado pelo engine). Falta instalar a configuração no formato oficial em `data/config/opencode/`, passar a chave por `{env:COARENA_API_KEY}`, definir `TMPDIR` dentro de `data/` e, opcionalmente, aceitar o `opencode` do PATH quando `engine/` não existir.

## CyberStrike e HexStrike: decisão de implementação

- **CyberStrike:** pode ser integrado futuramente para tarefas defensivas de repositório, como revisão de código e dependências, depois de verificar a documentação e a origem oficial dos servidores MCP. Não há integração funcional neste commit.
- **HexStrike AI:** não será iniciado automaticamente nem roteado a partir de texto livre para reconhecimento/varredura de alvos. Não há entrada de HexStrike na configuração. Uma integração futura deve ser opt-in, limitada a escopo autorizado e validada em sandbox antes do uso.
- O roteador atual não é uma barreira de segurança, autorização ou controle de acesso.

## Próximos requisitos antes de declarar pronto

1. Definir e testar a versão compatível do engine e a instalação verificável de seus binários.
2. Testar o `START.bat`/`launch.py` em Windows e os launchers Linux/macOS com o engine real.
3. Validar endpoint e modelos fornecidos pela Coarena (o formato do provedor já foi validado com o OpenCode 1.19.5).
4. Fazer os launchers gerarem a configuração no formato oficial, com a chave por `{env:...}` (sem gravá-la em texto claro), e eliminar o arquivo temporário do `start.sh` (o `launch.py` já não usa temporário).
5. Só integrar MCPs existentes depois de validar projeto upstream, transporte, argumentos e permissões; fixar versões (o `opencode.jsonc` já não usa `npx -y`).
6. Fazer o dashboard refletir health checks reais.
7. Substituir o Dockerfile de exemplo por uma configuração de isolamento realmente testada, sem mounts do host por padrão.
8. Adicionar testes automatizados e CI antes de rotular uma versão como pronta.

## Conclusão

O repositório recebeu correções de segurança pontuais, mas continua sendo um protótipo. Não use os launchers com credenciais reais nem habilite os MCPs de exemplo até a conclusão dos itens acima.
