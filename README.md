<p align="center">
  <pre align="center">
<span style="color:#ff1a1a">███╗   ███╗███████╗ ██████╗  █████╗       ██████╗ ██████╗ ██████╗ ███████╗██╗  ██╗██╗  ██╗</span>
<span style="color:#ff3333">████╗ ████║██╔════╝██╔════╝ ██╔══██╗     ██╔════╝██╔═══██╗██╔══██╗██╔════╝██║  ██║██║  ██║</span>
<span style="color:#ff4d4d">██╔████╔██║█████╗  ██║  ███╗███████║     ██║     ██║   ██║██║  ██║█████╗  ███████║███████║</span>
<span style="color:#ff6666">██║╚██╔╝██║██╔══╝  ██║   ██║██╔══██║     ██║     ██║   ██║██║  ██║██╔══╝  ██╔══██║╚════██║</span>
<span style="color:#ff8080">██║ ╚═╝ ██║███████╗╚██████╔╝██║  ██║     ╚██████╗╚██████╔╝██████╔╝███████╗██║  ██║     ██║</span>
<span style="color:#ff9999">╚═╝     ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝      ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝     ╚═╝</span>
  </pre>
  <strong style="color:#ff3333">⚡ MEGA-CODE-4 ⚡</strong><br>
  <em>Portable AI Coding Project</em>
</p>

# MEGA-CODE-4

> Projeto experimental para um agente portátil de codificação com integração de IA e documentação de segurança.

**Estado atual: protótipo incompleto.** Veja [status da implementação](docs/IMPLEMENTATION_STATUS.md) antes de tentar executar. O nome do repositório é `MEGA-CODE-4`.

## Conteúdo disponível

O repositório contém launchers experimentais, configuração de exemplo, um classificador de prompts para MCP e um dashboard de demonstração. **Não inclui atualmente os binários do engine OpenCode nem conectores MCP funcionais.** Os launchers e o Dockerfile ainda não foram validados como distribuição executável/sandbox.

## Requisitos para desenvolvimento

- Python 3 e o pacote `cryptography` para `tools/secure_env.py` e `tools/launch.py` (o `START.bat` exige Python 3 no Windows).
- Node.js para executar o servidor de dashboard de exemplo.
- Um engine OpenCode compatível, obtido de fonte oficial (opencode.ai); a árvore deste repositório não contém os binários. A configuração foi validada com a versão 1.19.5 (Linux x64). Evite forks não oficiais.
- Endpoint, modelo e credencial válidos fornecidos pela Coarena, se for testar o provedor.

Os valores `api.coarena.example` e `Fable-5` são placeholders e não garantem que esse endpoint/modelo exista. Confirme os dados com o provedor.

## Aviso sobre launchers

`start.sh`, `START.bat` (que chama `tools/launch.py`) e `tools/launch.py` estão em estado experimental. Foram testados apenas em Linux com um engine falso: o engine OpenCode real não está no repositório e o `START.bat` não foi executado em Windows. Não os use com credenciais reais até a validação (veja [status da implementação](docs/IMPLEMENTATION_STATUS.md)).

**Importante:** o `.opencode.json` que os launchers geram **não é lido** pelo OpenCode real (testado com a versão 1.19.5). A configuração válida é o `opencode.jsonc` deste repositório, que o engine lê na raiz do projeto aberto ou em `$XDG_CONFIG_HOME/opencode/`. Ajustar os launchers para isso ainda está pendente.

## CyberStrike e HexStrike AI

Essas ferramentas **não estão implementadas nem conectadas** neste repositório. O `opencode.jsonc` mantém três entradas CyberStrike no formato oficial do OpenCode, todas desativadas (`enabled: false`). Os pacotes não foram verificados e não devem ser tratados como comandos instaláveis. HexStrike não tem entrada na configuração. O roteador apenas classifica texto e sugere nomes; ele não inicia servidores nem integra ferramentas ao agente.

Qualquer integração futura deve usar fontes oficiais verificadas, ser opt-in e limitar-se a uso autorizado. O roteador não substitui controles de escopo ou autorização.

## Portabilidade e segurança

Redirecionar algumas variáveis de ambiente para `data/` não garante ausência de rastros no host. O sistema operacional, swap, logs, antivírus, backups e sincronização ainda podem registrar ou copiar informações. A cifragem em repouso não protege segredos depois de carregados em memória.

O Dockerfile atual serve apenas como exemplo de servidor HTTP estático: não é uma sandbox de segurança. Não use para executar ferramentas ou código não confiável.

## Documentação

- [Status real da implementação](docs/IMPLEMENTATION_STATUS.md)
- [Notas de segurança](docs/SECURITY.md)
- [Roteamento MCP](docs/MCP_ROUTING.md)
- [Prompt para Claude Code](docs/CLAUDE_CODE_PROMPT.md)
