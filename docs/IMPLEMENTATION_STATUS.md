# MEGA-CODE-4 — status real de implementação

Última revisão: 2026-11-14.

## Resultado da auditoria

**Este repositório ainda não está pronto para ser considerado funcional ou seguro para uso operacional.** Os arquivos atuais contêm uma base documental/prototípica, mas não uma entrega completa do agente.

| Componente | Estado verificado | O que falta |
|---|---|---|
| Engine OpenCode | Ausente neste repositório | O launcher procura binários em `engine/`, mas a árvore atual não contém esse diretório nem os executáveis. |
| Launcher Linux/macOS | Protótipo | Precisa de teste e correções de fluxo; não foi validado em ambiente real. |
| Launcher Windows | Incompleto | A cópia atual não contém todas as rotinas chamadas pelos labels e não deve ser apresentada como launcher funcional. |
| Coarena | Não validada | Endpoint e nomes de modelos são exemplos; confirmar URL, modelo e esquema de configuração com a Coarena. |
| Cifragem de credenciais | Ferramenta isolada | O helper usa AES-GCM/PBKDF2, mas os launchers atuais passam senha em argumentos e criam temporários; isso precisa de revisão antes de uso com segredos reais. |
| MCP router | Classificador apenas | `tools/mcp_router.py` imprime sugestões JSON. Não inicia MCPs, não faz lazy loading integrado ao OpenCode e não controla disponibilidade. |
| HexStrike AI | Não implementado/validado | Há apenas uma referência de configuração de exemplo. Nenhum servidor está empacotado, instalado ou conectado. |
| CyberStrike | Não implementado/validado | Há referências de configuração de exemplo, sem conectores reais confirmados. Os nomes de pacotes MCP não foram verificados e não devem ser executados como estão. |
| Dashboard | Protótipo não validado | O status apresentado é estático e não comprova conectividade real. A experiência de autenticação no navegador e a rota de token precisam de revisão. |
| Dockerfile | Não é sandbox de ferramentas | Executa apenas um servidor HTTP estático; não instala, inicia nem isola OpenCode, HexStrike ou CyberStrike. |

## CyberStrike e HexStrike: decisão de implementação

- **CyberStrike:** pode ser integrado futuramente para tarefas defensivas de repositório, como revisão de código e dependências, depois de verificar a documentação e a origem oficial dos servidores MCP. Não há integração funcional neste commit.
- **HexStrike AI:** não será iniciado automaticamente nem roteado a partir de texto livre para reconhecimento/varredura de alvos. A configuração existente é apenas referência e está desativada. Uma integração futura deve ser opt-in, limitada a escopo autorizado e validada em sandbox antes do uso.
- O roteador atual não é uma barreira de segurança, autorização ou controle de acesso.

## Próximos requisitos antes de declarar pronto

1. Definir e testar a versão compatível do engine e a instalação verificável de seus binários.
2. Corrigir os dois launchers e executar testes em Windows e Linux/macOS.
3. Validar o formato de configuração e o endpoint/modelo fornecidos pela Coarena.
4. Refazer o fluxo de segredos para não passar senha na linha de comando nem armazenar chave em configuração gerada sem necessidade.
5. Só integrar MCPs existentes depois de validar projeto upstream, transporte, argumentos e permissões.
6. Fazer o dashboard refletir health checks reais; remover estados MCP fixos e evitar expor tokens por rota pública.
7. Substituir o Dockerfile de exemplo por uma configuração de isolamento realmente testada, sem mounts do host por padrão.
8. Adicionar testes automatizados e evidências dos testes antes de rotular uma versão como pronta.

## Conclusão

O repositório foi criado e recebeu arquivos iniciais, mas a solicitação de “completo e funcional” ainda não foi satisfeita. Não use os launchers atuais com credenciais reais nem habilite os MCPs de exemplo até a conclusão dos itens acima.
