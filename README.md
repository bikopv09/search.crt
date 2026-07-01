# 🔍 SearchCRT - Sistema Profissional de Busca e Comparativo de Dados

[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)](https://github.com/bikopv09/search.crt)

**SearchCRT** é uma aplicação desktop profissional desenvolvida em Python com Tkinter, especializada em **busca avançada**, **comparação de dados** e **rastreamento de informações** em arquivos. Ideal para análise de grandes volumes de dados, identificação de duplicatas e cruzamento de informações entre múltiplas fontes.

---

## 🌟 Principais Funcionalidades

### 🔄 **Comparativo Avançado de Dados**
Compare múltiplos arquivos simultaneamente e identifique padrões:
- ✅ Suporte a XLSX, XLS, TXT e CSV
- ✅ Extração inteligente de: **Nomes**, **CPF**, **Telefone**, **E-mail**
- ✅ Validação automática de CPF (dígitos verificadores)
- ✅ Normalização Unicode de texto
- ✅ Limite customizável de fontes para ocorrência
- ✅ Processamento multi-thread não-bloqueante
- ✅ Barra de progresso em tempo real
- ✅ Exportação em ZIP (TXT, CSV, XLSX)

### 🎯 **Busca Localizada (Rastreio)**
Localize registros específicos com precisão:
- ✅ Busca por: Nome, CPF, Telefone, E-mail, Município
- ✅ Varredura de múltiplas abas em planilhas
- ✅ Processamento paralelo otimizado
- ✅ Resultados instantâneos
- ✅ Exportação de achados em TXT

### 🔐 **Autenticação e Segurança**
Sistema robusto de controle de acesso:
- ✅ Login com criptografia SHA-256
- ✅ Gerenciamento de usuários local
- ✅ Sessões com timeout configurável
- ✅ Roles (admin, user)
- ✅ Logging completo de acessos

### 📊 **Integração com Banco de Dados**
Armazenamento persistente e recuperação de dados:
- ✅ MongoDB integrado
- ✅ Collections: searches, results, users
- ✅ Histórico de buscas
- ✅ Modo offline com fallback
- ✅ Error handling robusto

### ⚙️ **Configuração Centralizada**
Controle total sobre a aplicação:
- ✅ Arquivo `config.ini` único
- ✅ Múltiplas seções organizadas
- ✅ Valores com defaults inteligentes
- ✅ Suporte a string, int, bool
- ✅ Carregamento automático

---

## 📋 Requisitos

### Sistema
- **Python**: 3.8 ou superior
- **RAM**: 2GB mínimo (4GB recomendado)
- **Espaço em disco**: 500MB

### Dependências
```
pandas>=1.3.0         # Processamento de dados
openpyxl>=3.6.0       # Excel
pymongo>=3.12.0       # MongoDB
python-dateutil>=2.8.0 # Utilitários de data
numpy>=1.20.0         # Computação numérica
```

---

## 🚀 Instalação Rápida

### 1. Clone o repositório
```bash
git clone https://github.com/bikopv09/search.crt.git
cd search.crt
```

### 2. Crie ambiente virtual (recomendado)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale dependências
```bash
pip install -r requirements.txt
```

### 4. Execute a aplicação
```bash
# Versão original
python searchcrt.py

# OU Versão integrada com autenticação e MongoDB
python searchcrt_integrated.py
```

---

## 📖 Uso

### Comparativo de Dados
1. Clique em **"COMPARATIVO DE DADOS"**
2. Selecione os campos: Nome, CPF, Telefone, E-mail
3. Defina o mínimo de fontes necessárias
4. Adicione arquivos para análise
5. Clique em **"PROCESSAR DADOS"**
6. Revise os resultados
7. Exporte em ZIP

### Busca Localizada
1. Clique em **"BUSCA LOCALIZADA"**
2. Selecione o tipo de dado
3. Insira o termo a buscar
4. Selecione a planilha
5. Aguarde o resultado
6. Exporte os achados

---

## ⚙️ Configuração

### Arquivo config.ini

Customize em `config.ini`:

```ini
[Database]
mongodb_host=localhost
mongodb_port=27017
database_name=searchcrt

[UI]
theme=dark
window_width=600
window_height=400

[Features]
enable_logging=True
log_file=./logs/searchcrt.log
log_level=INFO

[Authentication]
enable_auth=False
session_timeout=3600
```

Veja [INSTALL.md](INSTALL.md) para configuração completa.

---

## 🔐 Autenticação

### Credenciais Padrão
```
Usuário: admin
Senha: admin123
```

### Criar Novo Usuário
```python
from auth_manager import auth_manager

auth_manager.create_user(
    username='novo_usuario',
    password='senha_segura',
    email='usuario@example.com',
    role='admin'
)
```

### Ativar Autenticação
Edite `config.ini`:
```ini
[Authentication]
enable_auth=True
```

---

## 📊 Estrutura do Projeto

```
search.crt/
├── 📄 searchcrt.py                # App original (33.7 KB)
├── 📄 searchcrt_integrated.py       # App integrada com DB
├── 📄 config_manager.py            # Gerenciador de config
├── 📄 database_manager.py          # Gerenciador de DB
├── 📄 auth_manager.py              # Gerenciador de auth
├── ⚙️ config.ini                   # Configuração principal
├── 📦 requirements.txt             # Dependências
├── 📦 setup.py                     # Setup para distribuição
├── 📚 README.md                    # Este arquivo
├── 📚 INSTALL.md                   # Guia de instalação
├── 📚 CONFIGURATION_REPORT.md      # Relatório de configuração
├── 📁 etc/                         # Configurações
│   ├── users.json                  # Banco de usuários
│   └── README.md                   # Documentação
├── 📁 logs/                        # Logs da aplicação
│   └── searchcrt.log               # Log principal
├── 📁 exports/                     # Exportações geradas
└── 📁 tests/                       # Testes unitários
    └── test_core.py                # Testes
```

---

## 📝 Logs

Todos os eventos são registrados em `./logs/searchcrt.log`:

```
2026-07-01 20:30:45 - searchcrt - INFO - Connected to MongoDB successfully
2026-07-01 20:31:12 - searchcrt - INFO - User 'admin' authenticated successfully
2026-07-01 20:32:08 - searchcrt - INFO - Search record inserted: 507f1f77bcf86cd799439011
```

Configure em `config.ini`:
```ini
[Features]
enable_logging=True
log_file=./logs/searchcrt.log
log_level=INFO
max_log_size=100MB
```

---

## 🧪 Testes

Execute testes unitários:

```bash
# Instalar pytest
pip install pytest pytest-cov

# Rodar testes
pytest tests/

# Com cobertura
pytest --cov=. tests/
```

---

## 🔒 Segurança

- ✅ Senhas criptografadas com SHA-256
- ✅ Validação de entrada de dados
- ✅ Sessões com timeout
- ✅ Logging detalhado de operações
- ✅ Modo offline seguro
- ✅ Proteção de arquivos sensíveis

---

## 📈 Performance

- **Threading**: Operações não-bloqueantes
- **Cache**: Configurável para otimização
- **Limite de Resultados**: 500 registros por padrão
- **Max Workers**: 4 threads simultâneas
- **Chunk Processing**: Suporta arquivos grandes

Configure em `config.ini`:
```ini
[Performance]
max_workers=4
cache_enabled=True
cache_ttl=3600
result_limit=500
```

---

## 🐛 Troubleshooting

### Erro: "MongoDB Connection Failed"
```bash
# Inicie MongoDB
mongod --dbpath /data/db

# Ou use modo offline (deixar config.ini vazio)
```

### Interface Lenta
```ini
[Performance]
max_workers=2
cache_ttl=1800
result_limit=250
```

### Erro: "Configuration file not found"
```bash
# Verifique se config.ini existe
ls config.ini
# Se não, crie do template
cp config.ini.example config.ini
```

---

## 🤝 Contribuição

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está sob a **Licença MIT**. Veja [LICENSE](LICENSE) para detalhes.

---

## 👨‍💻 Autor

**bikopv09** - Desenvolvedor principal

- GitHub: [@bikopv09](https://github.com/bikopv09)
- Email: bkservicoss@gmail.com

---

## 📞 Suporte

- **Issues**: [GitHub Issues](https://github.com/bikopv09/search.crt/issues)
- **Email**: bkservicoss@gmail.com
- **Documentação**: [INSTALL.md](INSTALL.md)

---

## 🙏 Agradecimentos

- Comunidade Python
- Pandas development team
- MongoDB community
- Tkinter documentation

---

## 📊 Status

| Aspecto | Status |
|---------|--------|
| **Core** | ✅ Production Ready |
| **Testes** | ✅ Unit Tests |
| **Documentação** | ✅ Completa |
| **Segurança** | ✅ Implementada |
| **Performance** | ✅ Otimizada |

---

**Versão**: 1.0.0  
**Última Atualização**: 2026-07-01  
**Status**: 🚀 **Pronto para Produção**

---

> 💡 **Dica**: Para configuração completa, consulte [INSTALL.md](INSTALL.md) e [CONFIGURATION_REPORT.md](CONFIGURATION_REPORT.md)
