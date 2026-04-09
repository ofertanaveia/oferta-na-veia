import requests
import json
import os
import time
import re
from datetime import datetime
import random

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8744902004:AAHFshEgRNnSCc3DS5CoOCvMldrDaji-8GE")
TELEGRAM_CHANNEL = "@ofertanaveiaoficial"
AMAZON_TAG = "limacaioprado-20"
ML_ETIQUETA = "aehgdcfab53186"
INTERVALO_MINUTOS = 15
MAX_OFERTAS_POR_CICLO = 3
HISTORICO_FILE = "historico.json"

def carregar_historico():
    if os.path.exists(HISTORICO_FILE):
        with open(HISTORICO_FILE, "r") as f:
            return json.load(f)
    return []

def salvar_historico(historico):
    with open(HISTORICO_FILE, "w") as f:
        json.dump(historico, f)

def am(asin):
    return f"https://www.amazon.com.br/dp/{asin}?tag={AMAZON_TAG}"

def ml(mlb):
    return f"https://www.mercadolivre.com.br/p/{mlb}?matt_tool={ML_ETIQUETA}"

def gerar_ofertas():
    return [
        # AMAZON - ASINs verificados
        {'titulo': 'Echo Dot 5 Geracao Smart Speaker Alexa Preto', 'preco': 349.00, 'preco_original': 499.00, 'desconto': 30, 'link': am('B09B8VGCR8'), 'loja': 'Amazon'},
        {'titulo': 'Echo Dot 5 Geracao com Relogio Alexa Azul', 'preco': 449.00, 'preco_original': 649.00, 'desconto': 31, 'link': am('B09B8XXWKT'), 'loja': 'Amazon'},
        {'titulo': 'Fire TV Stick HD Streaming com Alexa', 'preco': 249.00, 'preco_original': 399.00, 'desconto': 38, 'link': am('B0CQMT33WX'), 'loja': 'Amazon'},
        {'titulo': 'Fire TV Stick 4K Streaming Dolby Vision Alexa', 'preco': 349.00, 'preco_original': 549.00, 'desconto': 36, 'link': am('B0872Y93TY'), 'loja': 'Amazon'},
        {'titulo': 'Kindle 11 Geracao 16GB com Luz Embutida', 'preco': 399.00, 'preco_original': 599.00, 'desconto': 33, 'link': am('B09SWS1R73'), 'loja': 'Amazon'},
        {'titulo': 'Fone JBL Tune 510BT Bluetooth 40h Preto', 'preco': 199.90, 'preco_original': 349.90, 'desconto': 43, 'link': am('B08WM3FVPZ'), 'loja': 'Amazon'},
        {'titulo': 'Caixa de Som JBL Go 3 Bluetooth Portatil', 'preco': 149.90, 'preco_original': 249.90, 'desconto': 40, 'link': am('B08KMQ9GWN'), 'loja': 'Amazon'},
        {'titulo': 'Headset HyperX Cloud Stinger Gamer', 'preco': 199.90, 'preco_original': 349.90, 'desconto': 43, 'link': am('B01LWZ8EGF'), 'loja': 'Amazon'},
        {'titulo': 'Webcam Logitech C920 Full HD 1080p', 'preco': 399.00, 'preco_original': 699.00, 'desconto': 43, 'link': am('B006A2Q81M'), 'loja': 'Amazon'},
        {'titulo': 'HD Externo Seagate Expansion 1TB USB 3.0', 'preco': 299.00, 'preco_original': 499.00, 'desconto': 40, 'link': am('B00TKFEEAS'), 'loja': 'Amazon'},
        {'titulo': 'SSD Interno Kingston 480GB SATA III', 'preco': 149.90, 'preco_original': 279.90, 'desconto': 46, 'link': am('B01N5IIA6W'), 'loja': 'Amazon'},
        {'titulo': 'Powerbank Anker 20000mAh Carregamento Rapido', 'preco': 299.90, 'preco_original': 499.90, 'desconto': 40, 'link': am('B09VPHVT2Z'), 'loja': 'Amazon'},
        {'titulo': 'Carregador Anker 65W USB-C GaN Compacto', 'preco': 199.90, 'preco_original': 349.90, 'desconto': 43, 'link': am('B09C7SLHFP'), 'loja': 'Amazon'},
        {'titulo': 'Mouse sem Fio Logitech MX Master 3S', 'preco': 549.00, 'preco_original': 899.00, 'desconto': 39, 'link': am('B09HM94VDS'), 'loja': 'Amazon'},
        {'titulo': 'Cafeteira Nespresso Essenza Mini Preta', 'preco': 399.90, 'preco_original': 699.90, 'desconto': 43, 'link': am('B07Q4NKBVD'), 'loja': 'Amazon'},
        {'titulo': 'Escova Dental Eletrica Oral-B Pro 1', 'preco': 149.90, 'preco_original': 299.90, 'desconto': 50, 'link': am('B00J3AFBD2'), 'loja': 'Amazon'},
        {'titulo': 'Protetor Solar Neutrogena Sun Fresh FPS 70', 'preco': 49.90, 'preco_original': 89.90, 'desconto': 44, 'link': am('B07H4DGKQX'), 'loja': 'Amazon'},
        {'titulo': 'Livro Pai Rico Pai Pobre Edicao Especial', 'preco': 39.90, 'preco_original': 79.90, 'desconto': 50, 'link': am('8550801488'), 'loja': 'Amazon'},
        {'titulo': 'Livro O Poder do Habito Charles Duhigg', 'preco': 34.90, 'preco_original': 69.90, 'desconto': 50, 'link': am('8539004119'), 'loja': 'Amazon'},
        {'titulo': 'Livro Mindset Psicologia do Sucesso Carol Dweck', 'preco': 39.90, 'preco_original': 79.90, 'desconto': 50, 'link': am('8543107539'), 'loja': 'Amazon'},
        {'titulo': 'Garrafa Termica Stanley Classic 1L', 'preco': 249.90, 'preco_original': 449.90, 'desconto': 44, 'link': am('B08TFX1MJL'), 'loja': 'Amazon'},
        {'titulo': 'Chaleira Eletrica Tramontina 1.7L Inox', 'preco': 99.90, 'preco_original': 189.90, 'desconto': 47, 'link': am('B07XQTHDRJ'), 'loja': 'Amazon'},
        {'titulo': 'Suporte Ergonomico para Notebook Ajustavel', 'preco': 89.90, 'preco_original': 179.90, 'desconto': 50, 'link': am('B07KDDKDH1'), 'loja': 'Amazon'},
        {'titulo': 'Whey Protein Gold Standard 1.8kg Chocolate', 'preco': 299.90, 'preco_original': 499.90, 'desconto': 40, 'link': am('B000GIQT2G'), 'loja': 'Amazon'},
        {'titulo': 'Camera Fujifilm Instax Mini 12', 'preco': 499.00, 'preco_original': 799.00, 'desconto': 38, 'link': am('B0BQMVNKL4'), 'loja': 'Amazon'},

        # MERCADO LIVRE - MLBs verificados
        {'titulo': 'Fire TV Stick 3 Geracao Full HD Alexa Preto', 'preco': 289.00, 'preco_original': 449.00, 'desconto': 36, 'link': ml('MLB18593745'), 'loja': 'Mercado Livre'},
        {'titulo': 'Fire TV Stick Amazon 3 Geracao Voz Full HD', 'preco': 299.00, 'preco_original': 449.00, 'desconto': 33, 'link': ml('MLB27803562'), 'loja': 'Mercado Livre'},
    ]

