import httpx
from bs4 import BeautifulSoup

async def scrape_website_text(url: str) -> dict:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    
    try:
        # Usamos follow_redirects para manejar redirecciones automáticamente
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
            # Filtramos textos vacíos y unimos con saltos de línea
            content_text = "\n".join([tag.get_text(separator=' ', strip=True) for tag in content_tags if tag.get_text(strip=True)])
            
            return {
                "url": url,
                "title": title,
                "description": description,
                "content": content_text
            }
            
    except Exception as e:
        # Lanzamos una excepción controlada si la web no responde
        raise Exception(f"Failed to scrape website {url}. Error: {str(e)}")
