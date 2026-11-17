# MEGA-CODE-4 — Notas de segurança

Consulte também [o status da implementação](IMPLEMENTATION_STATUS.md). O projeto está em protótipo e não deve ser considerado uma distribuição endurecida ou pronta para produção.

## Limites de portabilidade

Os launchers tentam redirecionar diretórios conhecidos para `data/`, mas isso não garante “zero rastros”: sistema operacional, swap, logs, antivírus, backups, telemetria e sincronização podem observar ou persistir dados.

## Credenciais

O helper Python cifra conteúdo com AES-GCM e deriva chave com PBKDF2-HMAC-SHA256. A senha não é mais passada como argumento de linha de comando: o `start.sh` a entrega por variável de ambiente apenas ao processo filho (ou o helper pede via `getpass`), e o `launch.py` a lê com `getpass` (ou de `MEGA_MASTER_PASSWORD`, que não é repassada ao engine). Limitações que continuam valendo:

- no `start.sh`, durante a carga e a gravação das configurações existe um arquivo temporário em texto claro, criado em `data/` com permissão 0600 e removido logo depois (e no `trap EXIT`); remover o arquivo não garante apagamento físico em SSD ou sistemas com journaling. O `tools/launch.py` (usado pelo `START.bat`) cifra e decifra em memória, sem esse temporário;
- a chave de API é gravada em texto claro em `data/home/.opencode.json` (permissão 0600), porque o formato de configuração do engine ainda não foi validado;
- o formato do arquivo cifrado não é versionado;
- criptografia em repouso não protege dados em memória.

Não use credenciais reais com o fluxo atual até esses pontos serem resolvidos e testados.

## Dashboard

O servidor de demonstração escuta apenas em `127.0.0.1`. A API (`/api/*`) exige Bearer token; os arquivos estáticos de `tools/web` são públicos nessa interface e não contêm segredos. A rota que devolvia o token foi removida: o token é exibido no terminal (ou definido em `MEGA_DASHBOARD_TOKEN`) e colado no campo da página, ficando só em `sessionStorage`. O status de MCP e modelo aparece como `unknown`, porque não há health check real. Ainda assim, não exponha a porta em interfaces de rede.

## MCP e ferramentas de segurança

Os conectores CyberStrike e HexStrike não estão instalados nem integrados neste repositório. Configuração declarativa não significa execução nem segurança. Mantenha serviços não validados desligados; o launcher gera a configuração com HexStrike sempre desativado. Só use ferramentas em sistemas com autorização e escopo definidos; não faça ativação automática baseada apenas em prompt.

## Container

O `Dockerfile` presente inicia um servidor HTTP estático e não constitui sandbox das ferramentas. Ele serve os arquivos de `tools/web` sem a autenticação do dashboard Node. Não o use para alegar isolamento de código ou de ferramentas MCP. Para desenvolvimento, prefira uma VM descartável ou um container revisado sem mounts do host, com usuário não-root, capabilities removidas, limites de recursos e rede restrita.
