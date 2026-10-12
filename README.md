# 🎯 Radar de Abertura Day Trade B3 (WIN & WDO)

Sistema autônomo de inteligência de mercado pré-abertura para **Mini-Índice (WIN)** e **Mini-Dólar (WDO)** na B3.

O sistema acorda automaticamente na nuvem às **08:35 BRT** (25 minutos antes dos contratos futuros abrirem), analisa os mercados internacionais (EUA, China, ADRs de Petrobras e Vale em NY, Minério de Ferro, Petróleo Brent, Gás Natural e Câmbio Forex), calcula a **direção com intensidade de tendência**, **alvos em pontos**, **travas de stop loss** e envia o resumo com link direto no seu celular.

Às **18:15 BRT**, o robô audita o fechamento oficial da B3 e computa a taxa de assertividade matemática dos últimos 60 pregões.

---

## 🚀 Como Subir para o seu GitHub Privado (Passo a Passo)

### 1. Criar o Repositório no GitHub
1. Acesse [github.com/new](https://github.com/new).
2. Nomeie o repositório (exemplo: `radar-daytrade-b3`).
3. **Importante:** Marque a opção **🔒 Private (Privado)** para que ninguém tenha acesso aos seus dados.
4. Clique em **Create repository**.

### 2. Conectar e Subir o Código
No terminal da pasta deste projeto, rode os seguintes comandos (substituindo pelo link do seu repositório):

```bash
git add .
git commit -m "feat: versao final do radar day trade b3"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/radar-daytrade-b3.git
git push -u origin main
```

---

## 🔑 Configurando as Chaves Secretas no GitHub (Segurança Total)

No seu repositório no GitHub:
1. Vá em **Settings** > **Secrets and variables** > **Actions**.
2. Clique no botão verde **New repository secret**.
3. Adicione as chaves que desejar:

| Nome do Secret | Descrição | Onde Obter (Grátis) |
| :--- | :--- | :--- |
| `GEMINI_API_KEY` | *(Opcional)* IA para refinamento dos textos | [Google AI Studio](https://aistudio.google.com/) |
| `TELEGRAM_BOT_TOKEN` | Token do seu robô no Telegram | Crie com o `@BotFather` no Telegram (leva 1 min) |
| `TELEGRAM_CHAT_ID` | Seu ID no Telegram para receber o alerta | Envie mensagem para `@userinfobot` no Telegram |
| `RESEND_API_KEY` | *(Opcional)* Chave de envio de e-mail | [resend.com](https://resend.com) |
| `NOTIFICATION_EMAIL` | *(Opcional)* Seu e-mail para receber o aviso | Seu próprio e-mail pessoal |
| `DASHBOARD_URL` | *(Opcional)* Link da página web | Link do GitHub Pages ou Vercel |

---

## ⏰ Horários de Execução Automática na Nuvem

O GitHub Actions executa automaticamente de segunda a sexta-feira:
* **08:35 BRT (11:35 UTC):** Rotina matinal de coleta internacional, precificação de alvos e envio do alerta.
* **18:15 BRT (21:15 UTC):** Rotina de fechamento, conferência se o modelo acertou o pregão e atualização do placar dos 60 dias.

> Você também pode disparar manualmente a qualquer momento indo na aba **Actions** > **Radar Day Trade B3** > **Run workflow**.

---

## 📁 Estrutura do Projeto

```text
├── .github/workflows/
│   └── daily_radar.yml      # Automação na nuvem (GitHub Actions)
├── data/
│   └── history.json         # Base de dados dos últimos 60 pregões
├── src/
│   ├── collector.py         # Coleta de 15 ativos (ADRs NY, Commodities, Forex)
│   ├── analyzer.py          # Motor matemático de tendência, pontos e travas
│   ├── history.py           # Cálculo de assertividade dos 60 pregões
│   ├── generator.py         # Renderizador do painel HTML moderno
│   └── notifier.py          # Disparador de notificações (Telegram & E-mail)
├── index.html               # Painel web completo e responsivo
├── run_briefing.py          # Executável matinal (08:35 BRT)
├── run_closing.py           # Executável de fechamento (18:15 BRT)
└── requirements.txt         # Dependências Python
```
