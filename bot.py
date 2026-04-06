import requests
import json
import os
import time
import re
import xml.etree.ElementTree as ET
from datetime import datetime

TELEGRAM_TOKEN = "8744902004:AAHFshEgRNnSCc3DS5CoOCvMldrDaji-8GE"
TELEGRAM_CHANNEL = "@ofertanaveiaoficial"
AMAZON_TAG = "limacaioprado-20"
SHOPEE_ID = "lima.caioprado"
ML_ETIQUETA = "aehgdcfab53186"
INTERVALO_MINUTOS = 30
MAX_OFERTAS_POR_CICLO = 5
HISTORICO_FILE = "historico.json"

def carregar_historico():
    if os.path.exists(HISTORICO_FILE):
        with open(HISTORICO_FILE, "r") as f:
            return json.load(f)
    return []

def salvar_historico(historico):
    historico = historico[-500:]
    with open(HISTORICO_FILE, "w") as f:
        json.dump(historico, f)

def adicionar_tag_amazon(url):
    url = re.sub(r'tag=[^&]+', f'tag={AMAZON_TAG}', url)
    if 'tag=' not in url:
        sep = '&' if '?' in url else '?'
        url = f"{url}{sep}tag={AMAZON_TAG}"
    return url

def adicionar_tag_shopee(url):
    if 'shopee.com.br' in url:
        sep = '&' if '?' in url else '?'
        if 'af_siteid' not in url:
            url = f"{url}{sep}af_siteid={SHOPEE_ID}"
    return url

def adicionar_tag_ml(url):
    if 'mercadolivre.com.br' in url or 'meli.la' in url or 'mercadolibre.com' in url:
        sep = '&' if '?' in url else '?'
        if 'matt_tool' not in url:
            url = f"{url}{sep}matt_tool={ML_ETIQUETA}"
    return url

def processar_link(url):
    try:
        resp = requests.head(url, allow_redirects=True, timeout=10)
        url_final = resp.url
    except:
        url_final = url

    if 'amazon.com.br' in url_final or 'amzn.to' in url_final:
        return adicionar_tag_amazon(url_final)
    elif 'shopee.com.br' in url_final:
        return adicionar_tag_shopee(url_final)
    elif 'mercadolivre.com.br' in url_final or 'mercadolibre.com' in url_final:
        return adicionar_tag_ml(url_final)
    return url_final

def buscar_promobit():
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; OfertaBot/1.0)'}
    ofertas = []
    try:
        resp = requests.get("https://www.promobit.com.br/feed/ofertas/rss.xml", headers=headers, timeout=15)
        root = ET.fromstring(resp.content)
        for item in root.findall('.//item')[:25]:
            try:
                titulo = item.findtext('title', '').strip()
                link = item.findtext('link', '').strip()
                desc = item.findtext('description', '').strip()
                if not titulo or not link:
                    continue
                preco = None
                preco_original = None
                desconto = 0
                m = re.search(r'R\$\s*([\d.,]+)', desc)
                if m:
                    try: preco = float(m.group(1).replace('.','').replace(',','.'))
                    except: pass
                m2 = re.search(r'[Dd]e[:\s]+R\$\s*([\d.,]+)', desc)
                if m2:
                    try: preco_original = float(m2.group(1).replace('.','').replace(',','.'))
                    except: pass
                m3 = re.search(r'(\d+)%\s*(?:de\s*)?[Dd]esconto', desc)
                if m3:
                    desconto = int(m3.group(1))
                elif preco and preco_original and preco_original > preco:
                    desconto = round((1 - preco / preco_original) * 100)
                loja = 'Promobit'
                for nome in ['Amazon','Shopee','Mercado Livre','Magazine Luiza','Americanas','Casas Bahia','Kabum','Samsung','Apple']:
                    if nome.lower() in desc.lower() or nome.lower() in titulo.lower():
                        loja = nome
                        break
                oferta_id = re.sub(r'[^a-z0-9]', '', titulo.lower())[:40]
                ofertas.append({'id': oferta_id, 'titulo': titulo, 'preco': preco, 'preco_original': preco_original, 'desconto': desconto, 'link': link, 'loja': loja})
            except: continue
    except Exception as e:
        print(f"  Erro Promobit: {e}")
    return ofertas

