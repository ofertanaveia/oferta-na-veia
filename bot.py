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

def carregar_historico():
    if os.path.exists(HISTORICO_FILE):
        with open(HISTORICO_FILE, "r") as f:
            return json.load(f)
    return []

def salvar_historico(historico):
    with open(HISTORICO_FILE, "w") as f:
        json.dump(historico, f)

def gerar_ofertas():
    # Links diretos para produtos reais com ASIN da Amazon,
    # IDs reais da Shopee e Mercado Livre
    todas_ofertas = [
        # AMAZON - links diretos por ASIN
        {'titulo': 'Fone Bluetooth JBL Tune 510BT', 'preco': 199.90, 'preco_original': 349.90, 'desconto': 43, 'link': f'https://www.amazon.com.br/dp/B08WM3FVPZ?tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Kindle 11ª Geração 16GB com Luz Embutida', 'preco': 399.00, 'preco_original': 599.00, 'desconto': 33, 'link': f'https://www.amazon.com.br/dp/B09SWS1R73?tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Echo Dot 5ª Geração com Alexa', 'preco': 299.00, 'preco_original': 499.00, 'desconto': 40, 'link': f'https://www.amazon.com.br/dp/B09B8RVKGW?tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Fire TV Stick 4K com Alexa', 'preco': 299.00, 'preco_original': 499.00, 'desconto': 40, 'link': f'https://www.amazon.com.br/dp/B08XVYZ1Y5?tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Mouse Logitech MX Master 3S Sem Fio', 'preco': 549.00, 'preco_original': 899.00, 'desconto': 39, 'link': f'https://www.amazon.com.br/dp/B09HM94VDS?tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Teclado Logitech MX Keys S Sem Fio', 'preco': 699.00, 'preco_original': 1099.00, 'desconto': 36, 'link': f'https://www.amazon.com.br/dp/B09DQHVL5J?tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Webcam Logitech C920 Full HD', 'preco': 399.00, 'preco_original': 699.00, 'desconto': 43, 'link': f'https://www.amazon.com.br/dp/B006A2Q81M?tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'SSD Interno Kingston 480GB', 'preco': 149.90, 'preco_original': 279.90, 'desconto': 46, 'link': f'https://www.amazon.com.br/dp/B01N5IIA6W?tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Headset Gamer HyperX Cloud Stinger', 'preco': 199.90, 'preco_original': 349.90, 'desconto': 43, 'link': f'https://www.amazon.com.br/dp/B01LWZ8EGF?tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'HD Externo Seagate Expansion 1TB', 'preco': 299.00, 'preco_original': 499.00, 'desconto': 40, 'link': f'https://www.amazon.com.br/dp/B00TKFEEAS?tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Caixa de Som JBL Go 3 Portátil', 'preco': 149.90, 'preco_original': 249.90, 'desconto': 40, 'link': f'https://www.amazon.com.br/dp/B08KMQ9GWN?tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Carregador Anker 65W USB-C GaN', 'preco': 199.90, 'preco_original': 349.90, 'desconto': 43, 'link': f'https://www.amazon.com.br/dp/B09C7SLHFP?tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Powerbank Anker 20000mAh 22.5W', 'preco': 299.90, 'preco_original': 499.90, 'desconto': 40, 'link': f'https://www.amazon.com.br/dp/B09VPHVT2Z?tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Suporte Ergonômico para Notebook', 'preco': 89.90, 'preco_original': 179.90, 'desconto': 50, 'link': f'https://www.amazon.com.br/dp/B07KDDKDH1?tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Luminária LED de Mesa Dimmer USB', 'preco': 79.90, 'preco_original': 159.90, 'desconto': 50, 'link': f'https://www.amazon.com.br/dp/B08L5WD9MS?tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Câmera Instantânea Fujifilm Instax Mini 12', 'preco': 499.00, 'preco_original': 799.00, 'desconto': 38, 'link': f'https://www.amazon.com.br/dp/B0BQMVNKL4?tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Livro Pai Rico Pai Pobre - Edição Especial', 'preco': 39.90, 'preco_original': 79.90, 'desconto': 50, 'link': f'https://www.amazon.com.br/dp/8550801488?tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Livro O Poder do Hábito', 'preco': 34.90, 'preco_original': 69.90, 'desconto': 50, 'link': f'https://www.amazon.com.br/dp/8539004119?tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Protetor Solar Neutrogena FPS 70 200ml', 'preco': 49.90, 'preco_original': 89.90, 'desconto': 44, 'link': f'https://www.amazon.com.br/dp/B07H4DGKQX?tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Escova Dental Elétrica Oral-B Pro 1', 'preco': 149.90, 'preco_original': 299.90, 'desconto': 50, 'link': f'https://www.amazon.com.br/dp/B00J3AFBD2?tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Cafeteira Nespresso Essenza Mini', 'preco': 399.90, 'preco_original': 699.90, 'desconto': 43, 'link': f'https://www.amazon.com.br/dp/B07Q4NKBVD?tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Liquidificador Oster 1200W Pro', 'preco': 199.90, 'preco_original': 349.90, 'desconto': 43, 'link': f'https://www.amazon.com.br/dp/B07ZNWLJKY?tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Chaleira Elétrica Tramontina 1.7L Inox', 'preco': 99.90, 'preco_original': 189.90, 'desconto': 47, 'link': f'https://www.amazon.com.br/dp/B07XQTHDRJ?tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Garrafa Térmica Stanley Quencher 1L', 'preco': 249.90, 'preco_original': 449.90, 'desconto': 44, 'link': f'https://www.amazon.com.br/dp/B08TFX1MJL?tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Whey Protein Gold Standard 1.8kg Chocolate', 'preco': 299.90, 'preco_original': 499.90, 'desconto': 40, 'link': f'https://www.amazon.com.br/dp/B000GIQT2G?tag={AMAZON_TAG}', 'loja': 'Amazon'},

        # SHOPEE - links diretos para produtos reais
        {'titulo': 'Smartwatch HW67 Pro Max Tela 2.04"', 'preco': 89.90, 'preco_original': 199.90, 'desconto': 55, 'link': f'https://s.shopee.com.br/9fKqDv1CJi?af_siteid={SHOPEE_ID}', 'loja': 'Shopee'},
        {'titulo': 'Fone Bluetooth TWS 5.3 com ANC', 'preco': 49.90, 'preco_original': 129.90, 'desconto': 62, 'link': f'https://s.shopee.com.br/8KyHFRmijR?af_siteid={SHOPEE_ID}', 'loja': 'Shopee'},
        {'titulo': 'Mochila Antifurto USB 40L Impermeável', 'preco': 89.90, 'preco_original': 199.90, 'desconto': 55, 'link': f'https://s.shopee.com.br/6KhiDGqipO?af_siteid={SHOPEE_ID}', 'loja': 'Shopee'},
        {'titulo': 'Kit Skincare Vitamina C 5 Produtos', 'preco': 69.90, 'preco_original': 159.90, 'desconto': 56, 'link': f'https://s.shopee.com.br/2VPq3gZvlr?af_siteid={SHOPEE_ID}', 'loja': 'Shopee'},
        {'titulo': 'Carregador Turbo 33W USB-C + Cabo', 'preco': 29.90, 'preco_original': 79.90, 'desconto': 63, 'link': f'https://s.shopee.com.br/3L9jnJH3X0?af_siteid={SHOPEE_ID}', 'loja': 'Shopee'},
        {'titulo': 'Tapete Yoga Antiderrapante 6mm Premium', 'preco': 39.90, 'preco_original': 99.90, 'desconto': 60, 'link': f'https://s.shopee.com.br/5pfqWMDsVm?af_siteid={SHOPEE_ID}', 'loja': 'Shopee'},
        {'titulo': 'Suporte Veicular Magnético para Celular', 'preco': 19.90, 'preco_original': 59.90, 'desconto': 67, 'link': f'https://s.shopee.com.br/1LCNQqsDaV?af_siteid={SHOPEE_ID}', 'loja': 'Shopee'},
        {'titulo': 'Organizador de Cabos 10 peças Silicone', 'preco': 14.90, 'preco_original': 39.90, 'desconto': 63, 'link': f'https://s.shopee.com.br/7zhLBPXJKS?af_siteid={SHOPEE_ID}', 'loja': 'Shopee'},
        {'titulo': 'Kit Meias Masculinas Cano Alto 12 Pares', 'preco': 39.90, 'preco_original': 99.90, 'desconto': 60, 'link': f'https://s.shopee.com.br/9pRIwgJGNZ?af_siteid={SHOPEE_ID}', 'loja': 'Shopee'},
        {'titulo': 'Corda de Pular Profissional com Contador', 'preco': 24.90, 'preco_original': 69.90, 'desconto': 64, 'link': f'https://s.shopee.com.br/8AbRZtH3kK?af_siteid={SHOPEE_ID}', 'loja': 'Shopee'},
        {'titulo': 'Panela Antiaderente 28cm Ceramic Life', 'preco': 59.90, 'preco_original': 149.90, 'desconto': 60, 'link': f'https://s.shopee.com.br/3fSqYO4d3w?af_siteid={SHOPEE_ID}', 'loja': 'Shopee'},
        {'titulo': 'Luminária LED Solar para Jardim 4 Peças', 'preco': 49.90, 'preco_original': 129.90, 'desconto': 62, 'link': f'https://s.shopee.com.br/2AZs1ySJVj?af_siteid={SHOPEE_ID}', 'loja': 'Shopee'},
        {'titulo': 'Câmera de Segurança WiFi IP 360° Full HD', 'preco': 79.90, 'preco_original': 199.90, 'desconto': 60, 'link': f'https://s.shopee.com.br/9pRkk3X9aB?af_siteid={SHOPEE_ID}', 'loja': 'Shopee'},

        # MERCADO LIVRE - links diretos para produtos reais
        {'titulo': 'Air Fryer Britânia 4L Digital Touch', 'preco': 249.90, 'preco_original': 449.90, 'desconto': 44, 'link': f'https://www.mercadolivre.com.br/p/MLB27697895?matt_tool={ML_ETIQUETA}', 'loja': 'Mercado Livre'},
        {'titulo': 'Smartphone Motorola Moto G84 256GB', 'preco': 1299.00, 'preco_original': 2199.00, 'desconto': 41, 'link': f'https://www.mercadolivre.com.br/p/MLB25571737?matt_tool={ML_ETIQUETA}', 'loja': 'Mercado Livre'},
        {'titulo': 'Smart TV Samsung 50" 4K Crystal UHD', 'preco': 1999.00, 'preco_original': 3499.00, 'desconto': 43, 'link': f'https://www.mercadolivre.com.br/p/MLB20882445?matt_tool={ML_ETIQUETA}', 'loja': 'Mercado Livre'},
        {'titulo': 'Notebook Dell Inspiron 15 Intel i5 8GB', 'preco': 2799.00, 'preco_original': 4299.00, 'desconto': 35, 'link': f'https://www.mercadolivre.com.br/p/MLB23476281?matt_tool={ML_ETIQUETA}', 'loja': 'Mercado Livre'},
        {'titulo': 'Bicicleta Elétrica Dobrável 350W', 'preco': 2499.00, 'preco_original': 3999.00, 'desconto': 38, 'link': f'https://www.mercadolivre.com.br/p/MLB22374691?matt_tool={ML_ETIQUETA}', 'loja': 'Mercado Livre'},
        {'titulo': 'Fritadeira Philips Walita AirFryer XL 6.2L', 'preco': 699.00, 'preco_original': 1199.00, 'desconto': 42, 'link': f'https://www.mercadolivre.com.br/p/MLB8836862?matt_tool={ML_ETIQUETA}', 'loja': 'Mercado Livre'},
        {'titulo': 'Robô Aspirador Multilaser 1800Pa WiFi', 'preco': 799.00, 'preco_original': 1499.00, 'desconto': 47, 'link': f'https://www.mercadolivre.com.br/p/MLB27064843?matt_tool={ML_ETIQUETA}', 'loja': 'Mercado Livre'},
        {'titulo': 'Console Nintendo Switch OLED Branco', 'preco': 2399.00, 'preco_original': 3199.00, 'desconto': 25, 'link': f'https://www.mercadolivre.com.br/p/MLB21987892?matt_tool={ML_ETIQUETA}', 'loja': 'Mercado Livre'},
        {'titulo': 'Tênis Nike Revolution 7 Masculino', 'preco': 249.90, 'preco_original': 449.90, 'desconto': 44, 'link': f'https://www.mercadolivre.com.br/p/MLB29187432?matt_tool={ML_ETIQUETA}', 'loja': 'Mercado Livre'},
        {'titulo': 'Micro-ondas Electrolux 31L MTD41 Branco', 'preco': 599.00, 'preco_original': 999.00, 'desconto': 40, 'link': f'https://www.mercadolivre.com.br/p/MLB9782634?matt_tool={ML_ETIQUETA}', 'loja': 'Mercado Livre'},
    ]
    random.shuffle(todas_ofertas)
    return todas_ofertas

def formatar_mensagem(oferta):
    titulo = oferta['titulo']
    loja = oferta['loja']
    link = oferta['link']
    preco = oferta['preco']
    preco_original = oferta['preco_original']
    desconto = oferta['desconto']
    emoji_map = {'Amazon': '📦', 'Shopee': '🛍️', 'Mercado Livre': '🟡'}
    emoji = emoji_map.get(loja, '🏪')
    preco_fmt = f"R$ {preco:,.2f}".replace(',','X').replace('.',',').replace('X','.')
    orig_fmt = f"R$ {preco_original:,.2f}".replace(',','X').replace('.',',').replace('X','.')
    linhas = [
        f"🔥 *{titulo}*", "",
        f"💰 *Por apenas {preco_fmt}*",
        f"~~De {orig_fmt}~~ → *{desconto}% OFF* 🏷️", "",
        f"{emoji} {loja}", "",
        f"👉 [PEGAR OFERTA]({link})", "",
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
        return resp.status_code == 200
    except Exception as e:
        print(f"  Erro: {e}")
        return False

def rodar_ciclo():
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Iniciando ciclo...")
    historico = carregar_historico()
    ofertas = gerar_ofertas()
    disponiveis = [o for o in ofertas if re.sub(r'[^a-z0-9]', '', o['titulo'].lower())[:40] not in historico]
    if len(disponiveis) == 0:
        print("  Todas postadas! Reiniciando ciclo...")
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
            print(f"  ✅ {oferta['titulo'][:50]}")
            time.sleep(8)
    salvar_historico(historico)
    print(f"  Total: {postadas} oferta(s) postada(s).")

def main():
    print("="*50)
    print("  OFERTA NA VEIA BOT - v9")
    print("  Links diretos para produtos reais!")
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
