# Prompt para concluir o MEGA-CODE-4 com Claude Code

Use este documento como instrução de trabalho com o repositório aberto no Claude Code. O Claude deve ler o código e a documentação atuais antes de implementar; este prompt não substitui a revisão do estado real nem garante testes em plataformas que não estejam disponíveis.

> **Acesso:** o repositório `OmegaVermelho/MEGA-CODE-4` está **público** (verificado em 2026-11-16). Qualquer pessoa pode ler, mas criar branch, commits e PR exige que o Claude Code esteja autenticado com permissão de escrita. Se a visibilidade mudar, atualize este aviso. Antes de qualquer mudança de visibilidade, revise código, histórico e arquivos em busca de segredos e dados privados.

---

## Instruções para Claude Code

Você é responsável por concluir o projeto **MEGA-CODE-4** neste repositório. Inspecione primeiro os arquivos, histórico e estrutura existentes; depois implemente e teste mudanças incrementais em uma branch de trabalho. Não presuma que documentos ou comentários descrevem corretamente o comportamento atual.

### Objetivo

Transformar o protótipo em uma base coerente, portátil, defensiva e testável para usar o engine OpenCode, corrigindo launchers, configuração, gerenciamento de credenciais, dashboard local, documentação e testes. Seja preciso sobre o que depende de serviços ou binários externos e não declare conclusão sem evidências.

### Regras de segurança e honestidade

1. Trabalhe em branch separada; não altere `main` diretamente. No final, apresente um resumo e a branch/PR para revisão. Não faça merge nem altere a visibilidade do repositório sem autorização.
2. Não invente nomes de modelos, endpoints, pacotes, opções de CLI, schemas ou capacidades. Verifique a documentação e o código oficiais das dependências; marque como pendente o que não puder verificar.
3. Nunca coloque chaves, tokens, senhas, dados pessoais ou configurações locais em commits, logs ou exemplos executáveis. Não use credenciais reais em testes.
4. Mantenha o escopo em codificação e análise defensiva do repositório local escolhido pelo usuário. Não implemente varredura de alvos, reconhecimento de rede, enumeração de portas/hosts, exploração, payloads, persistência ou execução ofensiva.
5. **HexStrike AI deve permanecer desativado e não executável por este projeto.** Não ligue varreduras/reconhecimento a texto livre ou a automação autônoma.
6. CyberStrike só pode ser avaliado para revisão defensiva de código/dependências local depois de confirmar projeto upstream, licença, versão, transporte, permissões e escopo. Se não for verificável, deixe-o fora e documente a pendência.
7. Um classificador de prompt não é autorização nem controle de segurança. Não execute processos arbitrários com base no texto do usuário.
8. Serviços opcionais locais devem vincular somente a `127.0.0.1`; nunca exponha em `0.0.0.0` ou interface pública.
9. Não alegue “zero rastros”, “sandbox militar”, “isolamento total” ou “pronto para produção” sem evidência. Explique limites do sistema hospedeiro.
10. Não instale nem execute dependências não verificadas ou versões flutuantes. Prefira fontes oficiais e versões fixadas.

### Etapa 1 — Auditoria do repositório

- Inspecione a árvore, estado do Git, launchers, arquivos de configuração, scripts, dependências, documentação e testes.
- Identifique funcionalidades reais, placeholders, erros e dependências ausentes.
- Registre o estado inicial e elabore um plano curto. Faça mudanças incrementais, evitando reescrita desnecessária.

### Etapa 2 — Engine OpenCode

- Determine, pela fonte/documentação oficial, qual versão do OpenCode é suportada e qual schema/configuração ela aceita.
- Não invente compatibilidade nem modelo/provedor. Se o engine não estiver disponível, não simule seu funcionamento: deixe uma mensagem clara e instruções verificáveis de obtenção/build oficial.
- Não faça download silencioso nem inclua binários grandes/de procedência duvidosa. Quando aplicável, verifique checksums/assinaturas publicados pelo upstream e registre versão e procedência.
- Marque testes de integração como pendentes se não puder executar o engine real.

### Etapa 3 — Launchers portáteis

Revise `start.sh` e `START.bat` para que:

- resolvam a raiz do projeto independentemente do diretório corrente;
- redirecionem no processo filho `HOME`, `USERPROFILE`, `XDG_CONFIG_HOME`, `XDG_DATA_HOME`, `XDG_CACHE_HOME`, `APPDATA` e `LOCALAPPDATA` a diretórios dentro de `data/`;
- validem diretórios e argumentos, preservem corretamente argumentos do engine e retornem seus códigos de saída;
- falhem com mensagens úteis quando engine/dependências estiverem ausentes;
- nunca imprimam credenciais ou senha mestre;
- exibam estados como “não configurado”, “desativado” ou “desconhecido”, sem badges MCP falsos de “ON”.

Não afirme que todo o sistema operacional está confinado ao `data/`; documente quais caminhos são controlados e as limitações do host. Use stubs/testes para validar o fluxo dos launchers sem executar comandos de segurança ou engine não disponível.

