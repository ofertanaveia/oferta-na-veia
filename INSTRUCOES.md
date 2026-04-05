# 🔥 OFERTA NA VEIA BOT — Guia de Instalação

## O que esse bot faz
- Busca ofertas quentes automaticamente no Pelando.com.br
- Filtra apenas ofertas com 15%+ de desconto ou alta temperatura
- Injeta seu link de afiliado Amazon automaticamente
- Posta no seu canal do Telegram a cada 30 minutos
- Evita repostar a mesma oferta

---

## OPÇÃO 1 — Rodar no Railway (recomendado, 24h online, grátis)

### Passo 1 — Criar conta no Railway
1. Acesse https://railway.app
2. Clique em "Login" → "Login with GitHub"
3. Crie uma conta no GitHub se não tiver (gratuito)

### Passo 2 — Subir os arquivos no GitHub
1. Acesse https://github.com e crie um repositório privado chamado `oferta-na-veia`
2. Faça upload dos 3 arquivos: `bot.py`, `requirements.txt`, `railway.toml`

### Passo 3 — Conectar ao Railway
1. No Railway, clique em "New Project"
2. Escolha "Deploy from GitHub repo"
3. Selecione o repositório `oferta-na-veia`
4. Clique em "Deploy Now"

### Passo 4 — Pronto!
O bot vai iniciar automaticamente e postar no canal.
Para ver os logs, clique no projeto → "View Logs"

---

## OPÇÃO 2 — Rodar no seu computador (para testar)

### Requisitos
- Python 3.10 ou superior instalado

### Passos
1. Coloque os arquivos em uma pasta chamada `oferta_na_veia`
2. Abra o terminal nessa pasta
3. Execute:
```
pip install -r requirements.txt
python bot.py
```

---

## Configurações que você pode ajustar no bot.py

| Configuração | Valor atual | O que faz |
|---|---|---|
| INTERVALO_MINUTOS | 30 | A cada quantos minutos buscar |
| DESCONTO_MINIMO | 15 | % mínimo de desconto |
| MAX_OFERTAS_POR_CICLO | 5 | Máximo de posts por rodada |

---

## Suporte
Em caso de dúvidas, consulte a documentação do Railway em https://docs.railway.app
