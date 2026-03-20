import httpx
import re
from bs4 import BeautifulSoup

async def scrape_website_text(url: str) -> dict:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    
    try:
        async with httpx.AsyncClient(headers=headers, timeout=15.0, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extraer <title>
            title = soup.title.string.strip() if soup.title and soup.title.string else ""
            
            # Extraer meta description
            description = ""
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                description = meta_desc['content'].strip()
                
            # Extraer texto limpio de encabezados y párrafos
            content_tags = soup.find_all(['h1', 'h2', 'h3', 'p'])
            content_text = "\n".join([tag.get_text(separator=' ', strip=True) for tag in content_tags if tag.get_text(strip=True)])
            
            # === EXTRACCIÓN DE COLORES DE MARCA ===
            brand_colors = extract_brand_colors(soup, response.text)
            
            return {
                "url": url,
                "title": title,
                "description": description,
                "content": content_text,
                "brand_colors": brand_colors
            }
            
    except Exception as e:
        raise Exception(f"Failed to scrape website {url}. Error: {str(e)}")


def extract_brand_colors(soup: BeautifulSoup, raw_html: str) -> dict:
    """
    Extrae colores reales de la marca desde múltiples fuentes del HTML:
    - Meta tags (theme-color, msapplication-TileColor, og:image bg)
    - CSS inline en <style> tags y atributos style=""
    - Colores de botones, headers, y elementos clave
    - favicon/logo URLs para referencia
    """
    colors_found = []
    color_sources = {}
    
    # 1. Meta theme-color (Chrome/Android lo usa como color de marca)
    theme_color = soup.find('meta', attrs={'name': 'theme-color'})
    if theme_color and theme_color.get('content'):
        c = theme_color['content'].strip()
        colors_found.append(c)
        color_sources[c] = "meta theme-color"
    
    # 2. msapplication-TileColor (Windows tile color)
    tile_color = soup.find('meta', attrs={'name': 'msapplication-TileColor'})
    if tile_color and tile_color.get('content'):
        c = tile_color['content'].strip()
        colors_found.append(c)
        color_sources[c] = "msapplication-TileColor"
    
    # 3. CSS custom properties (--primary, --brand, --accent, --main, etc.)
    css_var_pattern = re.compile(
        r'--(primary|brand|accent|main|base|theme|color-primary|color-brand|color-accent|btn-primary|header-bg|nav-bg)[^:]*:\s*(#[0-9a-fA-F]{3,8}|rgb[a]?\([^)]+\))',
        re.IGNORECASE
    )
    style_tags = soup.find_all('style')
    for style in style_tags:
        if style.string:
            for match in css_var_pattern.finditer(style.string):
                c = match.group(2).strip()
                colors_found.append(c)
                color_sources[c] = f"CSS variable --{match.group(1)}"
    
    # Also check in inline link stylesheets text
    for match in css_var_pattern.finditer(raw_html):
        c = match.group(2).strip()
        if c not in colors_found:
            colors_found.append(c)
            color_sources[c] = f"CSS variable --{match.group(1)}"
    
    # 4. Colors from key interactive elements (buttons, nav, header)
    key_selectors = [
        ('button', 'background-color', 'button bg'),
        ('button', 'background', 'button bg'),
        ('a.btn', 'background-color', 'button link'),
        ('nav', 'background-color', 'navigation bg'),
        ('header', 'background-color', 'header bg'),
        ('.navbar', 'background-color', 'navbar bg'),
    ]
    
    hex_pattern = re.compile(r'#[0-9a-fA-F]{3,8}')
    rgb_pattern = re.compile(r'rgb[a]?\(\s*\d+\s*,\s*\d+\s*,\s*\d+')
    
    # Extract from inline styles
    elements_with_style = soup.find_all(style=True)
    for el in elements_with_style:
        style_val = el.get('style', '')
        tag_name = el.name
        
        for hex_match in hex_pattern.finditer(style_val):
            c = hex_match.group()
            # Skip black, white, and near-variants
            if c.lower() not in ('#000', '#000000', '#fff', '#ffffff', '#333', '#333333', '#666', '#666666', '#999', '#ccc', '#eee', '#f5f5f5', '#fafafa'):
                colors_found.append(c)
                color_sources[c] = f"inline style on <{tag_name}>"
        
        for rgb_match in rgb_pattern.finditer(style_val):
            c = rgb_match.group() + ')'
            colors_found.append(c)
            color_sources[c] = f"inline style on <{tag_name}>"
    
    # 5. Background colors from CSS rules in <style> tags
    bg_color_pattern = re.compile(
        r'(?:background-color|background)\s*:\s*(#[0-9a-fA-F]{3,8})',
        re.IGNORECASE
    )
    for style in style_tags:
        if style.string:
            for match in bg_color_pattern.finditer(style.string):
                c = match.group(1).strip()
                if c.lower() not in ('#000', '#000000', '#fff', '#ffffff', '#333', '#333333', '#f5f5f5', '#fafafa', '#eee', '#ccc', '#666', '#999'):
                    colors_found.append(c)
                    color_sources[c] = "CSS background-color rule"
    
    # 6. Logo/favicon URLs for reference
    logo_urls = []
    logo_link = soup.find('link', rel=lambda x: x and 'icon' in x)
    if logo_link and logo_link.get('href'):
        logo_urls.append(logo_link['href'])
    
    logo_img = soup.find('img', alt=lambda x: x and ('logo' in x.lower()))
    if logo_img and logo_img.get('src'):
        logo_urls.append(logo_img['src'])
    
    # Count frequency to find most dominant
    color_frequency = {}
    for c in colors_found:
        c_normalized = c.lower().strip()
        color_frequency[c_normalized] = color_frequency.get(c_normalized, 0) + 1
    
    # Sort by frequency
    sorted_colors = sorted(color_frequency.items(), key=lambda x: x[1], reverse=True)
    
    return {
        "detected_colors": [c for c, _ in sorted_colors[:10]],
        "color_sources": color_sources,
        "logo_urls": logo_urls[:3],
        "most_frequent": sorted_colors[0][0] if sorted_colors else None
    }
