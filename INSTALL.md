# SearchCRT - Guia de Instalação e Configuração Completa

## 🚀 Início Rápido

### 1. Pré-requisitos
```bash
# Verificar Python 3.8+
python --version

# Verificar pip
pip --version
```

### 2. Clonar Repositório
```bash
git clone https://github.com/bikopv09/search.crt.git
cd search.crt
```

### 3. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 4. Executar Aplicação
```bash
python searchcrt_integrated.py
```

---

## ⚙️ Configuração Detalhada

### Arquivo config.ini

O arquivo `config.ini` controla todos os aspectos da aplicação.

#### Seção [Database]

```ini
[Database]
mongodb_host=localhost           # Host do MongoDB
mongodb_port=27017             # Porta do MongoDB
database_name=searchcrt        # Nome do banco de dados
mongodb_username=              # Usuário (deixe vazio se sem autenticação)
mongodb_password=              # Senha
```

**Para usar sem MongoDB:**
- Deixe vazios os campos de conexão
- A aplicação funcionará em modo offline
- Os dados serão armazenados localmente apenas

#### Seção [UI]

```ini
[UI]
theme=dark                     # Tema: dark ou light
window_width=600               # Largura da janela
window_height=400              # Altura da janela
bg_color=#0A1D3A              # Cor de fundo
panel_bg=#102F4D              # Cor dos painéis
fg_color=#4DD0E1              # Cor de destaque
```

#### Seção [Features]

```ini
[Features]
enable_logging=True            # Ativar logs
log_file=./logs/searchcrt.log # Arquivo de log
log_level=INFO                # Nível: DEBUG, INFO, WARNING, ERROR
max_log_size=100MB            # Tamanho máximo antes de rotacionar
backlog=5                     # Quantos logs antigos manter
```

#### Seção [Authentication]

```ini
[Authentication]
enable_auth=False             # Ativar autenticação
auth_type=local               # Tipo: local ou ldap (futuro)
session_timeout=3600          # Timeout em segundos (1 hora)
users_file=./etc/users.json  # Arquivo de usuários
```

#### Seção [Performance]

```ini
[Performance]
cache_enabled=True            # Cache de resultados
cache_ttl=3600               # TTL do cache em segundos
max_workers=4                # Threads para processamento paralelo
```

---

## 🔐 Gerenciamento de Usuários

### Ativar Autenticação

```ini
[Authentication]
enable_auth=True
```

### Criar Novo Usuário

```python
from auth_manager import auth_manager

# Criar admin
auth_manager.create_user(
    username='admin',
    password='SenhaForte123!',
    email='admin@searchcrt.com',
    role='admin'
)

# Criar usuário comum
auth_manager.create_user(
    username='usuario1',
    password='SenhaUsuario123',
    email='usuario@searchcrt.com',
    role='user'
)

# Listar usuários
print(auth_manager.list_users())
```

### Credenciais Padrão

- **Usuário**: admin
- **Senha**: admin123
- **Arquivo**: `./etc/users.json`

---

## 🗄️ Configuração do MongoDB

### Instalação Local

**Windows:**
```bash
# Baixar de: https://www.mongodb.com/try/download/community
# Executar instalador
mongod --dbpath "C:\data\db"
```

**macOS:**
```bash
brew tap mongodb/brew
brew install mongodb-community
mongod --dbpath /usr/local/var/mongodb
```

**Linux:**
```bash
sudo apt-get install -y mongodb-org
sudo systemctl start mongod
```

### Conexão Remota

```ini
[Database]
mongodb_host=mongo.example.com
mongodb_port=27017
mongodb_username=user
mongodb_password=pass
```

### Verificar Conexão

```python
from database_manager import get_db_manager

db = get_db_manager()
if db:
    print("✓ Conectado ao MongoDB")
else:
    print("✗ Modo offline (sem banco de dados)")
```

---

## 📊 Estrutura do Banco de Dados

### Collections

- **searches**: Histórico de buscas realizadas
- **results**: Resultados armazenados
- **users**: Informações de usuários (se autenticação habilitada)

### Exemplo de Documento (searches)

```json
{
  "_id": "507f1f77bcf86cd799439011",
  "username": "admin",
  "search_type": "comparative",
  "timestamp": "2026-07-01T20:30:00",
  "files_count": 3,
  "search_fields": ["Nome", "CPF"],
  "status": "completed",
  "results_count": 45
}
```

---

## 📝 Logs e Monitoramento

### Arquivo de Log

Localizado em: `./logs/searchcrt.log`

### Estrutura do Log

```
2026-07-01 20:30:45 - searchcrt - INFO - Connected to MongoDB successfully
2026-07-01 20:31:12 - searchcrt - INFO - User 'admin' authenticated successfully
2026-07-01 20:32:08 - searchcrt - INFO - Search record inserted: 507f1f77bcf86cd799439011
```

### Visualizar Logs em Tempo Real

```bash
# Linux/macOS
tail -f logs/searchcrt.log

# Windows
Get-Content logs\searchcrt.log -Wait
```

---

## 🧪 Testes

### Executar Testes

```bash
pip install pytest pytest-cov

# Rodar todos os testes
pytest tests/

# Com cobertura
pytest --cov=. tests/
```

### Exemplo de Teste

```bash
pytest tests/test_core.py::TestAuthenticationManager::test_verify_user_valid -v
```

---

## 🚨 Troubleshooting

### Erro: "Configuration file not found"

```bash
# Verificar se config.ini existe
ls -la config.ini

# Criar a partir do template
cp config.ini.example config.ini
```

### Erro: "MongoDB Connection Failed"

```bash
# Verificar se MongoDB está rodando
mongosh

# Ou usar modo offline
# Deixar campos vazios em [Database]
```

### Erro: "Permission Denied" ao gravar logs

```bash
# Criar diretório com permissões
mkdir -p logs
chmod 755 logs
```

### Interface Lenta

```ini
[Performance]
max_workers=2
cache_ttl=1800
result_limit=250
```

---

## 📦 Distribuição

### Criar Pacote

```bash
python setup.py sdist bdist_wheel
```

### Instalar Localmente

```bash
pip install -e .
```

---

## 📞 Suporte

- **Issues**: https://github.com/bikopv09/search.crt/issues
- **Email**: bkservicoss@gmail.com
- **Documentação**: README.md

---

**Versão**: 1.0.0  
**Última Atualização**: 2026-07-01
