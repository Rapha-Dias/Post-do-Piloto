import os
import re
import json
from datetime import datetime, timezone
import xml.etree.ElementTree as ET
from autopodcast.config_loader import load_config

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
EPISODES_FILE = os.path.join(DATA_DIR, "episodes.json")
RSS_OUTPUT_FILE = os.path.join(BASE_DIR, "rss.xml")

os.makedirs(DATA_DIR, exist_ok=True)

def load_episodes():
    if os.path.exists(EPISODES_FILE):
        with open(EPISODES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_episodes(episodes):
    with open(EPISODES_FILE, "w", encoding="utf-8") as f:
        json.dump(episodes, f, ensure_ascii=False, indent=2)

def generate_rss_xml(episodes):
    cfg = load_config()
    p = cfg["podcast"]
    podcast_title = p.get("title", "Meu Podcast")
    podcast_link = p.get("link", "https://seu-usuario.github.io/seu-repositorio").rstrip("/")
    podcast_desc = p.get("description", "Podcast gerado com IA")
    podcast_author = p.get("author", "Apresentadores do Podcast")
    podcast_email = p.get("email", "contato@exemplo.com")
    podcast_category = p.get("category", "Technology")
    podcast_language = p.get("language", "pt-br")
    podcast_image = f"{podcast_link}/cover.jpg"

    rss = ET.Element("rss", {
        "version": "2.0",
        "xmlns:itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd",
        "xmlns:content": "http://purl.org/rss/1.0/modules/content/"
    })
    
    channel = ET.SubElement(rss, "channel")
    
    ET.SubElement(channel, "title").text = podcast_title
    ET.SubElement(channel, "link").text = podcast_link
    ET.SubElement(channel, "description").text = podcast_desc
    ET.SubElement(channel, "language").text = podcast_language
    
    ET.SubElement(channel, "itunes:author").text = podcast_author
    ET.SubElement(channel, "itunes:explicit").text = "no"

    owner = ET.SubElement(channel, "itunes:owner")
    ET.SubElement(owner, "itunes:name").text = podcast_author
    ET.SubElement(owner, "itunes:email").text = podcast_email

    ET.SubElement(channel, "managingEditor").text = f"{podcast_email} ({podcast_author})"
    
    image = ET.SubElement(channel, "itunes:image")
    image.set("href", podcast_image)
    
    category = ET.SubElement(channel, "itunes:category")
    category.set("text", podcast_category)
    
    for ep in episodes:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = ep.get("title")
        ET.SubElement(item, "description").text = ep.get("description", "")
        ET.SubElement(item, "itunes:summary").text = ep.get("summary", ep.get("title"))
        ET.SubElement(item, "itunes:explicit").text = "no"
        ET.SubElement(item, "guid").text = ep.get("guid")
        ET.SubElement(item, "pubDate").text = ep.get("pubDate")
        ET.SubElement(item, "itunes:duration").text = ep.get("duration", "00:20:00")
        
        enclosure = ET.SubElement(item, "enclosure")
        enclosure.set("url", ep.get("audio_url", ""))
        enclosure.set("length", str(ep.get("audio_bytes", 25000000)))
        enclosure.set("type", "audio/mpeg")

    tree = ET.ElementTree(rss)
    ET.indent(tree, space="  ", level=0)
    tree.write(RSS_OUTPUT_FILE, encoding="utf-8", xml_declaration=True)
    print(f"[OK] Feed RSS 2.0 gerado com sucesso em: {RSS_OUTPUT_FILE}")

def add_new_episode(title, summary, script_text, audio_url, chapters, sources, audio_bytes=25000000):
    episodes = load_episodes()
    ep_num = len(episodes) + 1
    today_str = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    guid = f"podcast-ep{ep_num:03d}-{datetime.now().strftime('%Y%m%d')}"
    
    show_notes = f"🎙️ SOBRE ESTE EPISÓDIO:\n{summary}\n\n⏱️ CAPÍTULOS E MARCAS DE TEMPO:\n"
    for idx, (time_mark, ch_title) in enumerate(chapters, 1):
        clean_ch = re.sub(r'^(Bloco|Cap|Capítulo)\s*\d+:\s*', '', ch_title, flags=re.IGNORECASE)
        show_notes += f"• {time_mark} - Cap {idx:02d}: {clean_ch}\n"
        
    show_notes += "\n🔗 FONTES CITADAS E LINKS RECOMENDADOS:\n"
    for src_name, src_url in sources:
        show_notes += f"• {src_name}: {src_url}\n"
        
    final_title = title if re.match(r'^EP\d+', title, flags=re.IGNORECASE) else f"Ep {ep_num:02d}: {title}"
    new_ep = {
        "id": ep_num,
        "guid": guid,
        "title": final_title,
        "summary": summary,
        "description": show_notes,
        "audio_url": audio_url,
        "audio_bytes": audio_bytes,
        "pubDate": today_str,
        "duration": "00:20:00",
        "script": script_text,
        "sources": sources,
        "chapters": chapters
    }
    
    episodes.insert(0, new_ep)
    save_episodes(episodes)
    generate_rss_xml(episodes)
    return new_ep
