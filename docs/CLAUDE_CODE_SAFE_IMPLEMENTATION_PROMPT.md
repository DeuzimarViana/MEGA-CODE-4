# Prompt seguro para continuar a implementação do MEGA-CODE-4

Use este prompt no Claude Code com o repositório aberto. Primeiro leia o estado atual do código e da documentação; não presuma que o texto abaixo ou documentos antigos descrevam perfeitamente a implementação existente.

> **Acesso:** o repositório `DeuzimarViana/MEGA-CODE-4` é público. O Claude Code precisa estar autenticado e autorizado a ler e editar o repositório.

---

Você é responsável por completar a base defensiva do projeto MEGA-CODE-4. Trabalhe em uma branch separada e faça alterações pequenas, testáveis e documentadas. Não faça merge nem altere a visibilidade do repositório sem autorização.

## Regras obrigatórias

1. Revise a árvore, estado do Git, código e documentação antes de alterar arquivos.
2. Não invente nomes de modelos, endpoints, pacotes, opções de CLI, schemas ou capacidades. Verifique fontes oficiais e registre pendências quando não puder validar.
3. Nunca coloque chaves, tokens, senhas ou dados privados em commits, logs ou exemplos executáveis. Não use credenciais reais em testes.
4. Mantenha serviços opcionais em `127.0.0.1`, desativados por padrão. Bind local não prova que o processo não pode acessar a rede.
5. HexStrike e ferramentas de reconhecimento, varredura, enumeração ou exploração devem permanecer desativados e não executáveis pelo projeto. Não encaminhe texto livre a essas ferramentas.
6. Só avalie CyberStrike após confirmar o upstream, licença, versão, transporte e permissões; se não for possível comprovar uso defensivo e escopo local, deixe-o fora.
7. Um classificador de prompts não é autorização nem controle de segurança. Não execute processos arbitrários com base no texto do usuário.
8. Não declare “zero rastros”, “isolamento total”, “sandbox” ou “pronto para produção” sem evidências. Documente limites do sistema hospedeiro.
9. Não instale ou execute dependências não verificadas ou versões flutuantes. Prefira versões fixadas e fontes oficiais.
10. Não afirme que testes foram executados sem executá-los. Informe ambiente, comando e resultado real; marque o restante como pendente.

## Tarefas

### 1. Gerenciador local de processos

Revise `mcp_manager.py` e implemente ou corrija uma TUI segura para gerenciar apenas serviços locais inofensivos e aprovados, como `dummy_mcp.py`.

- Usar `data/mcp_prefs.json` para preferências booleanas e `data/mcp_pids.json` para PIDs, sem segredos.
- Distinguir estados `OFF`, `ON` e `UNKNOWN` por verificação real do processo e health check.
- Iniciar/parar apenas serviços em allowlist; recusar serviços não verificados e binds diferentes de localhost.
- Encerrar processos com tratamento correto por plataforma; não matar um PID sem verificar que corresponde ao processo esperado.
- Mostrar aviso de reinício do OpenCode se a configuração MCP não puder ser recarregada em tempo real.

### 2. Servidor dummy e teste de ciclo de vida

Crie `dummy_mcp.py` como servidor HTTP simples que só escute em `127.0.0.1` e responda `OK` no endpoint raiz. Crie `test_toggle.py` para iniciar esse servidor, confirmar PID e health check, enviar término gracioso e verificar que terminou sem zumbi. O teste não deve iniciar nenhuma ferramenta de segurança externa.

### 3. Credenciais criptografadas

Revise `tools/secure_env.py`:

- usar criptografia autenticada AES-GCM e derivação de chave versionada com parâmetros registrados no formato;
- pedir senha interativamente (`getpass`) ou recebê-la por mecanismo seguro, nunca em argumento de linha de comando;
- definir permissões restritas em arquivos compatíveis com o sistema operacional;
- não criar arquivo temporário de texto claro sem necessidade; se inevitável, restringir permissões, limpar em `finally` e documentar limitações de apagamento físico;
- testar senha errada e arquivo adulterado;
- não imprimir segredos ou conteúdo descriptografado.

