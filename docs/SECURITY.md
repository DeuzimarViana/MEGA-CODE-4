# MEGA-CODE-4 — Notas de segurança

Consulte também [o status da implementação](IMPLEMENTATION_STATUS.md). O projeto está em protótipo e não deve ser considerado uma distribuição endurecida ou pronta para produção.

## Limites de portabilidade

Os launchers tentam redirecionar diretórios conhecidos para `data/`, mas isso não garante “zero rastros”: sistema operacional, swap, logs, antivírus, backups, telemetria e sincronização podem observar ou persistir dados. Com o OpenCode 1.19.5, a pasta temporária do engine é `/tmp/opencode` (fora de `data/`), a menos que `TMPDIR` seja redirecionado antes de executá-lo.

## Credenciais

O helper Python cifra conteúdo com AES-GCM e deriva chave com PBKDF2-HMAC-SHA256. A senha não é mais passada como argumento de linha de comando: o `start.sh` a entrega por variável de ambiente apenas ao processo filho (ou o helper pede via `getpass`), e o `launch.py` a lê com `getpass` (ou de `MEGA_MASTER_PASSWORD`, que não é repassada ao engine). Limitações que continuam valendo:

- no `start.sh`, durante a carga e a gravação das configurações existe um arquivo temporário em texto claro, criado em `data/` com permissão 0600 e removido logo depois (e no `trap EXIT`); remover o arquivo não garante apagamento físico em SSD ou sistemas com journaling. O `tools/launch.py` (usado pelo `START.bat`) cifra e decifra em memória, sem esse temporário;
- os launchers ainda gravam a chave de API em texto claro em `data/home/.opencode.json` (permissão 0600), arquivo que o OpenCode real **não lê** (testado com a 1.19.5). O caminho correto é passar a chave por `{env:COARENA_API_KEY}`, como o `opencode.jsonc` já faz, e parar de gravá-la; os launchers ainda não foram ajustados;
- o formato do arquivo cifrado não é versionado;
- criptografia em repouso não protege dados em memória.

Não use credenciais reais com o fluxo atual até esses pontos serem resolvidos e testados.

## Dashboard

O servidor de demonstração escuta apenas em `127.0.0.1`. A API (`/api/*`) exige Bearer token; os arquivos estáticos de `tools/web` são públicos nessa interface e não contêm segredos. A rota que devolvia o token foi removida: o token é exibido no terminal (ou definido em `MEGA_DASHBOARD_TOKEN`) e colado no campo da página, ficando só em `sessionStorage`. O status de MCP e modelo aparece como `unknown`, porque não há health check real. Ainda assim, não exponha a porta em interfaces de rede.

## MCP e ferramentas de segurança

Os conectores CyberStrike e HexStrike não estão instalados nem integrados neste repositório. Configuração declarativa não significa execução nem segurança. Mantenha serviços não validados desligados; o `opencode.jsonc` não tem entrada de HexStrike e os launchers só geram, em um arquivo que o engine ignora, uma configuração com HexStrike desativado. Só use ferramentas em sistemas com autorização e escopo definidos; não faça ativação automática baseada apenas em prompt.

## Configuração do OpenCode

O `opencode.jsonc` pede confirmação (`ask`) para `edit`, `bash` e `webfetch`, desativa o compartilhamento de sessões (`share: disabled`) e lê a chave de API de `{env:COARENA_API_KEY}`, sem gravá-la no arquivo. Isso reduz riscos, mas não é isolamento nem autorização: o efeito interativo das permissões não foi exercitado e o engine continua rodando com os privilégios do seu usuário.

## Container

O `Dockerfile` presente inicia um servidor HTTP estático e não constitui sandbox das ferramentas. Ele serve os arquivos de `tools/web` sem a autenticação do dashboard Node. Não o use para alegar isolamento de código ou de ferramentas MCP. Para desenvolvimento, prefira uma VM descartável ou um container revisado sem mounts do host, com usuário não-root, capabilities removidas, limites de recursos e rede restrita.
