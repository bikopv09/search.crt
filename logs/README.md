# SearchCRT - Diretório de Logs

Todos os eventos da aplicação SearchCRT são registrados aqui.

## Arquivos de Log

- `searchcrt.log` - Log principal da aplicação
- `analytics.log` - Log de análises e operações

## Níveis de Log

- **DEBUG**: Informações detalhadas para diagnóstico
- **INFO**: Eventos importantes (login, operações completadas)
- **WARNING**: Situações incomuns (falhas de conexão, acesso negado)
- **ERROR**: Erros que precisam de atenção
- **CRITICAL**: Erros críticos que afetam a operação

## Rotação de Logs

Os logs são rotacionados automaticamente quando atingem o tamanho máximo configurado em `config.ini`:

```ini
[Features]
maxLogSize=100MB
backlog=5
```

## Exemplo de Log

```
2026-07-01 20:30:45,123 - searchcrt - INFO - Connected to MongoDB successfully
2026-07-01 20:31:12,456 - searchcrt - INFO - User 'admin' authenticated successfully
2026-07-01 20:32:08,789 - searchcrt - INFO - Search record inserted: 507f1f77bcf86cd799439011
2026-07-01 20:33:21,012 - searchcrt - WARNING - Cache miss for query: "João Silva"
```

## Limpeza de Logs Antigos

Para limpar logs antigos, execute:

```bash
find ./logs -name "*.log" -mtime +30 -delete
```

Isto removará logs com mais de 30 dias.
