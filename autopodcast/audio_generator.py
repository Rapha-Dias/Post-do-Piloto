import os
import re
import edge_tts
from autopodcast.config_loader import load_config

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "episodes")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def clean_text_for_speech(text: str) -> str:
    if not text:
        return ""
    clean = re.sub(r'```[\s\S]*?```', '', text)
    clean = re.sub(r'https?://\S+|www\.\S+', '', clean)
    clean = re.sub(r'\[\d{1,2}:\d{2}\]', '', clean)
    clean = re.sub(r'\[[^\]]*\]|\{[^\}]*\}', '', clean)
    clean = re.sub(r'<[^>]+>', '', clean)
    clean = re.sub(r'\(([A-Da-d])\)', r'\1)', clean)
    clean = re.sub(r'\((?:risos|pausa|vinheta|música|musica|efeito|gargalhadas|suspiro)[^\)]*\)', '', clean, flags=re.IGNORECASE)
    clean = re.sub(r'[\*\`\_\#\~\>]', '', clean)
    clean = clean.replace("&quot;", '"').replace("&amp;", 'e').replace("&lt;", '').replace("&gt;", '')
    clean = clean.replace("&", "e")
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean

def strip_id3(data: bytes) -> bytes:
    while data.startswith(b'ID3') and len(data) >= 10:
        size_bytes = data[6:10]
        tag_size = (
            (size_bytes[0] & 0x7F) << 21 |
            (size_bytes[1] & 0x7F) << 14 |
            (size_bytes[2] & 0x7F) << 7 |
            (size_bytes[3] & 0x7F)
        )
        total_id3_len = 10 + tag_size
        data = data[total_id3_len:]
        
    for i in range(min(len(data) - 1, 512)):
        if data[i] == 0xFF and (data[i+1] & 0xE0) == 0xE0:
            return data[i:]
            
    return data

async def synthesize_speech(text: str, voice: str) -> bytes:
    clean_text = clean_text_for_speech(text)
    if not clean_text:
        return b""
    
    communicate = edge_tts.Communicate(clean_text, voice)
    audio_bytes = bytearray()
    
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_bytes.extend(chunk["data"])
                
    return strip_id3(bytes(audio_bytes))

def parse_sections(script_text: str):
    cfg = load_config()
    h1_name = cfg["hosts"]["host_1"].get("name", "Host1").lower()
    h2_name = cfg["hosts"]["host_2"].get("name", "Host2").lower()

    lines = script_text.strip().split("\n")
    sections = []
    current_title = "Intro"
    current_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Section header check MUST come first before speaker matching (so bracketed titles with colons like [03:00] BLOCO 1: ... are not misidentified as speaker lines)
        if line.startswith("[") and "]" in line:
            if current_lines:
                sections.append((current_title, current_lines))
                current_lines = []
            title_part = line.split("]", 1)[1].strip()
            current_title = title_part if title_part else "Bloco"
            continue

        speaker_match = re.match(r'^(?:\*\*|\*)?\s*([^:\*]+)\s*(?:\*\*|\*)?\s*:\s*(.*)', line)
        if speaker_match:
            raw_speaker = speaker_match.group(1).strip().lower()
            text = speaker_match.group(2).strip()
            if text:
                if h1_name in raw_speaker:
                    speaker_key = "host_1"
                elif h2_name in raw_speaker:
                    speaker_key = "host_2"
                else:
                    speaker_key = "host_1" # default
                current_lines.append((speaker_key, text))
        else:
            # Continuation dialogue line (e.g., options A), B), C), D) or list items without explicit speaker prefix)
            last_speaker = current_lines[-1][0] if current_lines else "host_1"
            current_lines.append((last_speaker, line))
            
    if current_lines:
        sections.append((current_title, current_lines))
        
    return sections

def format_time(seconds: float) -> str:
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"

def format_duration_hhmmss(seconds: float) -> str:
    hours = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{mins:02d}:{secs:02d}"

async def generate_audio_for_episode(ep):
    cfg = load_config()
    v1 = cfg["hosts"]["host_1"].get("voice", "pt-BR-AntonioNeural")
    v2 = cfg["hosts"]["host_2"].get("voice", "pt-BR-FranciscaNeural")
    podcast_link = cfg["podcast"].get("link", "https://seu-usuario.github.io/seu-repositorio").rstrip("/")

    ep_id = ep["id"]
    filename = f"ep{ep_id:02d}_audio.mp3"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    print(f"\n[+] Sintetizando áudio MP3 de alta fidelidade para o Episódio {ep_id}: {ep['title']}...")
    
    sections = parse_sections(ep["script"])
    full_audio = bytearray()
    
    current_time_seconds = 0.0
    dynamic_chapters = []
    BYTES_PER_SECOND = 6000.0  # ~48 kbps mono MP3
    
    for idx, (section_title, dialogues) in enumerate(sections, 1):
        timestamp_str = format_time(current_time_seconds)
        clean_title = re.sub(r'^(INTRODUÇÃO|BLOCO \d+:|ENCERRAMENTO E DICAS)\s*', '', section_title, flags=re.IGNORECASE).strip()
        if not clean_title:
            clean_title = section_title
        
        dynamic_chapters.append((timestamp_str, clean_title))
        section_bytes = 0
        
        print(f"  - Marcador [{timestamp_str}] Cap {idx:02d}: {clean_title}")
        for speaker_key, text in dialogues:
            voice = v1 if speaker_key == "host_1" else v2
            chunk_audio = await synthesize_speech(text, voice)
            if chunk_audio:
                full_audio.extend(chunk_audio)
                section_bytes += len(chunk_audio)
            
        current_time_seconds += (section_bytes / BYTES_PER_SECOND)
        
    with open(filepath, "wb") as f:
        f.write(full_audio)
        
    file_size = len(full_audio)
    total_seconds = file_size / BYTES_PER_SECOND
    duration_str = format_duration_hhmmss(total_seconds)
    
    print(f"[OK] Áudio MP3 gerado com sucesso: {filepath} ({file_size} bytes, Duração: {duration_str})")
    
    ep["audio_url"] = f"{podcast_link}/episodes/{filename}?v={file_size}"
    ep["audio_bytes"] = file_size
    ep["duration"] = duration_str
    ep["local_audio_path"] = filepath
    ep["chapters"] = dynamic_chapters
    
    show_notes = f"🎙️ SOBRE ESTE EPISÓDIO:\n{ep['summary']}\n\n⏱️ CAPÍTULOS E MARCAS DE TEMPO:\n"
    for idx, (time_mark, ch_title) in enumerate(dynamic_chapters, 1):
        show_notes += f"• {time_mark} - Cap {idx:02d}: {ch_title}\n"
        
    if "sources" in ep and ep["sources"]:
        show_notes += "\n🔗 FONTES CITADAS E LINKS RECOMENDADOS:\n"
        for src in ep["sources"]:
            if isinstance(src, (list, tuple)) and len(src) >= 2:
                show_notes += f"• {src[0]}: {src[1]}\n"
                
    ep["description"] = show_notes
    return filepath, file_size
