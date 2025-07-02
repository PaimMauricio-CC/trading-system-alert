# Flask Forex Monitor

Aplicação simples de monitoramento de alertas para ativos de Forex usando Flask.

## Como executar

```bash
pip install -r flask_forex_monitor/requirements.txt

# Defina suas credenciais do Gmail
export GMAIL_USER="seu_usuario@gmail.com"
export GMAIL_PASS="sua_senha"
export TO_EMAIL="destinatario@example.com"

python flask_forex_monitor/app.py
```

A aplicação estará acessível em `http://localhost:5002`.
