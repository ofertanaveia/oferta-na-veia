import requests
import json
import os
import time
import re
from datetime import datetime
import random

TELEGRAM_TOKEN = "8744902004:AAHFshEgRNnSCc3DS5CoOCvMldrDaji-8GE"
TELEGRAM_CHANNEL = "@ofertanaveiaoficial"
AMAZON_TAG = "limacaioprado-20"
SHOPEE_ID = "lima.caioprado"
ML_ETIQUETA = "aehgdcfab53186"
INTERVALO_MINUTOS = 15
MAX_OFERTAS_POR_CICLO = 3
HISTORICO_FILE = "historico.json"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'application/json',
    'Accept-Language': 'pt-BR,pt;q=0.9',
}

def carregar_historico():
    if os.path.exists(HISTORICO_FILE):
        with open(HISTORICO_FILE, "r") as f:
            return json.load(f)
    return []

def salvar_historico(historico):
    historico = historico[-200:]
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
    elif 'mercadolivre.com.br' in url_final:
        sep = '&' if '?' in url_final else '?'
        return f"{url_final}{sep}matt_tool={ML_ETIQUETA}"
    return url_final

def gerar_ofertas():
    """Banco de ofertas rotativas para garantir postagem"""
    todas_ofertas = [
        {'titulo': 'Fone Bluetooth JBL Tune 510BT - Som Incrível', 'preco': 199.90, 'preco_original': 349.90, 'desconto': 43, 'link': f'https://www.amazon.com.br/s?k=fone+jbl+tune+510bt&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Smartwatch Xiaomi Redmi Watch 3 Active', 'preco': 249.90, 'preco_original': 399.90, 'desconto': 38, 'link': f'https://shopee.com.br/search?keyword=xiaomi+redmi+watch+3', 'loja': 'Shopee'},
        {'titulo': 'Carregador Turbo 65W USB-C GaN', 'preco': 69.90, 'preco_original': 149.90, 'desconto': 53, 'link': f'https://www.amazon.com.br/s?k=carregador+turbo+65w+usb-c&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Aspirador Robô Inteligente com Mapeamento', 'preco': 699.00, 'preco_original': 1299.00, 'desconto': 46, 'link': f'https://www.mercadolivre.com.br/ofertas', 'loja': 'Mercado Livre'},
        {'titulo': 'Fritadeira Air Fryer 4L Philips Walita', 'preco': 299.90, 'preco_original': 499.90, 'desconto': 40, 'link': f'https://www.amazon.com.br/s?k=air+fryer+philips+walita&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Kit Skincare Vitamina C Completo', 'preco': 89.90, 'preco_original': 179.90, 'desconto': 50, 'link': f'https://shopee.com.br/search?keyword=kit+skincare+vitamina+c', 'loja': 'Shopee'},
        {'titulo': 'Tênis Nike Air Max SC Masculino', 'preco': 299.99, 'preco_original': 499.99, 'desconto': 40, 'link': f'https://www.amazon.com.br/s?k=nike+air+max+sc&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Mochila Antifurto USB 40L Impermeável', 'preco': 119.90, 'preco_original': 229.90, 'desconto': 48, 'link': f'https://shopee.com.br/search?keyword=mochila+antifurto+usb', 'loja': 'Shopee'},
        {'titulo': 'SSD Kingston 480GB SATA III 2.5"', 'preco': 149.90, 'preco_original': 279.90, 'desconto': 46, 'link': f'https://www.amazon.com.br/s?k=ssd+kingston+480gb&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Cafeteira Nespresso Essenza Mini', 'preco': 399.90, 'preco_original': 699.90, 'desconto': 43, 'link': f'https://www.mercadolivre.com.br/ofertas', 'loja': 'Mercado Livre'},
        {'titulo': 'Caixa de Som JBL Go 3 Portátil', 'preco': 149.90, 'preco_original': 249.90, 'desconto': 40, 'link': f'https://www.amazon.com.br/s?k=jbl+go+3&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Tablet Samsung Galaxy Tab A9 64GB WiFi', 'preco': 999.00, 'preco_original': 1599.00, 'desconto': 38, 'link': f'https://shopee.com.br/search?keyword=samsung+galaxy+tab+a9', 'loja': 'Shopee'},
        {'titulo': 'Mouse Gamer Logitech G203 8000 DPI', 'preco': 149.90, 'preco_original': 249.90, 'desconto': 40, 'link': f'https://www.amazon.com.br/s?k=logitech+g203&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Panela de Pressão Elétrica 6L Digital', 'preco': 199.90, 'preco_original': 399.90, 'desconto': 50, 'link': f'https://shopee.com.br/search?keyword=panela+pressao+eletrica+6l', 'loja': 'Shopee'},
        {'titulo': 'Câmera de Segurança WiFi Full HD 1080p', 'preco': 89.90, 'preco_original': 179.90, 'desconto': 50, 'link': f'https://www.mercadolivre.com.br/ofertas', 'loja': 'Mercado Livre'},
        {'titulo': 'Headset Gamer HyperX Cloud Stinger', 'preco': 199.90, 'preco_original': 349.90, 'desconto': 43, 'link': f'https://www.amazon.com.br/s?k=hyperx+cloud+stinger&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Perfume Importado Calvin Klein Eternity 100ml', 'preco': 299.90, 'preco_original': 549.90, 'desconto': 45, 'link': f'https://shopee.com.br/search?keyword=calvin+klein+eternity', 'loja': 'Shopee'},
        {'titulo': 'Kindle 11ª Geração 16GB com Luz Embutida', 'preco': 399.00, 'preco_original': 599.00, 'desconto': 33, 'link': f'https://www.amazon.com.br/s?k=kindle+11+geracao&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Ferro de Passar Roupa a Vapor Philips', 'preco': 149.90, 'preco_original': 299.90, 'desconto': 50, 'link': f'https://www.mercadolivre.com.br/ofertas', 'loja': 'Mercado Livre'},
        {'titulo': 'Notebook Lenovo IdeaPad 15 Intel Core i5', 'preco': 2499.00, 'preco_original': 3999.00, 'desconto': 38, 'link': f'https://www.amazon.com.br/s?k=notebook+lenovo+ideapad+i5&tag={AMAZON_TAG}', 'loja': 'Amazon'},
    ]
    random.shuffle(todas_ofertas)
    return todas_ofertas

