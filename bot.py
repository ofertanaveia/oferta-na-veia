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

def buscar_lomadee():
    ofertas = []
    endpoints = [
        f"https://api.lomadee.com/v3/{LOMADEE_TOKEN}/offer/_search?sourceId={LOMADEE_SOURCE}&size=50&sort=discount&order=desc",
        f"https://api.lomadee.com/v3/{LOMADEE_TOKEN}/offer/_all?sourceId={LOMADEE_SOURCE}&size=50",
    ]
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Accept': 'application/json',
        'Accept-Language': 'pt-BR,pt;q=0.9',
    }
    for url in endpoints:
        try:
            print(f"  Tentando: {url[:80]}...")
            resp = requests.get(url, headers=headers, timeout=20)
            print(f"  Status: {resp.status_code}")
            if resp.status_code == 200:
                data = resp.json()
                print(f"  Keys: {list(data.keys())}")
                # Tenta diferentes estruturas de resposta
                items = (data.get('offers') or data.get('offer') or
                        data.get('data', {}).get('offers') or [])
                if isinstance(items, dict):
                    items = items.get('offer', [])
                print(f"  Ofertas encontradas: {len(items)}")
                for item in items:
                    try:
                        titulo = item.get('name') or item.get('nome') or ''
                        link = item.get('link') or item.get('url') or ''
                        preco = float(item.get('price') or item.get('preco') or 0)
                        preco_original = float(item.get('priceFrom') or item.get('precoOriginal') or 0)
                        desconto = int(item.get('discount') or item.get('desconto') or 0)
                        loja_data = item.get('store') or item.get('loja') or {}
                        loja = loja_data.get('name') or loja_data.get('nome') or 'Loja' if isinstance(loja_data, dict) else 'Loja'
                        if not titulo or not link or desconto < 5:
                            continue
                        if preco_original == 0 and preco > 0 and desconto > 0:
                            preco_original = round(preco / (1 - desconto/100), 2)
                        oferta_id = re.sub(r'[^a-z0-9]', '', titulo.lower())[:40]
                        ofertas.append({
                            'id': oferta_id,
                            'titulo': titulo,
                            'preco': preco,
                            'preco_original': preco_original,
                            'desconto': desconto,
                            'link': link,
                            'loja': loja
                        })
                    except:
                        continue
                if ofertas:
                    break
            else:
                print(f"  Resposta: {resp.text[:300]}")
        except Exception as e:
            print(f"  Erro: {e}")
    return ofertas

def ofertas_fallback():
    AMAZON_TAG = "limacaioprado-20"
    SHOPEE_ID = "lima.caioprado"
    ML_ETIQUETA = "aehgdcfab53186"
    return [
        {'id': 'kindlegeracao16gb', 'titulo': 'Kindle 11ª Geração 16GB com Luz', 'preco': 399.00, 'preco_original': 599.00, 'desconto': 33, 'link': f'https://www.amazon.com.br/dp/B09SWS1R73?tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'id': 'echodot5geracao', 'titulo': 'Echo Dot 5ª Geração com Alexa', 'preco': 299.00, 'preco_original': 499.00, 'desconto': 40, 'link': f'https://www.amazon.com.br/dp/B09B8RVKGW?tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'id': 'jblgo3portatil', 'titulo': 'Caixa de Som JBL Go 3 Portátil', 'preco': 149.90, 'preco_original': 249.90, 'desconto': 40, 'link': f'https://www.amazon.com.br/dp/B08KMQ9GWN?tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'id': 'ssdinternokingston', 'titulo': 'SSD Interno Kingston 480GB', 'preco': 149.90, 'preco_original': 279.90, 'desconto': 46, 'link': f'https://www.amazon.com.br/dp/B01N5IIA6W?tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'id': 'smartwatchhw67pro', 'titulo': 'Smartwatch HW67 Pro Max Tela 2.04"', 'preco': 89.90, 'preco_original': 199.90, 'desconto': 55, 'link': f'https://s.shopee.com.br/9fKqDv1CJi?af_siteid={SHOPEE_ID}', 'loja': 'Shopee'},
        {'id': 'airfryerbritania4l', 'titulo': 'Air Fryer Britânia 4L Digital', 'preco': 249.90, 'preco_original': 449.90, 'desconto': 44, 'link': f'https://www.mercadolivre.com.br/p/MLB27697895?matt_tool={ML_ETIQUETA}', 'loja': 'Mercado Livre'},
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
        print(f"  Erro: {e}")
        return False

def rodar_ciclo():
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Buscando ofertas Lomadee...")
    historico = carregar_historico()
    ofertas = buscar_lomadee()
    if len(ofertas) == 0:
        print("  Usando fallback...")
        ofertas = ofertas_fallback()
    random.shuffle(ofertas)
    disponiveis = [o for o in ofertas if o['id'] not in historico]
    if len(disponiveis) == 0:
        print("  Reiniciando ciclo...")
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
    print("  OFERTA NA VEIA BOT - v10 Lomadee Pro")
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
