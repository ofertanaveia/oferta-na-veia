import requests
import json
import os
import time
import re
from datetime import datetime
from bs4 import BeautifulSoup

# ============================================================
#  CONFIGURAÇÕES - OFERTA NA VEIA BOT
# ============================================================
TELEGRAM_TOKEN = "8744902004:AAHFshEgRNnSCc3DS5CoOCvMldrDaji-8GE"
TELEGRAM_CHANNEL = "@ofertanaveiaoficial"
AMAZON_TAG = "limacaioprado-20"
INTERVALO_MINUTOS = 30       # A cada quantos minutos buscar ofertas
DESCONTO_MINIMO = 15         # % mínimo de desconto para postar
MAX_OFERTAS_POR_CICLO = 5    # Máximo de ofertas por rodada
HISTORICO_FILE = "historico.json"
# ============================================================

def carregar_historico():
    if os.path.exists(HISTORICO_FILE):
        with open(HISTORICO_FILE, "r") as f:
            return json.load(f)
    return []

def salvar_historico(historico):
    # Manter apenas os últimos 500 IDs
    historico = historico[-500:]
    with open(HISTORICO_FILE, "w") as f:
        json.dump(historico, f)

def adicionar_tag_amazon(url):
    """Adiciona ou substitui o tag de afiliado em links Amazon"""
    url = re.sub(r'tag=[^&]+', f'tag={AMAZON_TAG}', url)
    if 'tag=' not in url:
        separador = '&' if '?' in url else '?'
        url = f"{url}{separador}tag={AMAZON_TAG}"
    return url

def processar_link(url):
    """Resolve redirecionamentos e adiciona tag se for Amazon"""
    try:
        resp = requests.head(url, allow_redirects=True, timeout=10)
        url_final = resp.url
    except:
        url_final = url

    if 'amazon.com.br' in url_final or 'amzn.to' in url_final:
        return adicionar_tag_amazon(url_final)
    return url_final