def emoji_loja(loja):
    mapa = {'Amazon': '📦', 'Shopee': '🛍️', 'Mercado Livre': '🟡'}
    return mapa.get(loja, '🏪')

def formatar_mensagem(oferta):
    titulo = oferta['titulo']
    loja = oferta['loja']
    link = oferta['link_afiliado']
    emoji = emoji_loja(loja)
    preco_fmt = f"R$ {oferta['preco']:,.2f}".replace(',','X').replace('.',',').replace('X','.')
    orig_fmt = f"R$ {oferta['preco_original']:,.2f}".replace(',','X').replace('.',',').replace('X','.')
    linhas = [
        f"🔥 *{titulo}*",
        "",
        f"💰 *Por apenas {preco_fmt}*",
        f"~~De {orig_fmt}~~ → *{oferta['desconto']}% OFF* 🏷️",
        "",
        f"{emoji} {loja}",
        "",
        f"👉 [PEGAR OFERTA]({link})",
        "",
        "━━━━━━━━━━━━━━━━━━",
        "📢 @ofertanaveiaoficial",
        "🔔 Ative as notificações!"
    ]
    return "\n".join(linhas)

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {'chat_id': TELEGRAM_CHANNEL, 'text': mensagem, 'parse_mode': 'Markdown', 'disable_web_page_preview': False}
    try:
        resp = requests.post(url, json=payload, timeout=15)
        print(f"  Telegram: {resp.status_code}")
        if resp.status_code != 200:
            print(f"  Erro: {resp.text[:150]}")
        return resp.status_code == 200
    except Exception as e:
        print(f"  Erro Telegram: {e}")
        return False

def rodar_ciclo():
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Iniciando ciclo...")
    historico = carregar_historico()
    ofertas = gerar_ofertas()
    postadas = 0

    for oferta in ofertas:
        if postadas >= MAX_OFERTAS_POR_CICLO:
            break
        oferta_id = re.sub(r'[^a-z0-9]', '', oferta['titulo'].lower())[:40]
        if oferta_id in historico:
            continue
        oferta['link_afiliado'] = processar_link(oferta['link'])
        mensagem = formatar_mensagem(oferta)
        if enviar_telegram(mensagem):
            historico.append(oferta_id)
            postadas += 1
            print(f"  ✅ {oferta['titulo'][:50]}")
            time.sleep(8)

    salvar_historico(historico)
    print(f"  Total: {postadas} oferta(s) postada(s).")

def main():
    print("="*50)
    print("  OFERTA NA VEIA BOT - v4")
    print(f"  Canal: {TELEGRAM_CHANNEL}")
    print(f"  Intervalo: {INTERVALO_MINUTOS} minutos")
    print("="*50)
    
    # Limpar histórico ao iniciar para garantir postagem
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