### Etapa 4 — Configuração e segredos

- Ajuste `opencode.jsonc` somente após validar o schema da versão real do OpenCode.
- Endpoint, modelo e chave devem vir de valores fornecidos/documentados pelo provedor; placeholders precisam ser claramente identificados como exemplos não funcionais.
- Revise `tools/secure_env.py`: entrada de senha segura, KDF com parâmetros versionados, criptografia autenticada (por exemplo AES-GCM), arquivos com permissões restritas e tratamento de erro sem revelar conteúdo.
- Não passe senha em argumento de processo. Evite chave em arquivo de configuração em texto claro, logs, ambiente persistente ou arquivo temporário. Se uma limitação da integração exigir segredo em memória/ambiente de subprocesso, minimize sua duração e documente o risco.
- Se usar arquivos temporários, crie-os sob `data/`, com permissões restritas, limpe-os em `finally` e explique que remoção não garante apagamento físico em SSD/journaling.
- Atualize `.gitignore` para cobrir segredos, dados locais, logs e arquivos gerados.

### Etapa 5 — Dashboard opcional

- O dashboard não deve iniciar automaticamente sem opção explícita.
- Faça bind apenas em `127.0.0.1`; valide a porta e não confie em host/proxy controlado pela requisição.
- Remova endpoint que devolve token ao cliente. Não exponha tokens em URL, JavaScript público ou resposta acessível sem autenticação.
- Corrija validação de Bearer token com comparação em tempo constante apenas após validar buffers de tamanho igual.
- Proteja arquivos estáticos com resolução canônica e allowlist; bloqueie path traversal e symlinks que escapem do diretório permitido.
- Use `textContent` para conteúdo dinâmico; não use `innerHTML` com dados externos.
- Health/status deve refletir verificações reais. Sem verificação, usar `unknown`/`disabled`; jamais inventar estado online.
- Aplique headers de segurança adequados, `Cache-Control: no-store` em APIs e erros sem stack trace para o cliente.
- Teste ausência/token inválido/válido, rotas autorizadas, traversal e bind local.

### Etapa 6 — MCPs

- Mantenha MCPs desativados por padrão.
- Verifique documentação upstream, licença, versão, transporte, opções, permissões e compatibilidade com o engine antes de qualquer integração.
- CyberStrike pode ser considerado somente para análise defensiva local, com opt-in explícito, escopo visível e versão fixada; não o inclua se essas condições não forem comprovadas.
- Não implemente ativação automática de HexStrike nem varredura/reconhecimento de rede.
- Se `tools/mcp_router.py` continuar existindo apenas como classificador informativo, diga isso claramente; não alegue que ele inicia servidores ou implementa lazy loading.
- Não use `npx -y` ou comandos equivalentes para pacotes MCP não verificados.

### Etapa 7 — Sandbox e CI

- Não chame o Dockerfile de sandbox até que ele realmente execute o componente alvo sob isolamento testado.
- Para ferramentas defensivas locais, documente isolamento apropriado: sem `--network host`, sem mounts desnecessários do host, usuário não-root, capabilities removidas, `no-new-privileges`, filesystem read-only quando possível, limites de recursos e rede bloqueada por padrão.
- Não exponha portas MCP externamente e não acrescente modo de varredura remota.
- Configure CI para testes/lint de Python, Node e shell disponíveis. Use runner Windows se validar Windows; não alegue teste macOS sem runner macOS.

### Etapa 8 — Testes e documentação

Adicione e execute testes, conforme aplicável, para:

- parsing/validação de argumentos e códigos de saída dos launchers;
- redirecionamento de ambiente e geração de configuração;
- cifragem/decifragem, senha incorreta e dados adulterados;
- autenticação e autorização do dashboard;
- tentativa de path traversal;
- router como classificador informativo, sem execução de processos;
- configuração conforme schema real, se engine disponível.

Atualize `README.md`, `docs/IMPLEMENTATION_STATUS.md`, `docs/SECURITY.md` e docs pertinentes para que correspondam ao comportamento implementado. Para cada teste, informe comando, ambiente e resultado. O que não foi executado deve ficar marcado como **não testado/pendente**, com motivo e procedimento de validação.

### Critério para declarar pronto para avaliação

Só declare o projeto “pronto para avaliação” quando código e docs coincidirem, testes executáveis passarem, não houver segredos, não houver placeholders apresentados como funcionais, o dashboard estiver limitado e testado em localhost, HexStrike continuar inativo, e qualquer integração CyberStrike estiver verificada e limitada a análise defensiva local. Ainda assim, liste plataformas e dependências não testadas.

### Entrega final

Ao terminar, informe:

1. o que foi implementado;
2. arquivos alterados;
3. testes executados com comandos, plataformas e resultados;
4. itens pendentes e por que não foram testados;
5. riscos e limitações conhecidos;
6. branch/PR criada e próximos passos para revisão.

Comece agora auditando o repositório aberto. Não diga que está concluído sem evidências e não finja integração com serviços externos ausentes.

---

## Fim do prompt
