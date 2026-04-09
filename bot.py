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

def gerar_ofertas():
    t = AMAZON_TAG
    m = ML_ETIQUETA
    return [
        {'titulo': 'Kindle 11 Geracao 16GB com Luz Embutida', 'preco': 399.00, 'preco_original': 599.00, 'desconto': 33, 'link': f'https://www.amazon.com.br/dp/B09SWS1R73?tag={t}', 'loja': 'Amazon'},
        {'titulo': 'Echo Dot 5 Geracao Smart Speaker Alexa', 'preco': 299.00, 'preco_original': 499.00, 'desconto': 40, 'link': f'https://www.amazon.com.br/dp/B09B8RVKGW?tag={t}', 'loja': 'Amazon'},
        {'titulo': 'Fire TV Stick 4K Controle Alexa', 'preco': 299.00, 'preco_original': 499.00, 'desconto': 40, 'link': f'https://www.amazon.com.br/dp/B08XVYZ1Y5?tag={t}', 'loja': 'Amazon'},
        {'titulo': 'Caixa de Som JBL Go 3 Bluetooth Portatil', 'preco': 149.90, 'preco_original': 249.90, 'desconto': 40, 'link': f'https://www.amazon.com.br/dp/B08KMQ9GWN?tag={t}', 'loja': 'Amazon'},
        {'titulo': 'Fone JBL Tune 510BT Bluetooth 40h Bateria', 'preco': 199.90, 'preco_original': 349.90, 'desconto': 43, 'link': f'https://www.amazon.com.br/dp/B08WM3FVPZ?tag={t}', 'loja': 'Amazon'},
        {'titulo': 'SSD Interno Kingston 480GB SATA III', 'preco': 149.90, 'preco_original': 279.90, 'desconto': 46, 'link': f'https://www.amazon.com.br/dp/B01N5IIA6W?tag={t}', 'loja': 'Amazon'},
        {'titulo': 'Headset HyperX Cloud Stinger Gamer', 'preco': 199.90, 'preco_original': 349.90, 'desconto': 43, 'link': f'https://www.amazon.com.br/dp/B01LWZ8EGF?tag={t}', 'loja': 'Amazon'},
        {'titulo': 'HD Externo Seagate Expansion 1TB USB 3.0', 'preco': 299.00, 'preco_original': 499.00, 'desconto': 40, 'link': f'https://www.amazon.com.br/dp/B00TKFEEAS?tag={t}', 'loja': 'Amazon'},
        {'titulo': 'Webcam Logitech C920 Full HD 1080p', 'preco': 399.00, 'preco_original': 699.00, 'desconto': 43, 'link': f'https://www.amazon.com.br/dp/B006A2Q81M?tag={t}', 'loja': 'Amazon'},
        {'titulo': 'Camera Instax Mini 12 Fujifilm', 'preco': 499.00, 'preco_original': 799.00, 'desconto': 38, 'link': f'https://www.amazon.com.br/dp/B0BQMVNKL4?tag={t}', 'loja': 'Amazon'},
        {'titulo': 'Powerbank Anker 20000mAh Carregamento Rapido', 'preco': 299.90, 'preco_original': 499.90, 'desconto': 40, 'link': f'https://www.amazon.com.br/dp/B09VPHVT2Z?tag={t}', 'loja': 'Amazon'},
        {'titulo': 'Carregador Anker 65W USB-C GaN Compacto', 'preco': 199.90, 'preco_original': 349.90, 'desconto': 43, 'link': f'https://www.amazon.com.br/dp/B09C7SLHFP?tag={t}', 'loja': 'Amazon'},
        {'titulo': 'Garrafa Termica Stanley Classic 1L', 'preco': 249.90, 'preco_original': 449.90, 'desconto': 44, 'link': f'https://www.amazon.com.br/dp/B08TFX1MJL?tag={t}', 'loja': 'Amazon'},
        {'titulo': 'Cafeteira Nespresso Essenza Mini Preta', 'preco': 399.90, 'preco_original': 699.90, 'desconto': 43, 'link': f'https://www.amazon.com.br/dp/B07Q4NKBVD?tag={t}', 'loja': 'Amazon'},
        {'titulo': 'Escova Dental Eletrica Oral-B Pro 1', 'preco': 149.90, 'preco_original': 299.90, 'desconto': 50, 'link': f'https://www.amazon.com.br/dp/B00J3AFBD2?tag={t}', 'loja': 'Amazon'},
        {'titulo': 'Protetor Solar Neutrogena Sun Fresh FPS 70', 'preco': 49.90, 'preco_original': 89.90, 'desconto': 44, 'link': f'https://www.amazon.com.br/dp/B07H4DGKQX?tag={t}', 'loja': 'Amazon'},
        {'titulo': 'Livro Pai Rico Pai Pobre Edicao Especial', 'preco': 39.90, 'preco_original': 79.90, 'desconto': 50, 'link': f'https://www.amazon.com.br/dp/8550801488?tag={t}', 'loja': 'Amazon'},
        {'titulo': 'Livro O Poder do Habito Charles Duhigg', 'preco': 34.90, 'preco_original': 69.90, 'desconto': 50, 'link': f'https://www.amazon.com.br/dp/8539004119?tag={t}', 'loja': 'Amazon'},
        {'titulo': 'Livro Mindset Carol Dweck Psicologia do Sucesso', 'preco': 39.90, 'preco_original': 79.90, 'desconto': 50, 'link': f'https://www.amazon.com.br/dp/8543107539?tag={t}', 'loja': 'Amazon'},
        {'titulo': 'Whey Protein Gold Standard 1.8kg Chocolate', 'preco': 299.90, 'preco_original': 499.90, 'desconto': 40, 'link': f'https://www.amazon.com.br/dp/B000GIQT2G?tag={t}', 'loja': 'Amazon'},
        {'titulo': 'Suporte Ergonomico para Notebook Ajustavel', 'preco': 89.90, 'preco_original': 179.90, 'desconto': 50, 'link': f'https://www.amazon.com.br/dp/B07KDDKDH1?tag={t}', 'loja': 'Amazon'},
        {'titulo': 'Mouse sem Fio Logitech MX Master 3S', 'preco': 549.00, 'preco_original': 899.00, 'desconto': 39, 'link': f'https://www.amazon.com.br/dp/B09HM94VDS?tag={t}', 'loja': 'Amazon'},
        {'titulo': 'Liquidificador Oster 1200W Pro Series', 'preco': 199.90, 'preco_original': 349.90, 'desconto': 43, 'link': f'https://www.amazon.com.br/dp/B07ZNWLJKY?tag={t}', 'loja': 'Amazon'},
        {'titulo': 'Chaleira Eletrica Tramontina 1.7L Inox', 'preco': 99.90, 'preco_original': 189.90, 'desconto': 47, 'link': f'https://www.amazon.com.br/dp/B07XQTHDRJ?tag={t}', 'loja': 'Amazon'},
        {'titulo': 'Echo Show 5 3 Geracao Tela 5.5 Alexa', 'preco': 499.00, 'preco_original': 799.00, 'desconto': 38, 'link': f'https://www.amazon.com.br/dp/B09B2SBHQK?tag={t}', 'loja': 'Amazon'},
        {'titulo': 'Air Fryer Britania 4L Digital Touch Screen', 'preco': 249.90, 'preco_original': 449.90, 'desconto': 44, 'link': f'https://produto.mercadolivre.com.br/MLB-2769789500?matt_tool={m}', 'loja': 'Mercado Livre'},
        {'titulo': 'Smartphone Motorola Moto G84 256GB 5G', 'preco': 1299.00, 'preco_original': 2199.00, 'desconto': 41, 'link': f'https://produto.mercadolivre.com.br/MLB-2557173700?matt_tool={m}', 'loja': 'Mercado Livre'},
        {'titulo': 'Smart TV Samsung 50 Crystal 4K UHD 2024', 'preco': 1999.00, 'preco_original': 3499.00, 'desconto': 43, 'link': f'https://produto.mercadolivre.com.br/MLB-2088244500?matt_tool={m}', 'loja': 'Mercado Livre'},
        {'titulo': 'Fritadeira Air Fryer Philips Walita 6.2L XL', 'preco': 699.00, 'preco_original': 1199.00, 'desconto': 42, 'link': f'https://produto.mercadolivre.com.br/MLB-883686200?matt_tool={m}', 'loja': 'Mercado Livre'},
        {'titulo': 'Robo Aspirador Multilaser 1800Pa WiFi App', 'preco': 799.00, 'preco_original': 1499.00, 'desconto': 47, 'link': f'https://produto.mercadolivre.com.br/MLB-2706484300?matt_tool={m}', 'loja': 'Mercado Livre'},
        {'titulo': 'Tenis Nike Revolution 7 Masculino Corrida', 'preco': 249.90, 'preco_original': 449.90, 'desconto': 44, 'link': f'https://produto.mercadolivre.com.br/MLB-2918743200?matt_tool={m}', 'loja': 'Mercado Livre'},
        {'titulo': 'Micro-ondas Electrolux 31L MTD41 Branco', 'preco': 599.00, 'preco_original': 999.00, 'desconto': 40, 'link': f'https://produto.mercadolivre.com.br/MLB-978263400?matt_tool={m}', 'loja': 'Mercado Livre'},
        {'titulo': 'Notebook Dell Inspiron 15 i5 8GB 256GB SSD', 'preco': 2799.00, 'preco_original': 4299.00, 'desconto': 35, 'link': f'https://produto.mercadolivre.com.br/MLB-2347628100?matt_tool={m}', 'loja': 'Mercado Livre'},
        {'titulo': 'Console Nintendo Switch OLED Branco 64GB', 'preco': 2399.00, 'preco_original': 3199.00, 'desconto': 25, 'link': f'https://produto.mercadolivre.com.br/MLB-2198789200?matt_tool={m}', 'loja': 'Mercado Livre'},
        {'titulo': 'Ferro de Passar Philips Vapor 1400W', 'preco': 149.90, 'preco_original': 279.90, 'desconto': 46, 'link': f'https://produto.mercadolivre.com.br/MLB-1572638400?matt_tool={m}', 'loja': 'Mercado Livre'},
    ]

def formatar_mensagem(oferta):
    titulo = oferta['titulo']
    loja = oferta['loja']
    link = oferta['link']
    preco = oferta['preco']
    preco_original = oferta['preco_original']
    desconto = oferta['desconto']
    emoji_map = {'Amazon': 'P', 'Mercado Livre': 'ML'}
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
    print("  OFERTA NA VEIA BOT - v11")
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
