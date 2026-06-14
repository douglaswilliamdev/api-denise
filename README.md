# WhatsApp Bot - API Oficial da Meta (Cloud API) na Vercel

Mesma aplicação do projeto anterior, adaptada para rodar como **função
serverless na Vercel**. Sem banco de dados - configuração via variáveis de
ambiente do painel da Vercel.

## Estrutura

```
.
├── api/
│   └── index.py      <- código Flask (webhook + envio de mensagens)
├── vercel.json        <- configuração de build/rotas
└── requirements.txt   <- dependências Python
```

## Pré-requisitos (Meta for Developers)

1. Criar um App em https://developers.facebook.com (tipo "Business").
2. Adicionar o produto **WhatsApp**.
3. Anotar:
   - **Token de acesso** (temporário ou permanente via System User)
   - **Phone number ID**
4. Definir um **Verify Token** (qualquer string que você escolher).

## Deploy na Vercel

### Opção 1 - via GitHub (recomendado)

1. Suba esta pasta para um repositório no GitHub.
2. Em https://vercel.com, clique em **Add New > Project** e importe o repositório.
3. A Vercel detecta o `vercel.json` automaticamente.

### Opção 2 - via CLI

```bash
npm install -g vercel
cd whatsapp-bot-vercel
vercel
```

Siga as instruções no terminal (login, nome do projeto, etc).

## Configurando as variáveis de ambiente

No painel do projeto na Vercel: **Settings > Environment Variables**, adicione:

| Nome              | Valor                                  |
|-------------------|------------------------------------------|
| `WHATSAPP_TOKEN`  | seu token de acesso da Meta            |
| `PHONE_NUMBER_ID` | o Phone Number ID do WhatsApp Business |
| `VERIFY_TOKEN`    | a senha que você escolher              |
| `GRAPH_API_VERSION` | (opcional) ex: `v20.0`               |

Depois de adicionar, faça um novo deploy (ou clique em **Redeploy**) para que
as variáveis sejam aplicadas.

## Configurando o Webhook na Meta

Após o deploy, a Vercel fornece uma URL, por exemplo:

```
https://seu-projeto.vercel.app
```

1. No App da Meta, vá em **WhatsApp > Configuration**.
2. Em "Webhook", clique em **Edit**:
   - **Callback URL**: `https://seu-projeto.vercel.app/api/webhook`
   - **Verify Token**: o mesmo valor definido em `VERIFY_TOKEN`
3. Clique em **Verify and Save**.
4. Em "Webhook fields", marque **messages**.

## Testando

Envie uma mensagem do WhatsApp para o número configurado (em modo de teste,
apenas números cadastrados como "testers" no App podem conversar). A
aplicação deve responder automaticamente em poucos segundos.

## Observações sobre a Vercel

- **Sem estado entre requisições**: cada chamada ao webhook é isolada, o que
  combina bem com "sem banco de dados".
- **Timeout**: no plano gratuito (Hobby) o limite é de 10 segundos por
  execução, mais que suficiente para enviar uma mensagem de texto.
- **Cold start**: a primeira requisição após um período de inatividade pode
  demorar um pouco mais (geralmente menos de 1s extra).
- **Logs**: acompanhe erros em tempo real em **Project > Deployments >
  Functions > Logs** no painel da Vercel.

## Personalizando as respostas

A lógica de resposta está na função `build_reply()` em `api/index.py`. Edite
essa função para adicionar novas palavras-chave, fluxos de menu, etc.