### 4. Controles de uso da Coarena e “tambor” de APIs

Implemente monitoramento de uso por conta, sem rotação de contas para contornar limites. Ter múltiplas chaves ou contas não prova que seus saldos ou quotas possam ser combinados.

- Antes de qualquer integração, verifique a documentação oficial e os termos da Coarena sobre contas múltiplas, limites diários, chaves e uso combinado. Se não for possível confirmar, deixe integração e failover desativados e registre a pendência.
- Criar `data/tambor.json` apenas para metadados e preferências: identificador não secreto, alias, estado, limites autorizados, uso registrado e horário de renovação. Nunca inclua API keys, tokens ou senhas nesse arquivo.
- Guardar credenciais somente em mecanismo criptografado e protegido; não as registrar em logs, argumentos, arquivos rastreados ou configuração em texto claro.
- Implementar um orçamento agregado configurável e limites por conta. Quando uma conta alcançar o limite diário, bloquear novas chamadas para essa conta e aguardar a renovação ou intervenção autorizada.
- **Não alternar automaticamente para outra conta quando a conta atual atingir seu limite diário, quota, saldo ou restrição.** Não usar múltiplas contas para contornar limite, cobrança, rate limit, controles antifraude ou termos do provedor.
- Só habilitar failover entre chaves/contas se houver confirmação explícita e documentada do provedor de que o caso de uso é permitido. Mesmo assim, exigir opt-in, teto agregado de gasto, auditoria sem segredos, limites por conta e mecanismo de parada; não elevar nem multiplicar limites autorizados.
- Respeitar respostas de rate limit e `Retry-After` conforme documentação. Erros de rede ou servidor não devem ser interpretados automaticamente como crédito esgotado.
- Não inventar endpoint, nome de modelo, semântica de erro ou saldo. Se os detalhes não forem verificáveis, implementar somente controles locais com mocks e manter chamadas reais desativadas.
- Criar testes unitários sem chaves reais e sem chamadas externas: limite por conta, teto agregado, bloqueio após atingir limite, renovação simulada, erros transitórios e ausência de rotação automática.

### 5. Launchers e configuração

Revise `start.sh`, `START.bat` e `opencode.jsonc`:

- mantenha MCPs desativados por padrão e não inclua comandos para HexStrike, scan, recon ou exploração;
- corrija referências inválidas e preserve códigos de saída/argumentos;
- não imprima chaves ou senha mestre;
- só configure o provedor Coarena com valores fornecidos e confirmados pelo usuário/documentação oficial;
- não alegue que diretórios sob `data/` isolam o sistema operacional inteiro.

### 6. Documentação

Atualize `README.md`, `docs/IMPLEMENTATION_STATUS.md` e `docs/SECURITY.md` para refletir o código efetivo, os limites de portabilidade, o status real de cada integração e os testes executados. Documente claramente o comportamento de limites e a política de não alternar contas para contorná-los.

## Critérios de aceite

- O ciclo de vida do servidor dummy passa nos testes locais e o status corresponde ao processo real.
- Nenhuma integração de ferramenta ofensiva pode ser ativada pelo manager, roteador ou prompt.
- Nenhum segredo fica em claro em arquivos rastreados, logs ou argumentos de processo.
- Limites por conta e teto agregado são respeitados; atingir um limite bloqueia novas chamadas, sem troca automática para outra conta.
- Failover de API só pode ser habilitado após validação da política e do protocolo oficiais; caso contrário, permanece desativado e documentado.
- Documentação e código coincidem, e testes não executados aparecem como pendentes.

## Entrega final

Informe:

1. o que foi implementado e quais arquivos foram alterados;
2. comandos de teste executados, ambiente e resultados;
3. itens não testados e motivo;
4. dependências e integração externa que continuam pendentes;
5. riscos e limitações conhecidos;
6. branch/PR para revisão, sem fazer merge.

Comece auditando o repositório atual. Não declare a tarefa concluída sem evidências.

---
