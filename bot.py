import requests
import json
import os
import time
import re
from datetime import datetime
import random

TELEGRAM_TOKEN = "8744902004:AAHFshEgRNnSCc3DS5CoOCvMldrDaji-8GE"
TELEGRAM_CHANNEL = "@ofertanaveiaoficial"
LOMADEE_TOKEN = "WLTKyxEVVYJPS3oNt-rKqa8vTcTYRw56"
LOMADEE_SOURCE = "6ff2699e-ceaa-4fad-a58a-8b91f885485f"
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

def buscar_ofertas_lomadee():
    """Busca ofertas reais da API da Lomadee"""
    ofertas = []
    try:
        url = f"https://api.lomadee.com/v3/{LOMADEE_TOKEN}/offer/_search"
        params = {
            'sourceId': LOMADEE_SOURCE,
            'size': 50,
            'sort': 'discount',
            'order': 'desc'
        }
        headers = {'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'}
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        print(f"  Lomadee status: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            items = data.get('offers', data.get('offer', []))
            print(f"  Lomadee: {len(items)} ofertas encontradas")
            
            for item in items:
                try:
                    titulo = item.get('name', item.get('nome', ''))
                    link = item.get('link', item.get('url', ''))
                    preco = float(item.get('price', item.get('preco', 0)) or 0)
                    preco_original = float(item.get('priceFrom', item.get('precoOriginal', 0)) or 0)
                    desconto = int(item.get('discount', item.get('desconto', 0)) or 0)
                    loja = item.get('store', {}).get('name', item.get('loja', {}).get('nome', 'Loja')) if isinstance(item.get('store', item.get('loja')), dict) else 'Loja'
                    imagem = item.get('thumbnail', item.get('imagem', ''))

                    if not titulo or not link or desconto < 10:
                        continue

                    if preco_original == 0 and preco > 0:
                        preco_original = round(preco / (1 - desconto/100), 2) if desconto > 0 else preco

                    oferta_id = re.sub(r'[^a-z0-9]', '', titulo.lower())[:40]
                    ofertas.append({
                        'id': oferta_id,
                        'titulo': titulo,
                        'preco': preco,
                        'preco_original': preco_original,
                        'desconto': desconto,
                        'link': link,
                        'loja': loja,
                        'imagem': imagem
                    })
                except Exception as e:
                    continue
        else:
            print(f"  Resposta: {resp.text[:200]}")
    except Exception as e:
        print(f"  Erro Lomadee: {e}")
    return ofertas

def ofertas_fallback():
    """Ofertas de backup caso a API falhe"""
    return [
        {'id': 'fonebluetoothjbl', 'titulo': 'Fone Bluetooth JBL Tune 510BT', 'preco': 199.90, 'preco_original': 349.90, 'desconto': 43, 'link': 'https://www.amazon.com.br/s?k=fone+jbl+tune+510bt&tag=limacaioprado-20', 'loja': 'Amazon'},
        {'id': 'smartwatchxiaomi', 'titulo': 'Smartwatch Xiaomi Redmi Watch 3', 'preco': 249.90, 'preco_original': 399.90, 'desconto': 38, 'link': 'https://shopee.com.br/search?keyword=xiaomi+redmi+watch+3&af_siteid=lima.caioprado', 'loja': 'Shopee'},
        {'id': 'airfryer4lphilips', 'titulo': 'Air Fryer 4L Philips Walita', 'preco': 299.90, 'preco_original': 499.90, 'desconto': 40, 'link': 'https://www.amazon.com.br/s?k=air+fryer+philips+walita&tag=limacaioprado-20', 'loja': 'Amazon'},
        {'id': 'sskingston480gb', 'titulo': 'SSD Kingston 480GB SATA III', 'preco': 149.90, 'preco_original': 279.90, 'desconto': 46, 'link': 'https://www.amazon.com.br/s?k=ssd+kingston+480gb&tag=limacaioprado-20', 'loja': 'Amazon'},
        {'id': 'carregador65wusbc', 'titulo': 'Carregador Turbo 65W USB-C GaN', 'preco': 69.90, 'preco_original': 149.90, 'desconto': 53, 'link': 'https://www.amazon.com.br/s?k=carregador+turbo+65w+usb-c&tag=limacaioprado-20', 'loja': 'Amazon'},
    ]

def formatar_mensagem(oferta):
    titulo = oferta['titulo']
    loja = oferta['loja']
    link = oferta['link']
    preco = oferta.get('preco', 0)
    preco_original = oferta.get('preco_original', 0)
    desconto = oferta.get('desconto', 0)

    emoji_map = {'Amazon': '📦', 'Shopee': '🛍️', 'Mercado Livre': '🟡', 'Americanas': '🔴', 'Magazine Luiza': '🛒', 'Casas Bahia': '🔵', 'Kabum': '🖥️'}
    emoji = emoji_map.get(loja, '🏪')

    linhas = [f"🔥 *{titulo}*", ""]
    if preco and preco > 0:
        preco_fmt = f"R$ {preco:,.2f}".replace(',','X').replace('.',',').replace('X','.')
        linhas.append(f"💰 *Por apenas {preco_fmt}*")
        if preco_original and preco_original > preco and desconto > 0:
            orig_fmt = f"R$ {preco_original:,.2f}".replace(',','X').replace('.',',').replace('X','.')
            linhas.append(f"~~De {orig_fmt}~~ → *{desconto}% OFF* 🏷️")
    elif desconto > 0:
        linhas.append(f"*{desconto}% OFF* 🏷️")
    linhas += ["", f"{emoji} {loja}", "", f"👉 [PEGAR OFERTA]({link})", "", "━━━━━━━━━━━━━━━━━━", "📢 @ofertanaveiaoficial", "🔔 Ative as notificações!"]
    return "\n".join(linhas)

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {'chat_id': TELEGRAM_CHANNEL, 'text': mensagem, 'parse_mode': 'Markdown', 'disable_web_page_preview': False}
    try:
        resp = requests.post(url, json=payload, timeout=15)
        print(f"  Telegram: {resp.status_code}")
        return resp.status_code == 200
    except Exception as e:
        print(f"  Erro Telegram: {e}")
        return False

def rodar_ciclo():
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Buscando ofertas Lomadee...")
    historico = carregar_historico()

    ofertas = buscar_ofertas_lomadee()

    if len(ofertas) == 0:
        print("  Lomadee sem retorno, usando fallback...")
        ofertas = ofertas_fallback()

    random.shuffle(ofertas)
    disponiveis = [o for o in ofertas if o['id'] not in historico]

    if len(disponiveis) == 0:
        print("  Todas postadas! Reiniciando ciclo...")
        historico = []
        disponiveis = ofertas

    postadas = 0
    for oferta in disponiveis:
        if postadas >= MAX_OFERTAS_POR_CICLO:
            break
        mensagem = formatar_mensagem(oferta)
        if enviar_telegram(mensagem):
            historico.append(oferta['id'])
            postadas += 1
            print(f"  ✅ {oferta['titulo'][:50]}")
            time.sleep(8)

    salvar_historico(historico)
    print(f"  Total: {postadas} oferta(s) postada(s).")

def main():
    print("="*50)
    print("  OFERTA NA VEIA BOT - v8 Lomadee")
    print(f"  API real de ofertas integrada!")
    print(f"  Intervalo: {INTERVALO_MINUTOS}min")
    print("="*50)
    if os.path.exists(HISTORICO_FILE):
        os.remove(HISTORICO_FILE)
        print("  Histórico limpo!")
    while True:
        try:
            rodar_ciclo()
        except Exception as e:
            print(f"  Erro: {e}")
        print(f"  Próxima busca em {INTERVALO_MINUTOS} min...")
        time.sleep(INTERVALO_MINUTOS * 60)

if __name__ == "__main__":
    main()
