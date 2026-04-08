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

def link_amazon(busca):
    return f"https://www.amazon.com.br/s?k={busca.replace(' ', '+')}&tag={AMAZON_TAG}"

def link_shopee(busca):
    return f"https://shopee.com.br/search?keyword={busca.replace(' ', '+')}&af_siteid={SHOPEE_ID}"

def link_ml(busca):
    return f"https://lista.mercadolivre.com.br/{busca.replace(' ', '-')}?matt_tool={ML_ETIQUETA}"

def gerar_ofertas():
    todas_ofertas = [
        # ELETRÔNICOS
        {'titulo': 'Fone Bluetooth JBL Tune 510BT', 'preco': 199.90, 'preco_original': 349.90, 'desconto': 43, 'link': link_amazon('fone jbl tune 510bt'), 'loja': 'Amazon'},
        {'titulo': 'Smartwatch Xiaomi Redmi Watch 3 Active', 'preco': 249.90, 'preco_original': 399.90, 'desconto': 38, 'link': link_shopee('xiaomi redmi watch 3'), 'loja': 'Shopee'},
        {'titulo': 'Carregador Turbo 65W USB-C GaN', 'preco': 69.90, 'preco_original': 149.90, 'desconto': 53, 'link': link_amazon('carregador turbo 65w usb-c'), 'loja': 'Amazon'},
        {'titulo': 'SSD Kingston 480GB SATA III', 'preco': 149.90, 'preco_original': 279.90, 'desconto': 46, 'link': link_amazon('ssd kingston 480gb'), 'loja': 'Amazon'},
        {'titulo': 'Caixa de Som JBL Go 3 Portátil', 'preco': 149.90, 'preco_original': 249.90, 'desconto': 40, 'link': link_amazon('jbl go 3'), 'loja': 'Amazon'},
        {'titulo': 'Mouse Gamer Logitech G203 8000 DPI', 'preco': 149.90, 'preco_original': 249.90, 'desconto': 40, 'link': link_amazon('logitech g203'), 'loja': 'Amazon'},
        {'titulo': 'Headset Gamer HyperX Cloud Stinger', 'preco': 199.90, 'preco_original': 349.90, 'desconto': 43, 'link': link_amazon('hyperx cloud stinger'), 'loja': 'Amazon'},
        {'titulo': 'Kindle 11ª Geração 16GB com Luz', 'preco': 399.00, 'preco_original': 599.00, 'desconto': 33, 'link': link_amazon('kindle 11 geracao'), 'loja': 'Amazon'},
        {'titulo': 'Tablet Samsung Galaxy Tab A9 64GB', 'preco': 999.00, 'preco_original': 1599.00, 'desconto': 38, 'link': link_shopee('samsung galaxy tab a9'), 'loja': 'Shopee'},
        {'titulo': 'Notebook Lenovo IdeaPad Intel Core i5', 'preco': 2499.00, 'preco_original': 3999.00, 'desconto': 38, 'link': link_amazon('notebook lenovo ideapad i5'), 'loja': 'Amazon'},
        {'titulo': 'Câmera de Segurança WiFi Full HD 1080p', 'preco': 89.90, 'preco_original': 179.90, 'desconto': 50, 'link': link_ml('camera seguranca wifi full hd'), 'loja': 'Mercado Livre'},
        {'titulo': 'Teclado Mecânico Gamer Redragon Kumara', 'preco': 199.90, 'preco_original': 349.90, 'desconto': 43, 'link': link_amazon('teclado redragon kumara'), 'loja': 'Amazon'},
        {'titulo': 'Monitor LG 24 Full HD IPS', 'preco': 799.00, 'preco_original': 1299.00, 'desconto': 38, 'link': link_amazon('monitor lg 24 full hd'), 'loja': 'Amazon'},
        {'titulo': 'Pen Drive Kingston 64GB USB 3.0', 'preco': 29.90, 'preco_original': 59.90, 'desconto': 50, 'link': link_amazon('pen drive kingston 64gb'), 'loja': 'Amazon'},
        {'titulo': 'Webcam Full HD 1080p com Microfone', 'preco': 99.90, 'preco_original': 199.90, 'desconto': 50, 'link': link_shopee('webcam full hd 1080p microfone'), 'loja': 'Shopee'},
        {'titulo': 'Impressora HP DeskJet Ink Advantage', 'preco': 349.00, 'preco_original': 599.00, 'desconto': 42, 'link': link_amazon('impressora hp deskjet ink advantage'), 'loja': 'Amazon'},
        {'titulo': 'HD Externo Seagate 1TB USB 3.0', 'preco': 299.00, 'preco_original': 499.00, 'desconto': 40, 'link': link_amazon('hd externo seagate 1tb'), 'loja': 'Amazon'},
        {'titulo': 'Roteador WiFi 6 TP-Link AX1500', 'preco': 299.90, 'preco_original': 499.90, 'desconto': 40, 'link': link_amazon('roteador tp-link ax1500'), 'loja': 'Amazon'},
        {'titulo': 'Caixa de Som Bluetooth Anker Soundcore', 'preco': 179.90, 'preco_original': 299.90, 'desconto': 40, 'link': link_amazon('anker soundcore'), 'loja': 'Amazon'},
        {'titulo': 'Controle PS5 DualSense Branco', 'preco': 399.00, 'preco_original': 599.00, 'desconto': 33, 'link': link_amazon('controle ps5 dualsense'), 'loja': 'Amazon'},
        # CASA E COZINHA
        {'titulo': 'Air Fryer 4L Philips Walita', 'preco': 299.90, 'preco_original': 499.90, 'desconto': 40, 'link': link_amazon('air fryer philips walita 4l'), 'loja': 'Amazon'},
        {'titulo': 'Cafeteira Nespresso Essenza Mini', 'preco': 399.90, 'preco_original': 699.90, 'desconto': 43, 'link': link_ml('cafeteira nespresso essenza mini'), 'loja': 'Mercado Livre'},
        {'titulo': 'Panela de Pressão Elétrica 6L Digital', 'preco': 199.90, 'preco_original': 399.90, 'desconto': 50, 'link': link_shopee('panela pressao eletrica 6l digital'), 'loja': 'Shopee'},
        {'titulo': 'Aspirador Robô com Mapeamento Inteligente', 'preco': 699.00, 'preco_original': 1299.00, 'desconto': 46, 'link': link_ml('aspirador robo mapeamento'), 'loja': 'Mercado Livre'},
        {'titulo': 'Ferro de Passar Roupa a Vapor Philips', 'preco': 149.90, 'preco_original': 299.90, 'desconto': 50, 'link': link_ml('ferro passar roupa vapor philips'), 'loja': 'Mercado Livre'},
        {'titulo': 'Liquidificador Oster 1200W 3 Velocidades', 'preco': 149.90, 'preco_original': 279.90, 'desconto': 46, 'link': link_amazon('liquidificador oster 1200w'), 'loja': 'Amazon'},
        {'titulo': 'Jogo de Panelas Antiaderente 5 Peças', 'preco': 199.90, 'preco_original': 399.90, 'desconto': 50, 'link': link_shopee('jogo panelas antiaderente 5 pecas'), 'loja': 'Shopee'},
        {'titulo': 'Purificador de Ar Electrolux PA31F', 'preco': 499.00, 'preco_original': 899.00, 'desconto': 44, 'link': link_amazon('purificador ar electrolux pa31f'), 'loja': 'Amazon'},
        {'titulo': 'Jogo de Cama King 200 Fios', 'preco': 99.90, 'preco_original': 199.90, 'desconto': 50, 'link': link_shopee('jogo cama king 200 fios'), 'loja': 'Shopee'},
        {'titulo': 'Ventilador de Mesa Arno 40cm Silence Force', 'preco': 149.90, 'preco_original': 269.90, 'desconto': 44, 'link': link_amazon('ventilador arno silence force'), 'loja': 'Amazon'},
        {'titulo': 'Chaleira Elétrica Tramontina 1.7L Inox', 'preco': 99.90, 'preco_original': 189.90, 'desconto': 47, 'link': link_amazon('chaleira eletrica tramontina inox'), 'loja': 'Amazon'},
        {'titulo': 'Suporte de Parede para TV 32 a 75 pol', 'preco': 59.90, 'preco_original': 129.90, 'desconto': 54, 'link': link_ml('suporte parede tv 75 polegadas'), 'loja': 'Mercado Livre'},
        {'titulo': 'Organizador de Gaveta 6 Divisórias', 'preco': 39.90, 'preco_original': 89.90, 'desconto': 56, 'link': link_shopee('organizador gaveta 6 divisorias'), 'loja': 'Shopee'},
        {'titulo': 'Conjunto de Toalhas 5 Peças Premium', 'preco': 89.90, 'preco_original': 179.90, 'desconto': 50, 'link': link_shopee('conjunto toalhas 5 pecas premium'), 'loja': 'Shopee'},
        # BELEZA E SAÚDE
        {'titulo': 'Kit Skincare Vitamina C Completo', 'preco': 89.90, 'preco_original': 179.90, 'desconto': 50, 'link': link_shopee('kit skincare vitamina c'), 'loja': 'Shopee'},
        {'titulo': 'Perfume Calvin Klein Eternity 100ml', 'preco': 299.90, 'preco_original': 549.90, 'desconto': 45, 'link': link_shopee('calvin klein eternity 100ml'), 'loja': 'Shopee'},
        {'titulo': 'Secador de Cabelo Taiff Style 2100W', 'preco': 129.90, 'preco_original': 249.90, 'desconto': 48, 'link': link_amazon('secador taiff 2100w'), 'loja': 'Amazon'},
        {'titulo': 'Kit Shampoo e Condicionador Elseve', 'preco': 49.90, 'preco_original': 99.90, 'desconto': 50, 'link': link_shopee('shampoo condicionador elseve kit'), 'loja': 'Shopee'},
        {'titulo': 'Protetor Solar Neutrogena FPS 70 200ml', 'preco': 49.90, 'preco_original': 89.90, 'desconto': 44, 'link': link_amazon('protetor solar neutrogena fps 70'), 'loja': 'Amazon'},
        {'titulo': 'Escova Dental Elétrica Oral-B Pro 1', 'preco': 149.90, 'preco_original': 299.90, 'desconto': 50, 'link': link_amazon('oral-b pro 1 escova eletrica'), 'loja': 'Amazon'},
        {'titulo': 'Escova Alisadora Taiff Tourmaline 250', 'preco': 149.90, 'preco_original': 299.90, 'desconto': 50, 'link': link_amazon('escova alisadora taiff tourmaline'), 'loja': 'Amazon'},
        {'titulo': 'Kit Maquiagem Maybelline Completo', 'preco': 79.90, 'preco_original': 159.90, 'desconto': 50, 'link': link_shopee('kit maquiagem maybelline'), 'loja': 'Shopee'},
        {'titulo': 'Perfume Dior Sauvage EDT 100ml', 'preco': 499.90, 'preco_original': 899.90, 'desconto': 44, 'link': link_shopee('dior sauvage edt 100ml'), 'loja': 'Shopee'},
        {'titulo': 'Balança Digital Corporal', 'preco': 69.90, 'preco_original': 139.90, 'desconto': 50, 'link': link_amazon('balanca digital corporal'), 'loja': 'Amazon'},
        {'titulo': 'Creme Anti-Idade Nivea Q10 Plus', 'preco': 39.90, 'preco_original': 79.90, 'desconto': 50, 'link': link_amazon('creme nivea q10 anti-idade'), 'loja': 'Amazon'},
        # MODA
        {'titulo': 'Tênis Nike Air Max SC Masculino', 'preco': 299.99, 'preco_original': 499.99, 'desconto': 40, 'link': link_amazon('nike air max sc masculino'), 'loja': 'Amazon'},
        {'titulo': 'Mochila Antifurto USB 40L Impermeável', 'preco': 119.90, 'preco_original': 229.90, 'desconto': 48, 'link': link_shopee('mochila antifurto usb 40l impermeavel'), 'loja': 'Shopee'},
        {'titulo': 'Relógio Casio Digital Esportivo', 'preco': 199.90, 'preco_original': 349.90, 'desconto': 43, 'link': link_amazon('casio digital esportivo'), 'loja': 'Amazon'},
        {'titulo': 'Tênis Feminino Adidas Cloudfoam', 'preco': 199.90, 'preco_original': 349.90, 'desconto': 43, 'link': link_shopee('adidas cloudfoam feminino'), 'loja': 'Shopee'},
        {'titulo': 'Carteira Masculina Couro Legítimo', 'preco': 59.90, 'preco_original': 119.90, 'desconto': 50, 'link': link_shopee('carteira masculina couro legitimo'), 'loja': 'Shopee'},
        {'titulo': 'Óculos de Sol Ray-Ban Wayfarer', 'preco': 399.90, 'preco_original': 699.90, 'desconto': 43, 'link': link_amazon('ray-ban wayfarer oculos'), 'loja': 'Amazon'},
        {'titulo': 'Bolsa Feminina Transversal Couro Sintético', 'preco': 79.90, 'preco_original': 159.90, 'desconto': 50, 'link': link_shopee('bolsa feminina transversal couro'), 'loja': 'Shopee'},
        {'titulo': 'Kit Meias Masculinas 12 Pares', 'preco': 39.90, 'preco_original': 89.90, 'desconto': 56, 'link': link_shopee('kit meias masculinas 12 pares'), 'loja': 'Shopee'},
        {'titulo': 'Tênis Infantil Nike Revolution 6', 'preco': 149.90, 'preco_original': 279.90, 'desconto': 46, 'link': link_shopee('nike revolution 6 infantil'), 'loja': 'Shopee'},
        # LIVROS
        {'titulo': 'Box Harry Potter Edição Especial 7 Livros', 'preco': 199.90, 'preco_original': 399.90, 'desconto': 50, 'link': link_amazon('box harry potter 7 livros'), 'loja': 'Amazon'},
        {'titulo': 'Pai Rico Pai Pobre Robert Kiyosaki', 'preco': 39.90, 'preco_original': 79.90, 'desconto': 50, 'link': link_amazon('pai rico pai pobre kiyosaki'), 'loja': 'Amazon'},
        {'titulo': 'Agenda Planner 2025 Capa Dura', 'preco': 29.90, 'preco_original': 69.90, 'desconto': 57, 'link': link_shopee('agenda planner 2025 capa dura'), 'loja': 'Shopee'},
        {'titulo': 'O Poder do Hábito Charles Duhigg', 'preco': 34.90, 'preco_original': 69.90, 'desconto': 50, 'link': link_amazon('o poder do habito charles duhigg'), 'loja': 'Amazon'},
        {'titulo': 'Kit Canetas Stabilo Boss 6 Cores', 'preco': 29.90, 'preco_original': 59.90, 'desconto': 50, 'link': link_shopee('stabilo boss 6 cores'), 'loja': 'Shopee'},
        # ESPORTES
        {'titulo': 'Kit Halteres 2kg 4kg 6kg Emborrachados', 'preco': 149.90, 'preco_original': 299.90, 'desconto': 50, 'link': link_shopee('kit halteres emborrachados'), 'loja': 'Shopee'},
        {'titulo': 'Corda de Pular Speed Jump 3 Metros', 'preco': 29.90, 'preco_original': 69.90, 'desconto': 57, 'link': link_shopee('corda pular speed jump'), 'loja': 'Shopee'},
        {'titulo': 'Tapete Yoga Antiderrapante 6mm', 'preco': 49.90, 'preco_original': 99.90, 'desconto': 50, 'link': link_shopee('tapete yoga antiderrapante 6mm'), 'loja': 'Shopee'},
        {'titulo': 'Whey Protein Isolado Growth 900g', 'preco': 99.90, 'preco_original': 199.90, 'desconto': 50, 'link': link_amazon('whey protein isolado growth 900g'), 'loja': 'Amazon'},
        {'titulo': 'Garrafa Térmica Stanley 1L Original', 'preco': 149.90, 'preco_original': 299.90, 'desconto': 50, 'link': link_amazon('garrafa termica stanley 1l'), 'loja': 'Amazon'},
        {'titulo': 'Bicicleta Ergométrica Magnética', 'preco': 899.00, 'preco_original': 1599.00, 'desconto': 44, 'link': link_ml('bicicleta ergometrica magnetica'), 'loja': 'Mercado Livre'},
        {'titulo': 'Kit Suplementos Vitamina C D Zinco', 'preco': 49.90, 'preco_original': 99.90, 'desconto': 50, 'link': link_shopee('kit vitamina c d zinco suplemento'), 'loja': 'Shopee'},
        # INFANTIL
        {'titulo': 'LEGO Classic Caixa de Ideias 790 Peças', 'preco': 299.90, 'preco_original': 549.90, 'desconto': 45, 'link': link_amazon('lego classic caixa ideias'), 'loja': 'Amazon'},
        {'titulo': 'Boneca Barbie Fashionista Articulada', 'preco': 79.90, 'preco_original': 149.90, 'desconto': 47, 'link': link_amazon('barbie fashionista articulada'), 'loja': 'Amazon'},
        {'titulo': 'Carrinho Hot Wheels Kit 10 Unidades', 'preco': 79.90, 'preco_original': 159.90, 'desconto': 50, 'link': link_shopee('hot wheels kit 10 carrinhos'), 'loja': 'Shopee'},
        {'titulo': 'Jogo de Tabuleiro Detetive Estrela', 'preco': 79.90, 'preco_original': 159.90, 'desconto': 50, 'link': link_amazon('detetive jogo tabuleiro estrela'), 'loja': 'Amazon'},
        {'titulo': 'Brinquedo Educativo Montar e Encaixar', 'preco': 49.90, 'preco_original': 99.90, 'desconto': 50, 'link': link_shopee('brinquedo educativo montar encaixar'), 'loja': 'Shopee'},
        # PETS
        {'titulo': 'Ração Royal Canin Cães Adultos 15kg', 'preco': 299.90, 'preco_original': 499.90, 'desconto': 40, 'link': link_amazon('royal canin caes adultos 15kg'), 'loja': 'Amazon'},
        {'titulo': 'Arranhador para Gatos com Brinquedo', 'preco': 79.90, 'preco_original': 159.90, 'desconto': 50, 'link': link_shopee('arranhador gatos brinquedo'), 'loja': 'Shopee'},
        {'titulo': 'Coleira Anti-Pulgas Seresto até 8kg', 'preco': 149.90, 'preco_original': 299.90, 'desconto': 50, 'link': link_amazon('coleira seresto anti pulgas caes'), 'loja': 'Amazon'},
        {'titulo': 'Cama Pet Impermeável Tamanho M', 'preco': 59.90, 'preco_original': 119.90, 'desconto': 50, 'link': link_shopee('cama pet impermeavel tamanho m'), 'loja': 'Shopee'},
        # AUTOMOTIVO
        {'titulo': 'Suporte Veicular Celular Magnético 360', 'preco': 29.90, 'preco_original': 69.90, 'desconto': 57, 'link': link_shopee('suporte celular carro magnetico 360'), 'loja': 'Shopee'},
        {'titulo': 'Carregador Veicular Duplo USB-C 36W', 'preco': 39.90, 'preco_original': 89.90, 'desconto': 56, 'link': link_amazon('carregador veicular usb-c 36w duplo'), 'loja': 'Amazon'},
        {'titulo': 'Câmera de Ré Universal com Sensor', 'preco': 89.90, 'preco_original': 179.90, 'desconto': 50, 'link': link_shopee('camera re universal sensor'), 'loja': 'Shopee'},
        {'titulo': 'Aspirador Portátil para Carro 12V', 'preco': 69.90, 'preco_original': 149.90, 'desconto': 53, 'link': link_shopee('aspirador portatil carro 12v'), 'loja': 'Shopee'},
        # FERRAMENTAS
        {'titulo': 'Furadeira de Impacto Bosch 550W', 'preco': 299.90, 'preco_original': 499.90, 'desconto': 40, 'link': link_amazon('furadeira impacto bosch 550w'), 'loja': 'Amazon'},
        {'titulo': 'Kit Ferramentas 127 Peças Tramontina', 'preco': 199.90, 'preco_original': 399.90, 'desconto': 50, 'link': link_amazon('kit ferramentas tramontina 127 pecas'), 'loja': 'Amazon'},
        {'titulo': 'Parafusadeira 12V com Maleta e Acessórios', 'preco': 249.90, 'preco_original': 449.90, 'desconto': 44, 'link': link_ml('parafusadeira 12v maleta acessorios'), 'loja': 'Mercado Livre'},
        # INFORMÁTICA
        {'titulo': 'Memória RAM Kingston 16GB DDR4 3200MHz', 'preco': 199.90, 'preco_original': 349.90, 'desconto': 43, 'link': link_amazon('memoria ram kingston 16gb ddr4'), 'loja': 'Amazon'},
        {'titulo': 'Mousepad Gamer Extra Grande 90x40cm', 'preco': 49.90, 'preco_original': 99.90, 'desconto': 50, 'link': link_shopee('mousepad gamer 90x40cm'), 'loja': 'Shopee'},
        {'titulo': 'Hub USB-C 7 em 1 Multiporta 4K HDMI', 'preco': 89.90, 'preco_original': 179.90, 'desconto': 50, 'link': link_amazon('hub usb-c 7 em 1 hdmi 4k'), 'loja': 'Amazon'},
        {'titulo': 'No-break APC 700VA 120V', 'preco': 299.90, 'preco_original': 549.90, 'desconto': 45, 'link': link_amazon('no-break apc 700va 120v'), 'loja': 'Amazon'},
        # CELULARES
        {'titulo': 'Capinha iPhone 15 Pro Silicone Premium', 'preco': 29.90, 'preco_original': 69.90, 'desconto': 57, 'link': link_shopee('capinha iphone 15 pro silicone'), 'loja': 'Shopee'},
        {'titulo': 'Película Vidro Temperado Samsung S24', 'preco': 19.90, 'preco_original': 49.90, 'desconto': 60, 'link': link_shopee('pelicula vidro temperado samsung s24'), 'loja': 'Shopee'},
        {'titulo': 'Powerbank 20000mAh Carregamento Rápido', 'preco': 199.90, 'preco_original': 399.90, 'desconto': 50, 'link': link_amazon('powerbank 20000mah carregamento rapido'), 'loja': 'Amazon'},
        {'titulo': 'Suporte de Mesa para Celular Ajustável', 'preco': 29.90, 'preco_original': 69.90, 'desconto': 57, 'link': link_shopee('suporte mesa celular ajustavel'), 'loja': 'Shopee'},
        {'titulo': 'Cabo USB-C 2 Metros Carga Rápida 5A', 'preco': 19.90, 'preco_original': 49.90, 'desconto': 60, 'link': link_shopee('cabo usb-c 2 metros carga rapida 5a'), 'loja': 'Shopee'},
        {'titulo': 'Cabo HDMI 4K 2 Metros', 'preco': 19.90, 'preco_original': 49.90, 'desconto': 60, 'link': link_shopee('cabo hdmi 4k 2 metros'), 'loja': 'Shopee'},
        # OUTROS
        {'titulo': 'Café Especial 3 Corações Premium 500g', 'preco': 29.90, 'preco_original': 59.90, 'desconto': 50, 'link': link_amazon('cafe 3 coracoes premium 500g'), 'loja': 'Amazon'},
        {'titulo': 'Whey Protein Growth Chocolate 900g', 'preco': 89.90, 'preco_original': 179.90, 'desconto': 50, 'link': link_shopee('whey protein growth chocolate 900g'), 'loja': 'Shopee'},
        {'titulo': 'Esteira Elétrica Residencial Dobrável', 'preco': 1999.00, 'preco_original': 3499.00, 'desconto': 43, 'link': link_ml('esteira eletrica residencial dobravel'), 'loja': 'Mercado Livre'},
        {'titulo': 'Chinelo Rider R1 Masculino', 'preco': 49.90, 'preco_original': 99.90, 'desconto': 50, 'link': link_ml('chinelo rider r1 masculino'), 'loja': 'Mercado Livre'},
    ]
    random.shuffle(todas_ofertas)
    return todas_ofertas

def emoji_loja(loja):
    mapa = {'Amazon': '📦', 'Shopee': '🛍️', 'Mercado Livre': '🟡'}
    return mapa.get(loja, '🏪')

def formatar_mensagem(oferta):
    titulo = oferta['titulo']
    loja = oferta['loja']
    link = oferta['link']
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
    print("  OFERTA NA VEIA BOT - v7")
    print(f"  100 ofertas com links corretos")
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
