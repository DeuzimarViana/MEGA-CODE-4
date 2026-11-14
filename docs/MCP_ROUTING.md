# MEGA-CODE-4 — Roteamento MCP

## Estado atual

`tools/mcp_router.py` é somente um classificador heurístico: recebe texto como argumentos e imprime uma sugestão JSON. Não está conectado ao OpenCode, não inicia nem encerra servidores, não implementa lazy loading e não autoriza operações.

As configurações MCP em `opencode.jsonc` são referências não verificadas. Os nomes de pacotes, opções de linha de comando e transportes não foram confirmados com projetos upstream; não os execute sem validação independente.

## CyberStrike e HexStrike AI

Nenhum dos dois está instalado ou integrado neste repositório.

- Uma futura integração CyberStrike deve começar por tarefas defensivas de código/dependências e usar um servidor MCP de origem e documentação verificadas.
- HexStrike não deve ser iniciado automaticamente por correspondência de prompt. A configuração existente é placeholder/desativada; qualquer uso futuro requer autorização explícita, escopo definido e isolamento validado.

## Requisitos para uma implementação real

1. Escolher servidores MCP upstream verificados e registrar versão fixa, não uma instalação flutuante via `npx -y`.
2. Confirmar transporte e esquema suportados pelo engine OpenCode utilizado.
3. Implementar ativação no cliente/engine; a saída atual do classificador não executa essa ação.
4. Manter servidores desativados por padrão e aplicar allowlist de escopo para ferramentas de segurança.
5. Exibir no dashboard estado obtido por health check real, não um rótulo estático.
6. Testar com servidores de demonstração em ambiente isolado antes de disponibilizar a usuários.