def buscar_buscapes():
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; OfertaBot/1.0)'}
    ofertas = []
    try:
        resp = requests.get("https://www.buscape.com.br/feed/ofertas/rss.xml", headers=headers, timeout=15)
        root = ET.fromstring(resp.content)
        for item in root.findall('.//item')[:15]:
            try:
                titulo = item.findtext('title', '').strip()
                link = item.findtext('link', '').strip()
                desc = item.findtext('description', '').strip()
                if not titulo or not link:
                    continue
                preco = None
                m = re.search(r'R\$\s*([\d.,]+)', desc)
                if m:
                    try: preco = float(m.group(1).replace('.','').replace(',','.'))
                    except: pass
                oferta_id = re.sub(r'[^a-z0-9]', '', titulo.lower())[:40]
                ofertas.append({'id': oferta_id, 'titulo': titulo, 'preco': preco, 'preco_original': None, 'desconto': 0, 'link': link, 'loja': 'Buscapé'})
            except: continue
    except Exception as e:
        print(f"  Erro Buscapé: {e}")
    return ofertas

def emoji_loja(loja):
    mapa = {'Amazon': '📦', 'Shopee': '🛍️', 'Mercado Livre': '🟡', 'Magazine Luiza': '🛒', 'Americanas': '🔴', 'Casas Bahia': '🔵', 'Kabum': '🖥️', 'Samsung': '📱', 'Apple': '🍎'}
    return mapa.get(loja, '🏪')

def formatar_mensagem(oferta):
    titulo = oferta['titulo']
    loja = oferta['loja']
    link = oferta['link_afiliado']
    emoji = emoji_loja(loja)
    linhas = [f"🔥 *{titulo}*", ""]
    if oferta['preco']:
        preco_fmt = f"R$ {oferta['preco']:,.2f}".replace(',','X').replace('.',',').replace('X','.')
        linhas.append(f"💰 *Por apenas {preco_fmt}*")
        if oferta['preco_original'] and oferta['desconto'] > 0:
            orig_fmt = f"R$ {oferta['preco_original']:,.2f}".replace(',','X').replace('.',',').replace('X','.')
            linhas.append(f"~~De {orig_fmt}~~ → *{oferta['desconto']}% OFF* 🏷️")
    else:
        linhas.append("💰 *Preço imperdível — acesse e confira!*")
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
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Buscando ofertas...")
    historico = carregar_historico()
    ofertas = buscar_promobit()
    print(f"  Promobit: {len(ofertas)}")
    if len(ofertas) < 5:
        extras = buscar_buscapes()
        ofertas += extras
        print(f"  Buscapé: {len(extras)}")
    ofertas.sort(key=lambda x: x['desconto'], reverse=True)
    postadas = 0
    for oferta in ofertas:
        if postadas >= MAX_OFERTAS_POR_CICLO:
            break
        if oferta['id'] in historico:
            continue
        oferta['link_afiliado'] = processar_link(oferta['link'])
        mensagem = formatar_mensagem(oferta)
        if enviar_telegram(mensagem):
            historico.append(oferta['id'])
            postadas += 1
            print(f"  ✅ {oferta['titulo'][:50]}")
            time.sleep(5)
        else:
            print(f"  ❌ {oferta['titulo'][:50]}")
    salvar_historico(historico)
    print(f"  Total postado: {postadas}")

def main():
    print("="*50)
    print("  OFERTA NA VEIA BOT - Iniciando...")
    print(f"  Amazon: {AMAZON_TAG}")
    print(f"  Shopee: {SHOPEE_ID}")
    print(f"  ML: {ML_ETIQUETA}")
    print("="*50)
    while True:
        try:
            rodar_ciclo()
        except Exception as e:
            print(f"  Erro: {e}")
        print(f"  Proxima busca em {INTERVALO_MINUTOS} min...")
        time.sleep(INTERVALO_MINUTOS * 60)

if __name__ == "__main__":
    main()
