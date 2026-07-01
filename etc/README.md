# SearchCRT - Configuração de Desenvolvimento

Este diretório contém arquivos de configuração para o desenvolvimento do SearchCRT.

## Arquivos

- `users.json` - Banco de dados local de usuários com credenciais pré-configuradas

## Credenciais Padrão

**Usuário**: admin  
**Senha**: admin123  
**Função**: admin

## Segurança

⚠️ **IMPORTANTE**: 
- Altere as credenciais padrão antes de usar em produção
- Não compartilhe o arquivo `users.json` em repositórios públicos
- Use variáveis de ambiente para senhas em produção

## Como Alterar Senha

```python
from auth_manager import auth_manager

# Criar novo usuário com senha
auth_manager.create_user('novo_usuario', 'nova_senha', 'email@example.com', 'admin')

# Listar usuários
usuarios = auth_manager.list_users()
print(usuarios)
```