def formatar_mensagem(oferta):
    titulo = oferta['titulo']
    loja = oferta['loja']
    link = oferta['link']
    preco = oferta['preco']
    preco_original = oferta['preco_original']
    desconto = oferta['desconto']
    emoji = '📦' if loja == 'Amazon' else '🟡'
    preco_fmt = f"R$ {preco:,.2f}".replace(',','X').replace('.',',').replace('X','.')
    orig_fmt = f"R$ {preco_original:,.2f}".replace(',','X').replace('.',',').replace('X','.')
    linhas = [
        f"🔥 *{titulo}*", "",
        f"💰 *Por apenas {preco_fmt}*",
        f"~~De {orig_fmt}~~ — *{desconto}% OFF* 🏷️", "",
        f"{emoji} {loja}", "",
        f"👉 [PEGAR OFERTA]({link})", "",
        "━━━━━━━━━━━━━━━━━━",
        "📢 @ofertanaveiaoficial",
        "🔔 Ative as notificacoes!"
    ]
    return "\n".join(linhas)

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {'chat_id': TELEGRAM_CHANNEL, 'text': mensagem, 'parse_mode': 'Markdown', 'disable_web_page_preview': False}
    try:
        resp = requests.post(url, json=payload, timeout=15)
        print(f"  Telegram: {resp.status_code}")
        return resp.status_code == 200
    except Exception as e:
        print(f"  Erro: {e}")
        return False

def rodar_ciclo():
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Iniciando ciclo...")
    historico = carregar_historico()
    ofertas = gerar_ofertas()
    random.shuffle(ofertas)
    disponiveis = [o for o in ofertas if re.sub(r'[^a-z0-9]', '', o['titulo'].lower())[:40] not in historico]
    if len(disponiveis) == 0:
        print("  Reiniciando ciclo...")
        historico = []
        disponiveis = ofertas
    postadas = 0
    for oferta in disponiveis:
        if postadas >= MAX_OFERTAS_POR_CICLO:
            break
        oferta_id = re.sub(r'[^a-z0-9]', '', oferta['titulo'].lower())[:40]
        mensagem = formatar_mensagem(oferta)
        if enviar_telegram(mensagem):
            historico.append(oferta_id)
            postadas += 1
            print(f"  OK: {oferta['titulo'][:50]}")
            time.sleep(8)
    salvar_historico(historico)
    print(f"  Total: {postadas} postada(s).")

def main():
    print("="*50)
    print("  OFERTA NA VEIA BOT - v12")
    print("  Links verificados e reais!")
    print(f"  Intervalo: {INTERVALO_MINUTOS}min")
    print("="*50)
    if os.path.exists(HISTORICO_FILE):
        os.remove(HISTORICO_FILE)
    while True:
        try:
            rodar_ciclo()
        except Exception as e:
            print(f"  Erro: {e}")
        print(f"  Proxima busca em {INTERVALO_MINUTOS} min...")
        time.sleep(INTERVALO_MINUTOS * 60)

if __name__ == "__main__":
    main()
