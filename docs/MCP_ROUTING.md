# MEGA-CODE-4 — Roteamento MCP

## Estado atual

`tools/mcp_router.py` é somente um classificador heurístico: recebe texto como argumentos e imprime uma sugestão JSON. Não está conectado ao OpenCode, não inicia nem encerra servidores, não implementa lazy loading e não autoriza operações.

O `opencode.jsonc` segue agora o formato oficial de MCP do OpenCode (`type: local`, `command` como lista, `enabled: false`), validado com a versão 1.19.5: o engine carrega a configuração e lista os três servidores como desativados. Os nomes de pacotes, opções de linha de comando e transportes **não** foram confirmados com projetos upstream; não os execute sem validação independente. O roteador não é um servidor MCP e por isso não aparece na configuração, e o bloco `routing` que existia no arquivo foi removido (o engine não o usa).

## CyberStrike e HexStrike AI

Nenhum dos dois está instalado ou integrado neste repositório.

- Uma futura integração CyberStrike deve começar por tarefas defensivas de código/dependências e usar um servidor MCP de origem e documentação verificadas.
- HexStrike não deve ser iniciado automaticamente por correspondência de prompt. Não há entrada de HexStrike no `opencode.jsonc`; qualquer uso futuro requer autorização explícita, escopo definido e isolamento validado.

## Requisitos para uma implementação real

1. Escolher servidores MCP upstream verificados e registrar versão fixa, não uma instalação flutuante via `npx -y`.
2. Confirmar o transporte de cada servidor com o engine utilizado (o esquema `mcp` do OpenCode 1.19.5 já foi confirmado; os servidores em si não).
3. Implementar ativação no cliente/engine; a saída atual do classificador não executa essa ação.
4. Manter servidores desativados por padrão e aplicar allowlist de escopo para ferramentas de segurança.
5. Exibir no dashboard estado obtido por health check real, não um rótulo estático.
6. Testar com servidores de demonstração em ambiente isolado antes de disponibilizar a usuários.
