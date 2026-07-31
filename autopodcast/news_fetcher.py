import re
import ssl
import urllib.request
import feedparser
from autopodcast.config_loader import load_config

def clean_html(text: str) -> str:
    if not text:
        return ""
    cleaned = re.sub(r'<[^>]+>', '', text)
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned.strip()[:350]

def fetch_feed_data(url: str, timeout: int = 4) -> bytes:
    cfg = load_config()
    bot_name = cfg["podcast"].get("title", "AutoPodcastBot").replace(" ", "") + "Bot/2.0"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) {bot_name}"}
    )
    context = ssl._create_unverified_context()
    with urllib.request.urlopen(req, timeout=timeout, context=context) as resp:
        return resp.read()

def fetch_tech_news(max_items: int = 4, exclude_links: list = None) -> list:
    """
    Coleta e filtra notícias de feeds RSS definidos em podcast_config.json.
    """
    if exclude_links is None:
        exclude_links = []

    cfg = load_config()
    feeds = cfg.get("feeds", [])
    keywords = [kw.lower() for kw in cfg.get("keywords", [])]
    podcast_title = cfg["podcast"].get("title", "Podcast")

    articles = []
    seen_links = set(exclude_links)
    
    for feed_info in feeds:
        try:
            raw_data = fetch_feed_data(feed_info["url"], timeout=4)
            feed = feedparser.parse(raw_data)
            for entry in feed.entries[:5]:
                link = entry.get("link", feed_info["url"])
                if link in seen_links:
                    continue

                title = clean_html(entry.get("title", ""))
                if not title:
                    continue

                summary = clean_html(entry.get("summary", entry.get("description", "")))
                full_text = f"{title} {summary}".lower()

                # Verifica se contém alguma palavra-chave (ou aceita todos se keywords estiver vazio)
                if not keywords or any(kw in full_text for kw in keywords):
                    seen_links.add(link)
                    articles.append({
                        "title": title,
                        "link": link,
                        "summary": summary if summary else title,
                        "source": feed_info["name"]
                    })
                    if len(articles) >= max_items:
                        break
        except Exception as e:
            print(f"[!] Aviso: erro ao buscar feed '{feed_info.get('name')}': {e}")
            
    # Fallback caso os feeds não retornem notícias suficientes
    if len(articles) < 2:
        print("[!] Adicionando módulos essenciais do Curso Básico de Piloto Privado (PPA).")
        fallback_topics = [
            {
                "title": "Teoria de Voo e Aerodinâmica: As Quatro Forças (Sustentação, Arrasto, Tração e Peso)",
                "link": "https://canalpiloto.com.br/guia-basico-ppa-parte-3-curso-teorico/",
                "summary": "Estudo das forças aerodinâmicas em voo reto e nivelado, sustentação do aerofólio, perfis de asa e prevenindo o estol (stall).",
                "source": "Canal Piloto - Curso PPA"
            },
            {
                "title": "Meteorologia Aeronáutica: Leitura de METAR, Altimetria (QNH) e Segurança VFR",
                "link": "https://pt.scribd.com/document/974659764/Guia-Piloto-Privado-de-Aviao-Parte-2-Material-Didatico",
                "summary": "Conceitos de pressão atmosférica, camadas da atmosfera, interpretação de informes meteorológicos METAR/TAF e identificação de nuvens perigosas.",
                "source": "Material Didático PPA"
            },
            {
                "title": "Instrução Prática de Voo: Inspeção Pré-Voo, Checklists e o Primeiro Voo Solo",
                "link": "https://canalpiloto.com.br/guia-basico-ppa-parte-6-curso-pratico/",
                "summary": "Passo a passo da rotina do aluno no aeroclube, inspeção de cabine e pré-voo, fraseologia de torre e o grande momento do voo solo.",
                "source": "Instrução de Voo INVA"
            }
        ]
        for fb in fallback_topics:
            if fb["link"] not in seen_links and len(articles) < max_items:
                articles.append(fb)
                seen_links.add(fb["link"])
            
    return articles[:max_items]
