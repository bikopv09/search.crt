# SearchCRT - Diretório de Exportações

Arquivo de exportações geradas pelo SearchCRT.

## Formatos Suportados

- **ZIP**: Relatórios consolidados com múltiplos formatos
- **CSV**: Valores separados por vírgula (;)
- **XLSX**: Planilhas Excel
- **TXT**: Arquivos de texto

## Estrutura de Pasta

```
exports/
├── Relatorio_SearchCRT_20260701.zip
├── SearchCRT_Busca_20260701.txt
└── comparativo_20260701.xlsx
```

## Nomeação de Arquivos

Os arquivos são nomeados automaticamente com timestamp:
- Formato: `[Tipo]_[YYYYMMDD_HHMMSS].[ext]`
- Exemplo: `Relatorio_20260701_203045.zip`

## Política de Retenção

Configure em `config.ini`:

```ini
[Features]
export_directory=./exports/
```

## Limpeza de Exportações Antigas

Para remover exportações com mais de 90 dias:

```bash
find ./exports -type f -mtime +90 -delete
```
