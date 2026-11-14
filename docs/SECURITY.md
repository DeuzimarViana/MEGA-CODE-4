# MEGA-CODE-4 — Notas de segurança

Consulte também [o status da implementação](IMPLEMENTATION_STATUS.md). O projeto está em protótipo e não deve ser considerado uma distribuição endurecida ou pronta para produção.

## Limites de portabilidade

Os launchers tentam redirecionar diretórios conhecidos para `data/`, mas isso não garante “zero rastros”: sistema operacional, swap, logs, antivírus, backups, telemetria e sincronização podem observar ou persistir dados.

## Credenciais

O helper Python cifra conteúdo com AES-GCM e deriva chave com PBKDF2-HMAC-SHA256. Apesar disso, o fluxo atual de launcher ainda passa senha como argumento de processo e cria arquivo temporário de texto claro; isso pode expor segredos. Não use credenciais reais com o fluxo atual até essa implementação ser corrigida e testada. Criptografia em repouso não protege dados em memória.

## Dashboard

O servidor de demonstração tem limitações que precisam de correção antes de uso sensível: token configurável por ambiente, rota de token local, autenticação do navegador não concluída e badges que não representam health checks reais. Não exponha a porta em interfaces de rede.

## MCP e ferramentas de segurança

Os conectores CyberStrike e HexStrike não estão instalados nem integrados neste repositório. Configuração declarativa não significa execução nem segurança. Mantenha serviços não validados desligados. Só use ferramentas em sistemas com autorização e escopo definidos; não faça ativação automática baseada apenas em prompt.

## Container

O `Dockerfile` presente inicia um servidor HTTP estático e não constitui sandbox das ferramentas. Não o use para alegar isolamento de código ou de ferramentas MCP. Para desenvolvimento, prefira uma VM descartável ou um container revisado sem mounts do host, com usuário não-root, capabilities removidas, limites de recursos e rede restrita.
