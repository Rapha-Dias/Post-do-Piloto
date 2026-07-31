import sys
import asyncio
from autopodcast.news_fetcher import fetch_tech_news
from autopodcast.script_generator import generate_script_with_ai
from autopodcast.audio_generator import generate_audio_for_episode
from autopodcast.rss_generator import add_new_episode, load_episodes, generate_rss_xml, save_episodes
from autopodcast.config_loader import load_config

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

def run_pipeline():
    cfg = load_config()
    podcast_title = cfg["podcast"].get("title", "Meu Podcast")
    print("=" * 60)
    print(f"🎙️ INICIANDO AUTOMATOR MASTER DO {podcast_title.upper()}")
    print("=" * 60)
    
    # 1. Coleta de notícias
    episodes = load_episodes()
    exclude_links = []
    for ep in episodes:
        for src in ep.get("sources", []):
            if isinstance(src, (list, tuple)) and len(src) >= 2:
                exclude_links.append(src[1])

    print("\n[Etapa 1/4] Buscando matérias e tutoriais relevantes em tempo real...")
    news = fetch_tech_news(max_items=3, exclude_links=exclude_links)
    print(f"[OK] {len(news)} notícias selecionadas.")

    # 2. Geração do roteiro
    print("\n[Etapa 2/4] Criando roteiro estruturado com IA...")
    next_ep_num = len(episodes) + 1
    script_data = generate_script_with_ai(news, episode_num=next_ep_num)
    
    dummy_audio_url = f"{cfg['podcast'].get('link', 'http://localhost').rstrip('/')}/episodes/temp.mp3"
    new_ep = add_new_episode(
        title=script_data["title"],
        summary=script_data["summary"],
        script_text=script_data["script"],
        audio_url=dummy_audio_url,
        chapters=script_data["chapters"],
        sources=script_data["sources"]
    )

    # 3. Síntese de áudio MP3
    print("\n[Etapa 3/4] Gerando áudio MP3 com vozes neurais...")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    filepath, file_size = loop.run_until_complete(generate_audio_for_episode(new_ep))
    loop.close()

    # 4. Atualização do Feed RSS
    print("\n[Etapa 4/4] Atualizando feed RSS 2.0...")
    episodes = load_episodes()
    for idx, ep in enumerate(episodes):
        if ep["id"] == new_ep["id"]:
            episodes[idx] = new_ep
            break
            
    save_episodes(episodes)
    generate_rss_xml(episodes)

    print("\n" + "=" * 60)
    print(f"🎉 NOVO EPISÓDIO DO {podcast_title.upper()} GERADO COM SUCESSO!")
    print(f"📌 Título: {new_ep['title']}")
    print(f"📁 Arquivo: {filepath}")
    print("=" * 60)
