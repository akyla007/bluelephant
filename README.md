Projeto Bluelephant.

Descrição do desafio: ./info/desafio_tecnico_bluelephant.pdf

# WebSocket Chat – Desafio Técnico

Este projeto mostra, de forma direta, como criar um chat simples com **WebSockets**.
Ele possui:
- **Backend em Python (FastAPI)** para manter conexões ativas e fazer **broadcast** de mensagens.
- **Frontend em HTML + JavaScript** para enviar e receber mensagens no navegador.

Objetivo: demonstrar domínio do protocolo WebSocket e organização de código.

---

## 📐 Arquitetura (Visão Geral)

```bash
Cliente (Browser / CLI)
│
│ WebSocket
▼
Servidor FastAPI
│
├── Pool de conexões ativas
└── Broadcast de mensagens
```

- Cada cliente mantém uma conexão aberta com o servidor.
- Ao enviar uma mensagem, o servidor repassa para todos os outros clientes conectados.

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.10+**
- **FastAPI** – Backend e WebSockets
- **Uvicorn** – Servidor ASGI
- **uv** – Gerenciamento de dependências e execução
- **Black** – Formatação automática de código
- **HTML + JavaScript** – Cliente WebSocket simples

---

## 📁 Estrutura do Projeto

```bash
bluelephant/
├── backend/
│   ├── main.py
│   └── connection_manager.py
├── frontend/
│   └── index.html
├── info/
├── pyproject.toml
└── README.md
```


---

## ▶️ Como Executar (passo a passo)

### 1️⃣ Pré-requisitos
- Python 3.10+
- uv instalado

```bash
pip install uv
```

### 2️⃣ Instalar dependências
Na raiz do projeto, rode:

```bash
uv sync
```

### 3️⃣ Iniciar o servidor

```bash
uv run uvicorn backend.main:app --reload --reload-dir backend
```

Se tudo estiver ok, o servidor estará em http://localhost:8000.

---

## 🧪 Como Testar

### ✅ Teste HTTP (health check)

```bash
curl http://localhost:8000/
```

Resposta esperada:

```json
{"status":"ok"}
```

### ✅ Teste via navegador (Frontend)

1. Abra o arquivo frontend/index.html no navegador.
2. Abra duas abas com esse mesmo arquivo.
3. Envie mensagens em uma aba e veja o **broadcast** na outra.

### ✅ Teste via linha de comando (opcional)

```bash
wscat -c ws://localhost:8000/ws
```

Abra dois terminais e envie mensagens para validar o broadcast.

## 🧠 Decisões Técnicas

- **FastAPI** pela simplicidade, clareza e suporte nativo a WebSockets.
- **ConnectionManager** para centralizar o controle das conexões ativas e facilitar manutenção.
- **Broadcast** como abordagem mais simples e adequada ao escopo do desafio.
- **uv** e **black** para ambiente moderno, reprodutível e código padronizado.

## 🚀 Possíveis Extensões

- Identificação de clientes
- Criação de salas (rooms)
- Autenticação
- Persistência de mensagens
- Escalonamento com Pub/Sub (ex: Redis)

## 📌 Observações Finais

Este projeto foi desenvolvido com foco em:

- Clareza de código
- Organização
- Simplicidade
- Aderência aos requisitos do desafio


