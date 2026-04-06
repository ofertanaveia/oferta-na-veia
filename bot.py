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
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json',
    'Accept-Language': 'pt-BR,pt;q=0.9',
}

def carregar_historico():
    if os.path.exists(HISTORICO_FILE):
        with open(HISTORICO_FILE, "r") as f:
            return json.load(f)
    return []

def salvar_historico(historico):
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
    todas_ofertas = [
        {'titulo': 'Fone Bluetooth JBL Tune 510BT', 'preco': 199.90, 'preco_original': 349.90, 'desconto': 43, 'link': f'https://www.amazon.com.br/s?k=fone+jbl+tune+510bt&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Smartwatch Xiaomi Redmi Watch 3 Active', 'preco': 249.90, 'preco_original': 399.90, 'desconto': 38, 'link': f'https://shopee.com.br/search?keyword=xiaomi+redmi+watch+3', 'loja': 'Shopee'},
        {'titulo': 'Carregador Turbo 65W USB-C GaN', 'preco': 69.90, 'preco_original': 149.90, 'desconto': 53, 'link': f'https://www.amazon.com.br/s?k=carregador+turbo+65w&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'SSD Kingston 480GB SATA III', 'preco': 149.90, 'preco_original': 279.90, 'desconto': 46, 'link': f'https://www.amazon.com.br/s?k=ssd+kingston+480gb&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Caixa de Som JBL Go 3 Portátil', 'preco': 149.90, 'preco_original': 249.90, 'desconto': 40, 'link': f'https://www.amazon.com.br/s?k=jbl+go+3&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Mouse Gamer Logitech G203 8000 DPI', 'preco': 149.90, 'preco_original': 249.90, 'desconto': 40, 'link': f'https://www.amazon.com.br/s?k=logitech+g203&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Headset Gamer HyperX Cloud Stinger', 'preco': 199.90, 'preco_original': 349.90, 'desconto': 43, 'link': f'https://www.amazon.com.br/s?k=hyperx+cloud+stinger&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Kindle 11ª Geração 16GB com Luz', 'preco': 399.00, 'preco_original': 599.00, 'desconto': 33, 'link': f'https://www.amazon.com.br/s?k=kindle+11+geracao&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Tablet Samsung Galaxy Tab A9 64GB', 'preco': 999.00, 'preco_original': 1599.00, 'desconto': 38, 'link': f'https://shopee.com.br/search?keyword=samsung+galaxy+tab+a9', 'loja': 'Shopee'},
        {'titulo': 'Notebook Lenovo IdeaPad Intel Core i5', 'preco': 2499.00, 'preco_original': 3999.00, 'desconto': 38, 'link': f'https://www.amazon.com.br/s?k=notebook+lenovo+ideapad+i5&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Câmera de Segurança WiFi Full HD 1080p', 'preco': 89.90, 'preco_original': 179.90, 'desconto': 50, 'link': f'https://www.mercadolivre.com.br/ofertas', 'loja': 'Mercado Livre'},
        {'titulo': 'Teclado Mecânico Gamer Redragon Kumara', 'preco': 199.90, 'preco_original': 349.90, 'desconto': 43, 'link': f'https://www.amazon.com.br/s?k=teclado+redragon+kumara&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Monitor LG 24" Full HD IPS', 'preco': 799.00, 'preco_original': 1299.00, 'desconto': 38, 'link': f'https://www.amazon.com.br/s?k=monitor+lg+24+full+hd&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Pen Drive Kingston 64GB USB 3.0', 'preco': 29.90, 'preco_original': 59.90, 'desconto': 50, 'link': f'https://www.amazon.com.br/s?k=pen+drive+kingston+64gb&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Webcam Full HD 1080p com Microfone', 'preco': 99.90, 'preco_original': 199.90, 'desconto': 50, 'link': f'https://shopee.com.br/search?keyword=webcam+full+hd+1080p', 'loja': 'Shopee'},
        {'titulo': 'Impressora HP DeskJet Ink Advantage', 'preco': 349.00, 'preco_original': 599.00, 'desconto': 42, 'link': f'https://www.amazon.com.br/s?k=impressora+hp+deskjet&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'HD Externo Seagate 1TB USB 3.0', 'preco': 299.00, 'preco_original': 499.00, 'desconto': 40, 'link': f'https://www.amazon.com.br/s?k=hd+externo+seagate+1tb&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Roteador WiFi 6 TP-Link AX1500', 'preco': 299.90, 'preco_original': 499.90, 'desconto': 40, 'link': f'https://www.amazon.com.br/s?k=roteador+tp-link+ax1500&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Caixa de Som Bluetooth Anker Soundcore', 'preco': 179.90, 'preco_original': 299.90, 'desconto': 40, 'link': f'https://www.amazon.com.br/s?k=anker+soundcore&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Controle PS5 DualSense Branco', 'preco': 399.00, 'preco_original': 599.00, 'desconto': 33, 'link': f'https://www.amazon.com.br/s?k=controle+ps5+dualsense&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Air Fryer 4L Philips Walita', 'preco': 299.90, 'preco_original': 499.90, 'desconto': 40, 'link': f'https://www.amazon.com.br/s?k=air+fryer+philips&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Cafeteira Nespresso Essenza Mini', 'preco': 399.90, 'preco_original': 699.90, 'desconto': 43, 'link': f'https://www.mercadolivre.com.br/ofertas', 'loja': 'Mercado Livre'},
        {'titulo': 'Panela de Pressão Elétrica 6L Digital', 'preco': 199.90, 'preco_original': 399.90, 'desconto': 50, 'link': f'https://shopee.com.br/search?keyword=panela+pressao+eletrica', 'loja': 'Shopee'},
        {'titulo': 'Aspirador Robô com Mapeamento Inteligente', 'preco': 699.00, 'preco_original': 1299.00, 'desconto': 46, 'link': f'https://www.mercadolivre.com.br/ofertas', 'loja': 'Mercado Livre'},
        {'titulo': 'Ferro de Passar Roupa a Vapor Philips', 'preco': 149.90, 'preco_original': 299.90, 'desconto': 50, 'link': f'https://www.mercadolivre.com.br/ofertas', 'loja': 'Mercado Livre'},
        {'titulo': 'Liquidificador Oster 1200W 3 Velocidades', 'preco': 149.90, 'preco_original': 279.90, 'desconto': 46, 'link': f'https://www.amazon.com.br/s?k=liquidificador+oster+1200w&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Jogo de Panelas Antiaderente 5 Peças', 'preco': 199.90, 'preco_original': 399.90, 'desconto': 50, 'link': f'https://shopee.com.br/search?keyword=jogo+panelas+antiaderente', 'loja': 'Shopee'},
        {'titulo': 'Purificador de Ar Electrolux PA31F', 'preco': 499.00, 'preco_original': 899.00, 'desconto': 44, 'link': f'https://www.amazon.com.br/s?k=purificador+ar+electrolux&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Jogo de Cama King Plumasul 200 Fios', 'preco': 99.90, 'preco_original': 199.90, 'desconto': 50, 'link': f'https://shopee.com.br/search?keyword=jogo+cama+king+200+fios', 'loja': 'Shopee'},
        {'titulo': 'Ventilador de Mesa Arno 40cm Silence Force', 'preco': 149.90, 'preco_original': 269.90, 'desconto': 44, 'link': f'https://www.amazon.com.br/s?k=ventilador+arno+silence+force&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Kit Skincare Vitamina C Completo', 'preco': 89.90, 'preco_original': 179.90, 'desconto': 50, 'link': f'https://shopee.com.br/search?keyword=kit+skincare+vitamina+c', 'loja': 'Shopee'},
        {'titulo': 'Perfume Calvin Klein Eternity 100ml', 'preco': 299.90, 'preco_original': 549.90, 'desconto': 45, 'link': f'https://shopee.com.br/search?keyword=calvin+klein+eternity', 'loja': 'Shopee'},
        {'titulo': 'Secador de Cabelo Taiff Style 2100W', 'preco': 129.90, 'preco_original': 249.90, 'desconto': 48, 'link': f'https://www.amazon.com.br/s?k=secador+taiff+2100w&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Kit Shampoo e Condicionador Elseve', 'preco': 49.90, 'preco_original': 99.90, 'desconto': 50, 'link': f'https://shopee.com.br/search?keyword=kit+shampoo+condicionador+elseve', 'loja': 'Shopee'},
        {'titulo': 'Protetor Solar Neutrogena FPS 70 200ml', 'preco': 49.90, 'preco_original': 89.90, 'desconto': 44, 'link': f'https://www.amazon.com.br/s?k=protetor+solar+neutrogena+fps70&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Escova Dental Elétrica Oral-B Pro 1', 'preco': 149.90, 'preco_original': 299.90, 'desconto': 50, 'link': f'https://www.amazon.com.br/s?k=oral-b+pro+1&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Tênis Nike Air Max SC Masculino', 'preco': 299.99, 'preco_original': 499.99, 'desconto': 40, 'link': f'https://www.amazon.com.br/s?k=nike+air+max+sc&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Mochila Antifurto USB 40L Impermeável', 'preco': 119.90, 'preco_original': 229.90, 'desconto': 48, 'link': f'https://shopee.com.br/search?keyword=mochila+antifurto+usb', 'loja': 'Shopee'},
        {'titulo': 'Relógio Masculino Casio Digital Esportivo', 'preco': 199.90, 'preco_original': 349.90, 'desconto': 43, 'link': f'https://www.amazon.com.br/s?k=casio+digital+esportivo&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Tênis Feminino Adidas Cloudfoam', 'preco': 199.90, 'preco_original': 349.90, 'desconto': 43, 'link': f'https://shopee.com.br/search?keyword=adidas+cloudfoam+feminino', 'loja': 'Shopee'},
        {'titulo': 'Carteira Masculina de Couro Legítimo', 'preco': 59.90, 'preco_original': 119.90, 'desconto': 50, 'link': f'https://shopee.com.br/search?keyword=carteira+masculina+couro', 'loja': 'Shopee'},
        {'titulo': 'Óculos de Sol Ray-Ban Wayfarer', 'preco': 399.90, 'preco_original': 699.90, 'desconto': 43, 'link': f'https://www.amazon.com.br/s?k=ray-ban+wayfarer&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Bolsa Feminina Couro Sintético Transversal', 'preco': 79.90, 'preco_original': 159.90, 'desconto': 50, 'link': f'https://shopee.com.br/search?keyword=bolsa+feminina+transversal', 'loja': 'Shopee'},
        {'titulo': 'Kit Meias Masculinas 12 Pares', 'preco': 39.90, 'preco_original': 89.90, 'desconto': 56, 'link': f'https://shopee.com.br/search?keyword=kit+meias+masculinas+12+pares', 'loja': 'Shopee'},
        {'titulo': 'Box Harry Potter Edição Especial 7 Livros', 'preco': 199.90, 'preco_original': 399.90, 'desconto': 50, 'link': f'https://www.amazon.com.br/s?k=box+harry+potter&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Livro Pai Rico Pai Pobre Robert Kiyosaki', 'preco': 39.90, 'preco_original': 79.90, 'desconto': 50, 'link': f'https://www.amazon.com.br/s?k=pai+rico+pai+pobre&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Agenda Planner 2025 Capa Dura', 'preco': 29.90, 'preco_original': 69.90, 'desconto': 57, 'link': f'https://shopee.com.br/search?keyword=agenda+planner+2025', 'loja': 'Shopee'},
        {'titulo': 'Livro O Poder do Hábito Charles Duhigg', 'preco': 34.90, 'preco_original': 69.90, 'desconto': 50, 'link': f'https://www.amazon.com.br/s?k=o+poder+do+habito&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Kit Canetas Stabilo Boss 6 Cores', 'preco': 29.90, 'preco_original': 59.90, 'desconto': 50, 'link': f'https://shopee.com.br/search?keyword=stabilo+boss+6+cores', 'loja': 'Shopee'},
        {'titulo': 'Kit Halteres 2kg + 4kg + 6kg Emborrachados', 'preco': 149.90, 'preco_original': 299.90, 'desconto': 50, 'link': f'https://shopee.com.br/search?keyword=kit+halteres+emborrachados', 'loja': 'Shopee'},
        {'titulo': 'Corda de Pular Speed Jump 3 Metros', 'preco': 29.90, 'preco_original': 69.90, 'desconto': 57, 'link': f'https://shopee.com.br/search?keyword=corda+pular+speed', 'loja': 'Shopee'},
        {'titulo': 'Tapete Yoga Antiderrapante 6mm', 'preco': 49.90, 'preco_original': 99.90, 'desconto': 50, 'link': f'https://shopee.com.br/search?keyword=tapete+yoga+antiderrapante', 'loja': 'Shopee'},
        {'titulo': 'Whey Protein Isolado Growth 900g', 'preco': 99.90, 'preco_original': 199.90, 'desconto': 50, 'link': f'https://www.amazon.com.br/s?k=whey+protein+isolado+growth&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Garrafa Térmica Stanley 1L Original', 'preco': 149.90, 'preco_original': 299.90, 'desconto': 50, 'link': f'https://www.amazon.com.br/s?k=garrafa+termica+stanley&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'LEGO Classic Caixa de Ideias 790 Peças', 'preco': 299.90, 'preco_original': 549.90, 'desconto': 45, 'link': f'https://www.amazon.com.br/s?k=lego+classic+caixa+ideias&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Boneca Barbie Fashionista Articulada', 'preco': 79.90, 'preco_original': 149.90, 'desconto': 47, 'link': f'https://www.amazon.com.br/s?k=barbie+fashionista&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Carrinho Hot Wheels Kit com 10 Unidades', 'preco': 79.90, 'preco_original': 159.90, 'desconto': 50, 'link': f'https://shopee.com.br/search?keyword=hot+wheels+kit+10', 'loja': 'Shopee'},
        {'titulo': 'Jogo de Tabuleiro Detetive Estrela', 'preco': 79.90, 'preco_original': 159.90, 'desconto': 50, 'link': f'https://www.amazon.com.br/s?k=detetive+jogo+estrela&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Ração Premium Royal Canin Cães 15kg', 'preco': 299.90, 'preco_original': 499.90, 'desconto': 40, 'link': f'https://www.amazon.com.br/s?k=royal+canin+caes+15kg&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Arranhador para Gatos com Brinquedo', 'preco': 79.90, 'preco_original': 159.90, 'desconto': 50, 'link': f'https://shopee.com.br/search?keyword=arranhador+gatos+brinquedo', 'loja': 'Shopee'},
        {'titulo': 'Suporte Veicular Celular Magnético 360°', 'preco': 29.90, 'preco_original': 69.90, 'desconto': 57, 'link': f'https://shopee.com.br/search?keyword=suporte+celular+carro+magnetico', 'loja': 'Shopee'},
        {'titulo': 'Carregador Veicular Duplo USB-C 36W', 'preco': 39.90, 'preco_original': 89.90, 'desconto': 56, 'link': f'https://www.amazon.com.br/s?k=carregador+veicular+usb-c+36w&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Furadeira de Impacto Bosch 550W', 'preco': 299.90, 'preco_original': 499.90, 'desconto': 40, 'link': f'https://www.amazon.com.br/s?k=furadeira+bosch+550w&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Kit Ferramentas 127 Peças Tramontina', 'preco': 199.90, 'preco_original': 399.90, 'desconto': 50, 'link': f'https://www.amazon.com.br/s?k=kit+ferramentas+tramontina&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Memória RAM Kingston 16GB DDR4 3200MHz', 'preco': 199.90, 'preco_original': 349.90, 'desconto': 43, 'link': f'https://www.amazon.com.br/s?k=memoria+ram+kingston+16gb&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Mousepad Gamer Extra Grande 90x40cm', 'preco': 49.90, 'preco_original': 99.90, 'desconto': 50, 'link': f'https://shopee.com.br/search?keyword=mousepad+gamer+90x40', 'loja': 'Shopee'},
        {'titulo': 'Hub USB-C 7 em 1 Multiporta 4K', 'preco': 89.90, 'preco_original': 179.90, 'desconto': 50, 'link': f'https://www.amazon.com.br/s?k=hub+usb-c+7+em+1&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Powerbank 20000mAh Anker Carregamento Rápido', 'preco': 199.90, 'preco_original': 399.90, 'desconto': 50, 'link': f'https://www.amazon.com.br/s?k=powerbank+anker+20000mah&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Cabo USB-C 2 Metros Carga Rápida 5A', 'preco': 19.90, 'preco_original': 49.90, 'desconto': 60, 'link': f'https://shopee.com.br/search?keyword=cabo+usb-c+carga+rapida+5a', 'loja': 'Shopee'},
        {'titulo': 'Capinha iPhone 15 Pro Silicone Premium', 'preco': 29.90, 'preco_original': 69.90, 'desconto': 57, 'link': f'https://shopee.com.br/search?keyword=capinha+iphone+15+pro+silicone', 'loja': 'Shopee'},
        {'titulo': 'Suporte de Mesa para Celular Ajustável', 'preco': 29.90, 'preco_original': 69.90, 'desconto': 57, 'link': f'https://shopee.com.br/search?keyword=suporte+mesa+celular', 'loja': 'Shopee'},
        {'titulo': 'Bicicleta Ergométrica Magnética Kikos', 'preco': 899.00, 'preco_original': 1599.00, 'desconto': 44, 'link': f'https://www.mercadolivre.com.br/ofertas', 'loja': 'Mercado Livre'},
        {'titulo': 'Esteira Elétrica Residencial Kikos E10', 'preco': 1999.00, 'preco_original': 3499.00, 'desconto': 43, 'link': f'https://www.mercadolivre.com.br/ofertas', 'loja': 'Mercado Livre'},
        {'titulo': 'Café Especial 3 Corações Premium 500g', 'preco': 29.90, 'preco_original': 59.90, 'desconto': 50, 'link': f'https://www.amazon.com.br/s?k=cafe+3+coracoes+premium&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Kit Suplementos Vitamina C + D + Zinco', 'preco': 49.90, 'preco_original': 99.90, 'desconto': 50, 'link': f'https://shopee.com.br/search?keyword=kit+vitamina+c+d+zinco', 'loja': 'Shopee'},
        {'titulo': 'No-break APC 700VA 120V', 'preco': 299.90, 'preco_original': 549.90, 'desconto': 45, 'link': f'https://www.amazon.com.br/s?k=no-break+apc+700va&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Escova Alisadora Taiff Tourmaline 250°C', 'preco': 149.90, 'preco_original': 299.90, 'desconto': 50, 'link': f'https://www.amazon.com.br/s?k=escova+alisadora+taiff&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Kit Maquiagem Maybelline Completo', 'preco': 79.90, 'preco_original': 159.90, 'desconto': 50, 'link': f'https://shopee.com.br/search?keyword=kit+maquiagem+maybelline', 'loja': 'Shopee'},
        {'titulo': 'Perfume Importado Dior Sauvage EDT 100ml', 'preco': 499.90, 'preco_original': 899.90, 'desconto': 44, 'link': f'https://shopee.com.br/search?keyword=dior+sauvage+edt', 'loja': 'Shopee'},
        {'titulo': 'Tênis Infantil Nike Revolution 6', 'preco': 149.90, 'preco_original': 279.90, 'desconto': 46, 'link': f'https://shopee.com.br/search?keyword=nike+revolution+6+infantil', 'loja': 'Shopee'},
        {'titulo': 'Coleira Anti-Pulgas Seresto Cães até 8kg', 'preco': 149.90, 'preco_original': 299.90, 'desconto': 50, 'link': f'https://www.amazon.com.br/s?k=coleira+seresto+caes&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Cama Pet Impermeável Tamanho M', 'preco': 59.90, 'preco_original': 119.90, 'desconto': 50, 'link': f'https://shopee.com.br/search?keyword=cama+pet+impermeavel', 'loja': 'Shopee'},
        {'titulo': 'Câmera de Ré Universal com Sensor', 'preco': 89.90, 'preco_original': 179.90, 'desconto': 50, 'link': f'https://shopee.com.br/search?keyword=camera+re+sensor', 'loja': 'Shopee'},
        {'titulo': 'Aspirador de Pó Portátil para Carro 12V', 'preco': 69.90, 'preco_original': 149.90, 'desconto': 53, 'link': f'https://shopee.com.br/search?keyword=aspirador+portatil+carro+12v', 'loja': 'Shopee'},
        {'titulo': 'Parafusadeira Philips 12V com Maleta', 'preco': 249.90, 'preco_original': 449.90, 'desconto': 44, 'link': f'https://www.mercadolivre.com.br/ofertas', 'loja': 'Mercado Livre'},
        {'titulo': 'Organizador de Gaveta 6 Divisórias', 'preco': 39.90, 'preco_original': 89.90, 'desconto': 56, 'link': f'https://shopee.com.br/search?keyword=organizador+gaveta', 'loja': 'Shopee'},
        {'titulo': 'Conjunto de Toalhas Buddemeyer 5 Peças', 'preco': 89.90, 'preco_original': 179.90, 'desconto': 50, 'link': f'https://shopee.com.br/search?keyword=conjunto+toalhas+buddemeyer', 'loja': 'Shopee'},
        {'titulo': 'Suporte de Parede para TV 32 a 75"', 'preco': 59.90, 'preco_original': 129.90, 'desconto': 54, 'link': f'https://shopee.com.br/search?keyword=suporte+parede+tv', 'loja': 'Shopee'},
        {'titulo': 'Chaleira Elétrica Tramontina 1.7L Inox', 'preco': 99.90, 'preco_original': 189.90, 'desconto': 47, 'link': f'https://www.amazon.com.br/s?k=chaleira+eletrica+tramontina&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Balança Digital Corporal Multilaser', 'preco': 69.90, 'preco_original': 139.90, 'desconto': 50, 'link': f'https://www.amazon.com.br/s?k=balanca+digital+multilaser&tag={AMAZON_TAG}', 'loja': 'Amazon'},
        {'titulo': 'Brinquedo Educativo Montar e Encaixar', 'preco': 49.90, 'preco_original': 99.90, 'desconto': 50, 'link': f'https://shopee.com.br/search?keyword=brinquedo+educativo+montar', 'loja': 'Shopee'},
        {'titulo': 'Chinelo Rider R1 Masculino', 'preco': 49.90, 'preco_original': 99.90, 'desconto': 50, 'link': f'https://www.mercadolivre.com.br/ofertas', 'loja': 'Mercado Livre'},
        {'titulo': 'Cabo HDMI 4K 2 Metros Gold Series', 'preco': 19.90, 'preco_original': 49.90, 'desconto': 60, 'link': f'https://shopee.com.br/search?keyword=cabo+hdmi+4k+2+metros', 'loja': 'Shopee'},
        {'titulo': 'Película de Vidro Temperado Samsung S24', 'preco': 19.90, 'preco_original': 49.90, 'desconto': 60, 'link': f'https://shopee.com.br/search?keyword=pelicula+vidro+samsung+s24', 'loja': 'Shopee'},
        {'titulo': 'Whey Protein Growth Chocolate 900g', 'preco': 89.90, 'preco_original': 179.90, 'desconto': 50, 'link': f'https://shopee.com.br/search?keyword=whey+protein+chocolate+900g', 'loja': 'Shopee'},
        {'titulo': 'Creme Anti-Idade Hidratante Nivea Q10', 'preco': 39.90, 'preco_original': 79.90, 'desconto': 50, 'link': f'https://www.amazon.com.br/s?k=creme+nivea+q10&tag={AMAZON_TAG}', 'loja': 'Amazon'},
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
        f"🔥 *{titulo}*", "",
        f"💰 *Por apenas {preco_fmt}*",
        f"~~De {orig_fmt}~~ → *{oferta['desconto']}% OFF* 🏷️", "",
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

    # Filtra ofertas ainda não postadas
    disponiveis = [o for o in ofertas if re.sub(r'[^a-z0-9]', '', o['titulo'].lower())[:40] not in historico]

    # Se todas foram postadas, limpa o histórico e recomeça
    if len(disponiveis) == 0:
        print("  Todas as ofertas postadas! Reiniciando ciclo...")
        historico = []
        disponiveis = ofertas

    postadas = 0
    for oferta in disponiveis:
        if postadas >= MAX_OFERTAS_POR_CICLO:
            break
        oferta_id = re.sub(r'[^a-z0-9]', '', oferta['titulo'].lower())[:40]
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
    print("  OFERTA NA VEIA BOT - v6")
    print(f"  100 ofertas | Intervalo: {INTERVALO_MINUTOS}min")
    print("  Auto-reinicio quando esgotar ofertas")
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
