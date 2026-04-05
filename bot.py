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
        separador = '&' if '?' in url else '?'
        url = f"{url}{separador}tag={AMAZON_TAG}"
    return url

def processar_link(url):
    try:
        resp = requests.head(url, allow_redirects=True, timeout=10)
        url_final = resp.url
    except:
        url_final = url
    if 'amazon.com.br' in url_final or 'amzn.to' in url_final:
        return adicionar_tag_amazon(url_final)
    return url_final

def buscar_ofertas_promobit():
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; OfertaBot/1.0)'}
    ofertas = []
    try:
        url = "https://www.promobit.com.br/feed/ofertas/rss.xml"
        resp = requests.get(url, headers=headers, timeout=15)
        root = ET.fromstring(resp.content)
        items = root.findall('.//item')[:20]
        for item in items:
            try:
                titulo = item.findtext('title', '').strip()
                link = item.findtext('link', '').strip()
                descricao = item.findtext('description', '').strip()
                if not titulo or not link:
                    continue
                preco = None
                preco_original = None
                desconto = 0
                preco_match = re.search(r'R\$\s*([\d.,]+)', descricao)
                if preco_match:
                    try:
                        preco = float(preco_match.group(1).replace('.','').replace(',','.'))
                    except:
                        pass
                de_match = re.search(r'[Dd]e[:\s]+R\$\s*([\d.,]+)', descricao)
                if de_match:
                    try:
                        preco_original = float(de_match.group(1).replace('.','').replace(',','.'))
                    except:
                        pass
                desc_match = re.search(r'(\d+)%\s*(?:de\s*)?[Dd]esconto', descricao)
                if desc_match:
                    desconto = int(desc_match.group(1))
                elif preco and preco_original and preco_original > preco:
                    desconto = round((1 - preco / preco_original) * 100)
                loja = 'Promobit'
                for nome in ['Amazon','Shopee','Mercado Livre','Magazine Luiza','Americanas','Casas Bahia']:
                    if nome.lower() in descricao.lower() or nome.lower() in titulo.lower():
                        loja = nome
                        break
                oferta_id = re.sub(r'[^a-z0-9]', '', titulo.lower())[:40]
                ofertas.append({'id': oferta_id, 'titulo': titulo, 'preco': preco, 'preco_original': preco_original, 'desconto': desconto, 'link': link, 'loja': loja})
            except Exception as e:
                print(f"  Erro item: {e}")
                continue
    except Exception as e:
        print(f"  Erro Promobit: {e}")
    return ofertas

def formatar_mensagem(oferta):
    titulo = oferta['titulo']
    loja = oferta['loja']
    link = oferta['link_afiliado']
    linhas = [f"🔥 *{titulo}*", ""]
    if oferta['preco']:
        preco_fmt = f"R$ {oferta['preco']:,.2f}".replace(',','X').replace('.',',').replace('X','.')
        linhas.append(f"💰 *Por apenas {preco_fmt}*")
        if oferta['preco_original'] and oferta['desconto'] > 0:
            orig_fmt = f"R$ {oferta['preco_original']:,.2f}".replace(',','X').replace('.',',').replace('X','.')
            linhas.append(f"~~De {orig_fmt}~~ → *{oferta['desconto']}% OFF* 🏷️")
    else:
        linhas.append("💰 *Preço imperdível — acesse e confira!*")
    linhas += ["", f"🏪 {loja}", "", f"👉 [PEGAR OFERTA]({link})", "", "━━━━━━━━━━━━━━━━━━", "📢 @ofertanaveiaoficial", "🔔 Ative as notificações!"]
    return "\n".join(linhas)

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {'chat_id': TELEGRAM_CHANNEL, 'text': mensagem, 'parse_mode': 'Markdown', 'disable_web_page_preview': False}
    try:
        resp = requests.post(url, json=payload, timeout=15)
        print(f"  Telegram status: {resp.status_code} | {resp.text[:100]}")
        return resp.status_code == 200
    except Exception as e:
        print(f"  Erro Telegram: {e}")
        return False

def rodar_ciclo():
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Buscando ofertas...")
    historico = carregar_historico()
    ofertas = buscar_ofertas_promobit()
    print(f"  Total encontrado: {len(ofertas)} ofertas")
    ofertas.sort(key=lambda x: x['desconto'], reverse=True)
    postadas = 0
    for oferta in ofertas:
        if postadas >= MAX_OFERTAS_POR_CICLO:
            break
        if oferta['id'] in historico:
            continue
        link_final = processar_link(oferta['link'])
        oferta['link_afiliado'] = link_final
        mensagem = formatar_mensagem(oferta)
        sucesso = enviar_telegram(mensagem)
        if sucesso:
            historico.append(oferta['id'])
            postadas += 1
            print(f"  Postado: {oferta['titulo'][:50]}...")
            time.sleep(5)
        else:
            print(f"  Falha: {oferta['titulo'][:50]}")
    salvar_historico(historico)
    print(f"  {postadas} oferta(s) postada(s).")

def main():
    print("="*50)
    print("  OFERTA NA VEIA BOT - Iniciando...")
    print("="*50)
    while True:
        try:
            rodar_ciclo()
        except Exception as e:
            print(f"  Erro ciclo: {e}")
        print(f"  Proxima busca em {INTERVALO_MINUTOS} minutos...")
        time.sleep(INTERVALO_MINUTOS * 60)

if __name__ == "__main__":
    main()
