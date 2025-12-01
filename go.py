import re
import json
from bs4 import BeautifulSoup
from typing import Tuple, Optional, Dict, Any

def extract_product_info(html_content: str) -> Dict[str, Optional[str]]:
    soup = BeautifulSoup(html_content, 'html.parser')
    
    result = {
        'name': None,
        'brand': None,
        'price': None
    }
    
    # Primeira estratégia: Schema.org (JSON-LD)
    json_ld = _extract_from_json_ld(soup)
    if json_ld:
        return json_ld
    
    # Segunda estratégia: Microdata
    microdata = _extract_from_microdata(soup)
    if microdata:
        return microdata
    
    # Terceira estratégia: Busca heurística
    result['name'] = _find_product_name(soup)
    result['brand'] = _find_product_brand(soup)
    result['price'] = _find_product_price(soup)
    
    return result

def _extract_from_json_ld(soup: BeautifulSoup) -> Optional[Dict[str, str]]:
    scripts = soup.find_all('script', {'type': 'application/ld+json'})
    for script in scripts:
        try:
            data = json.loads(script.string, strict=False)
            if isinstance(data, list):
                data = data[0]
                
            if data.get('@type') in ['Product', 'http://schema.org/Product']:
                product_info = {}
                
                # Nome
                product_info['name'] = data.get('name')
                
                # Marca
                brand = data.get('brand')
                if isinstance(brand, dict):
                    product_info['brand'] = brand.get('name')
                else:
                    product_info['brand'] = brand
                
                # Preço
                offers = data.get('offers')
                if offers:
                    if isinstance(offers, list):
                        offers = offers[0]
                    product_info['price'] = offers.get('price')
                
                return {k: v for k, v in product_info.items() if v is not None}
        except:
            continue
    return None

def _extract_from_microdata(soup: BeautifulSoup) -> Optional[Dict[str, str]]:
    product = soup.find(itemtype="http://schema.org/Product")
    if not product:
        return None
    
    microdata = {}
    
    # Nome
    name_elem = product.find(itemprop="name")
    if name_elem:
        microdata['name'] = name_elem.get_text(strip=True)
    
    # Marca
    brand_elem = product.find(itemprop="brand")
    if brand_elem:
        microdata['brand'] = brand_elem.get_text(strip=True)
    
    # Preço
    price_elem = product.find(itemprop="price")
    if price_elem:
        microdata['price'] = price_elem.get('content') or price_elem.get_text(strip=True)
    
    return microdata

def _find_product_name(soup: BeautifulSoup) -> Optional[str]:
    # Tentativas em ordem de prioridade
    candidates = []
    
    # 1. Título da página
    title = soup.title.string if soup.title else None
    if title:
        candidates.append(title.strip())
    
    # 2. Elementos h1
    for h1 in soup.find_all('h1'):
        text = h1.get_text(strip=True)
        if text:
            candidates.append(text)
    
    # 3. Meta tags
    meta = soup.find('meta', {'property': 'og:title'})
    if meta and meta.get('content'):
        candidates.append(meta['content'].strip())
    
    # 4. Classes comuns
    for class_name in ['product-name', 'product-title', 'product__name', 'prod-name']:
        for elem in soup.find_all(class_=class_name):
            text = elem.get_text(strip=True)
            if text:
                candidates.append(text)
    
    # Selecionar o melhor candidato
    if candidates:
        return max(candidates, key=len)
    return None

def _find_product_brand(soup: BeautifulSoup) -> Optional[str]:
    # Estratégias para encontrar a marca
    strategies = [
        {'itemprop': 'brand'},
        {'class': ['brand', 'product-brand', 'maker', 'vendor']},
        {'id': 'brand'},
        {'name': 'brand'}
    ]
    
    for strategy in strategies:
        elem = soup.find(**strategy)
        if elem:
            text = elem.get_text(strip=True)
            if text:
                return text
    
    # Tentar extrair de imagens (logos)
    for img in soup.find_all('img', alt=True):
        alt = img['alt'].lower()
        if 'logo' in alt:
            return alt.replace('logo', '').strip()
    
    return None

def _find_product_price(soup: BeautifulSoup) -> Optional[str]:
    # Regex para encontrar preços
    price_regex = re.compile(
        r'(\$|\€|\£)?\s?(\d{1,3}(?:[.,\s]?\d{3})*(?:[.,]\d{2})?)',
        re.UNICODE
    )
    
    # Elementos com classes relacionadas a preço
    price_classes = ['price', 'product-price', 'current-price', 'sale-price']
    
    # Procurar em elementos específicos
    for class_name in price_classes:
        for elem in soup.find_all(class_=class_name):
            text = elem.get_text(strip=True)
            match = price_regex.search(text)
            if match:
                return match.group().strip()
    
    # Procurar em meta tags
    meta = soup.find('meta', {'property': 'product:price:amount'})
    if meta and meta.get('content'):
        return meta['content'].strip()
    
    # Varredura geral por padrões numéricos
    for elem in soup.find_all(string=price_regex):
        match = price_regex.search(elem)
        if match:
            return match.group().strip()
    
    return None

# Exemplo de uso
if __name__ == "__main__":
    import requests
    
    # Substituir por qualquer URL de produto
    url = 'https://www.amazon.com.br/Crime-castigo-Fi%C3%B3dor-Dostoi%C3%A9vski/dp/8544002161/?_encoding=UTF8&pd_rd_w=vtWNr&content-id=amzn1.sym.7b2d638d-dfa8-4a77-b0b2-ecd6bdff1d14&pf_rd_p=7b2d638d-dfa8-4a77-b0b2-ecd6bdff1d14&pf_rd_r=VJ1VM6H9EW0C8Q0994CQ&pd_rd_wg=PpKiz&pd_rd_r=822faea0-8c1c-480f-9fdd-d5225ff725ca&ref_=pd_hp_d_atf_dealz_cs'
    response = requests.get(url)
    
    if response.status_code == 200:
        product_info = extract_product_info(response.text)
        print("Nome:", product_info['name'])
        print("Marca:", product_info['brand'])
        print("Preço:", product_info['price'])
    else:
        print("Erro ao carregar a página")