def buscar_ofertas_pelando():
    """Busca ofertas quentes no Pelando"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    ofertas = []
    try:
        url = "https://www.pelando.com.br/mais-quentes"
        resp = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(resp.text, 'html.parser')

        items = soup.select('article[data-testid="thread-card"]')[:20]

        for item in items:
            try:
                titulo_el = item.select_one('[data-testid="thread-card-title"]')
                preco_el = item.select_one('[data-testid="thread-price"]')
                preco_orig_el = item.select_one('[data-testid="thread-original-price"]')
                link_el = item.select_one('a[href]')
                temp_el = item.select_one('[data-testid="temperature"]')
                img_el = item.select_one('img')
                loja_el = item.select_one('[data-testid="thread-merchant"]')

                if not titulo_el or not link_el:
                    continue

                titulo = titulo_el.get_text(strip=True)
                link = "https://www.pelando.com.br" + link_el['href'] if link_el['href'].startswith('/') else link_el['href']
                temperatura = int(temp_el.get_text(strip=True).replace('°', '').replace('+', '').strip()) if temp_el else 0
                imagem = img_el.get('src', '') if img_el else ''
                loja = loja_el.get_text(strip=True) if loja_el else 'Loja'

                preco = None
                preco_original = None
                desconto = 0

                if preco_el:
                    preco_txt = preco_el.get_text(strip=True).replace('R$', '').replace('.', '').replace(',', '.').strip()
                    try:
                        preco = float(preco_txt)
                    except:
                        pass

                if preco_orig_el:
                    orig_txt = preco_orig_el.get_text(strip=True).replace('R$', '').replace('.', '').replace(',', '.').strip()
                    try:
                        preco_original = float(orig_txt)
                    except:
                        pass

                if preco and preco_original and preco_original > preco:
                    desconto = round((1 - preco / preco_original) * 100)

                # Filtrar por desconto ou temperatura alta
                if desconto >= DESCONTO_MINIMO or temperatura >= 100:
                    oferta_id = re.sub(r'[^a-z0-9]', '', titulo.lower())[:40]
                    ofertas.append({
                        'id': oferta_id,
                        'titulo': titulo,
                        'preco': preco,
                        'preco_original': preco_original,
                        'desconto': desconto,
                        'link': link,
                        'temperatura': temperatura,
                        'imagem': imagem,
                        'loja': loja
                    })
            except Exception as e:
                continue

    except Exception as e:
        print(f"Erro ao buscar Pelando: {e}")

    return ofertas

def formatar_mensagem(oferta):
    """Formata a mensagem para o Telegram"""
    titulo = oferta['titulo']
    loja = oferta['loja']
    temperatura = oferta['temperatura']
    link = oferta['link_afiliado']

    linhas = []
    linhas.append(f"🔥 *{titulo}*")
    linhas.append("")

    if oferta['preco']:
        preco_fmt = f"R$ {oferta['preco']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        linhas.append(f"💰 *Por apenas {preco_fmt}*")

        if oferta['preco_original'] and oferta['desconto'] > 0:
            orig_fmt = f"R$ {oferta['preco_original']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            linhas.append(f"~~De {orig_fmt}~~ → *{oferta['desconto']}% OFF* 🏷️")
    else:
        linhas.append("💰 *Preço imperdível!*")

    linhas.append("")
    linhas.append(f"🏪 {loja}")
    linhas.append(f"🌡️ {temperatura}° de temperatura")
    linhas.append("")
    linhas.append(f"👉 [PEGAR OFERTA]({link})")
    linhas.append("")
    linhas.append("━━━━━━━━━━━━━━━━━━")
    linhas.append("📢 @ofertanaveiaoficial")
    linhas.append("💬 Ative as notificações 🔔")

    return "\n".join(linhas)

def enviar_telegram(mensagem, imagem=None):
    """Envia mensagem para o canal do Telegram"""
    base_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

    if imagem:
        try:
            url = f"{base_url}/sendPhoto"
            payload = {
                'chat_id': TELEGRAM_CHANNEL,
                'photo': imagem,
                'caption': mensagem,
                'parse_mode': 'Markdown'
            }
            resp = requests.post(url, json=payload, timeout=15)
            if resp.status_code == 200:
                return True
        except:
            pass

    # Fallback: texto simples
    url = f"{base_url}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHANNEL,
        'text': mensagem,
        'parse_mode': 'Markdown',
        'disable_web_page_preview': False
    }
    resp = requests.post(url, json=payload, timeout=15)
    return resp.status_code == 200

def rodar_ciclo():
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🔍 Buscando ofertas...")
    historico = carregar_historico()
    ofertas = buscar_ofertas_pelando()

    # Ordenar por desconto + temperatura
    ofertas.sort(key=lambda x: (x['desconto'] * 0.7 + x['temperatura'] * 0.3), reverse=True)

    postadas = 0
    for oferta in ofertas:
        if postadas >= MAX_OFERTAS_POR_CICLO:
            break

        if oferta['id'] in historico:
            continue

        # Resolver link e adicionar afiliado
        link_final = processar_link(oferta['link'])
        oferta['link_afiliado'] = link_final

        mensagem = formatar_mensagem(oferta)
        sucesso = enviar_telegram(mensagem, oferta.get('imagem'))

        if sucesso:
            historico.append(oferta['id'])
            postadas += 1
            print(f"  ✅ Postado: {oferta['titulo'][:50]}...")
            time.sleep(3)  # Pausa entre posts
        else:
            print(f"  ❌ Erro ao postar: {oferta['titulo'][:50]}")

    salvar_historico(historico)
    print(f"  📊 {postadas} oferta(s) postada(s) neste ciclo.")

def main():
    print("=" * 50)
    print("  🔥 OFERTA NA VEIA BOT - Iniciando...")
    print("=" * 50)
    print(f"  Canal: {TELEGRAM_CHANNEL}")
    print(f"  Tag Amazon: {AMAZON_TAG}")
    print(f"  Intervalo: {INTERVALO_MINUTOS} minutos")
    print(f"  Desconto mínimo: {DESCONTO_MINIMO}%")
    print("=" * 50)

    while True:
        try:
            rodar_ciclo()
        except Exception as e:
            print(f"  ⚠️ Erro no ciclo: {e}")

        print(f"  ⏳ Próxima busca em {INTERVALO_MINUTOS} minutos...")
        time.sleep(INTERVALO_MINUTOS * 60)

if __name__ == "__main__":
    main()
