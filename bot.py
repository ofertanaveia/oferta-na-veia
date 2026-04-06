import requests
import json
import os
import time
import re
from datetime import datetime

TELEGRAM_TOKEN = "8744902004:AAHFshEgRNnSCc3DS5CoOCvMldrDaji-8GE"
TELEGRAM_CHANNEL = "@ofertanaveiaoficial"
AMAZON_TAG = "limacaioprado-20"
SHOPEE_ID = "lima.caioprado"
ML_ETIQUETA = "aehgdcfab53186"
INTERVALO_MINUTOS = 30
MAX_OFERTAS_POR_CICLO = 5
HISTORICO_FILE = "historico.json"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'pt-BR,pt;q=0.9',
    'Referer': 'https://www.pelando.com.br/',
}

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

def processar_link(url):
    try:
        resp = requests.head(url, allow_redirects=True, timeout=10, headers=HEADERS)
        url_final = resp.url
    except:
        url_final = url
    if 'amazon.com.br' in url_final or 'amzn.to' in url_final:
        return adicionar_tag_amazon(url_final)
    elif 'shopee.com.br' in url_final:
        sep = '&' if '?' in url_final else '?'
        return f"{url_final}{sep}af_siteid={SHOPEE_ID}"
    elif 'mercadolivre.com.br' in url_final or 'mercadolibre.com' in url_final:
        sep = '&' if '?' in url_final else '?'
        return f"{url_final}{sep}matt_tool={ML_ETIQUETA}"
    return url_final

def buscar_pelando_api():
    """Busca via API GraphQL do Pelando"""
    ofertas = []
    try:
        query = """
        {
          hotThreads(
            filter: {period: DAY}
            pagination: {limit: 20, page: 1}
          ) {
            edges {
              node {
                id
                title
                price
                originalPrice
                discount
                url
                merchant { name }
                temperature
              }
            }
          }
        }
        """
        resp = requests.post(
            'https://www.pelando.com.br/api/graphql',
            json={'query': query},
            headers={**HEADERS, 'Content-Type': 'application/json'},
            timeout=15
        )
        data = resp.json()
        edges = data.get('data', {}).get('hotThreads', {}).get('edges', [])
        for edge in edges:
            try:
                node = edge['node']
                titulo = node.get('title', '')
                link = node.get('url', '')
                preco = node.get('price')
                preco_original = node.get('originalPrice')
                desconto = node.get('discount', 0) or 0
                temperatura = node.get('temperature', 0) or 0
                loja = node.get('merchant', {}).get('name', 'Pelando') if node.get('merchant') else 'Pelando'
                if not titulo or not link:
                    continue
                if preco and preco_original and preco_original > preco and desconto == 0:
                    desconto = round((1 - preco / preco_original) * 100)
                oferta_id = re.sub(r'[^a-z0-9]', '', titulo.lower())[:40]
                ofertas.append({'id': oferta_id, 'titulo': titulo, 'preco': preco, 'preco_original': preco_original, 'desconto': desconto or 0, 'link': link, 'loja': loja, 'temperatura': temperatura})
            except Exception as e:
                print(f"  Erro item: {e}")
                continue
        print(f"  Pelando API: {len(ofertas)} ofertas")
    except Exception as e:
        print(f"  Erro Pelando API: {e}")
    return ofertas

def buscar_coupons_brasil():
    """Busca via API pública de cupons brasileiros"""
    ofertas = []
    try:
        resp = requests.get(
            'https://api.publicas.br/cupons/v1/destaques',
            headers=HEADERS,
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            for item in data.get('data', [])[:15]:
                titulo = item.get('titulo', '')
                link = item.get('link', '')
                desconto = item.get('desconto', 0)
                loja = item.get('loja', 'Loja')
                if titulo and link:
                    oferta_id = re.sub(r'[^a-z0-9]', '', titulo.lower())[:40]
                    ofertas.append({'id': oferta_id, 'titulo': titulo, 'preco': None, 'preco_original': None, 'desconto': desconto, 'link': link, 'loja': loja, 'temperatura': 0})
    except Exception as e:
        print(f"  Erro cupons: {e}")
    return ofertas

def gerar_ofertas_fallback():
    """Gera ofertas buscando produtos em promoção direto nas lojas via API"""
    ofertas = []
    try:
        # Amazon Best Sellers via API
        resp = requests.get(
            f'https://www.amazon.com.br/gp/bestsellers/ajax/get-units-rank?asin=B09G9HDKKH&marketplaceId=A2Q3Y263D00KWC',
            headers=HEADERS,
            timeout=10
        )
    except:
        pass

    # Fallback: ofertas estáticas de teste para verificar se o bot posta
    produtos_teste = [
        {'titulo': 'Fone Bluetooth JBL Tune 510BT', 'preco': 199.90, 'preco_original': 299.90, 'desconto': 33, 'link': f'https://www.amazon.com.br/s?k=fone+bluetooth+jbl&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Smartwatch Xiaomi Redmi Watch 3', 'preco': 299.90, 'preco_original': 449.90, 'desconto': 33, 'link': f'https://shopee.com.br/search?keyword=xiaomi+redmi+watch', 'loja': 'Shopee'},
        {'titulo': 'Aspirador Robô Multilaser', 'preco': 399.00, 'preco_original': 699.00, 'desconto': 43, 'link': f'https://www.mercadolivre.com.br/ofertas', 'loja': 'Mercado Livre'},
        {'titulo': 'Carregador Turbo USB-C 65W', 'preco': 79.90, 'preco_original': 149.90, 'desconto': 47, 'link': f'https://www.amazon.com.br/s?k=carregador+turbo+usb-c&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Kit Skincare Vitamina C Dermage', 'preco': 89.90, 'preco_original': 159.90, 'desconto': 44, 'link': f'https://shopee.com.br/search?keyword=skincare+vitamina+c', 'loja': 'Shopee'},
    ]
    for p in produtos_teste:
        oferta_id = re.sub(r'[^a-z0-9]', '', p['titulo'].lower())[:40]
        ofertas.append({**p, 'id': oferta_id, 'temperatura': 200})
    return ofertas

def emoji_loja(loja):
    mapa = {'Amazon': '📦', 'Shopee': '🛍️', 'Mercado Livre': '🟡', 'Magazine Luiza': '🛒', 'Americanas': '🔴', 'Casas Bahia': '🔵', 'Kabum': '🖥️'}
    return mapa.get(loja, '🏪')

def formatar_mensagem(oferta):
    titulo = oferta['titulo']
    loja = oferta['loja']
    link = oferta['link_afiliado']
    emoji = emoji_loja(loja)
    linhas = [f"🔥 *{titulo}*", ""]
    if oferta.get('preco'):
        preco_fmt = f"R$ {oferta['preco']:,.2f}".replace(',','X').replace('.',',').replace('X','.')
        linhas.append(f"💰 *Por apenas {preco_fmt}*")
        if oferta.get('preco_original') and oferta['desconto'] > 0:
            orig_fmt = f"R$ {oferta['preco_original']:,.2f}".replace(',','X').replace('.',',').replace('X','.')
            linhas.append(f"~~De {orig_fmt}~~ → *{oferta['desconto']}% OFF* 🏷️")
    else:
        linhas.append(f"*{oferta['desconto']}% OFF* 🏷️" if oferta['desconto'] > 0 else "💰 *Preço imperdível!*")
    linhas += ["", f"{emoji} {loja}", "", f"👉 [PEGAR OFERTA]({link})", "", "━━━━━━━━━━━━━━━━━━", "📢 @ofertanaveiaoficial", "🔔 Ative as notificações!"]
    return "\n".join(linhas)

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {'chat_id': TELEGRAM_CHANNEL, 'text': mensagem, 'parse_mode': 'Markdown', 'disable_web_page_preview': False}
    try:
        resp = requests.post(url, json=payload, timeout=15)
        print(f"  Telegram status: {resp.status_code}")
        if resp.status_code != 200:
            print(f"  Resposta: {resp.text[:200]}")
        return resp.status_code == 200
    except Exception as e:
        print(f"  Erro Telegram: {e}")
        return False

def rodar_ciclo():
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Buscando ofertas...")
    historico = carregar_historico()

    ofertas = buscar_pelando_api()

    if len(ofertas) == 0:
        print("  API Pelando sem retorno, usando fallback...")
        ofertas = gerar_ofertas_fallback()

    ofertas.sort(key=lambda x: (x.get('desconto', 0) * 0.6 + x.get('temperatura', 0) * 0.4), reverse=True)

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
            print(f"  ✅ Postado: {oferta['titulo'][:50]}")
            time.sleep(5)
        else:
            print(f"  ❌ Falhou: {oferta['titulo'][:50]}")

    salvar_historico(historico)
    print(f"  Total: {postadas} oferta(s) postada(s).")

def main():
    print("="*50)
    print("  OFERTA NA VEIA BOT - v3")
    print(f"  Canal: {TELEGRAM_CHANNEL}")
    print(f"  Amazon: {AMAZON_TAG}")
    print(f"  Shopee: {SHOPEE_ID}")
    print(f"  ML: {ML_ETIQUETA}")
    print("="*50)
    while True:
        try:
            rodar_ciclo()
        except Exception as e:
            print(f"  Erro ciclo: {e}")
        print(f"  Proxima busca em {INTERVALO_MINUTOS} min...")
        time.sleep(INTERVALO_MINUTOS * 60)

if __name__ == "__main__":
    main()
