import os
import re
import json
from google import genai
from autopodcast.config_loader import load_config

SUBJECT_ROTATION = [
    {
        "key": "Teoria de Voo",
        "prefix": "Aerodinâmica e Teoria de voo",
        "desc": "Estudo das quatro forças em voo (Sustentação, Arrasto, Tração e Peso), sustentação de asas, ângulo de ataque, estol (stall), velocidade de cruzeiro e equilíbrio dinâmico.",
        "fallback_title": "As Quatro Forças em Voo e o Comportamento do Aerofólio",
        "fallback_b1": "Como a Sustentação Vence o Peso e a Tração Vence o Arrasto",
        "fallback_b2": "Ângulo de Ataque Crítico e Como Prevenir e Recuperar um Stall",
        "fallback_b3": "Efeito Solo, Flaps e Estabilidade Longitudinal em Voo",
        "quiz": [
            {
                "q": "O que acontece com a sustentação quando a asa ultrapassa o ângulo de ataque crítico?",
                "options": "A) A sustentação aumenta exponencialmente\nB) A asa entra em estol (stall) e perde sustentação de forma abrupta\nC) O arrasto diminui a zero\nD) A velocidade do avião dobra instantaneamente",
                "answer": "B",
                "exp": "Ao ultrapassar o ângulo de ataque crítico, o fluxo de ar se descola do extradorso da asa, gerando turbulência e provocando o estol (perda abrupta de sustentação)."
            },
            {
                "q": "Em voo reto e nivelado com velocidade constante, qual é a relação entre as forças aerodinâmicas?",
                "options": "A) Sustentação é maior que o Peso e Tração é menor que o Arrasto\nB) Sustentação iguala o Peso e Tração iguala o Arrasto em equilíbrio dinâmico\nC) O Peso é zero e o Arrasto é infinito\nD) A Tração precisa ser 4 vezes maior que a Sustentação",
                "answer": "B",
                "exp": "Em voo reto, nivelado e não acelerado, a sustentação compensa exatamente o peso da aeronave, enquanto a tração do motor vence o arrasto do ar."
            },
            {
                "q": "Qual é a principal função dos flaps durante a aproximação para o pouso?",
                "options": "A) Aumentar apenas a velocidade máxima da aeronave\nB) Aumentar a sustentação e o arrasto, permitindo aproximações mais rampa e menores velocidades de pouso\nC) Desligar o motor para economizar combustível\nD) Travar os comandos de voo",
                "answer": "B",
                "exp": "Os flaps alteram a curvatura do perfil da asa, aumentando a sustentação em baixas velocidades e gerando arrasto para auxiliar na desaceleração e rampa de descida."
            }
        ]
    },
    {
        "key": "Meteorologia",
        "prefix": "Meteorologia Aeronáutica",
        "desc": "Atmosfera padrão, pressão atmosférica, ajuste de altímetro QNH/QNE, leitura e interpretação prática de METAR e TAF, nuvens perigosas como Cumulonimbus (CB) e visibilidade.",
        "fallback_title": "Altimetria, Leitura de METAR e Segurança sob Regras VFR",
        "fallback_b1": "Pressão Atmosférica, Altura x Altitude e Ajuste de QNH",
        "fallback_b2": "Decodificando METAR e TAF de Forma Prática no Cockpit",
        "fallback_b3": "Perigos de Nuvens Cumulonimbus (CB) e Voo em Nevoeiro",
        "quiz": [
            {
                "q": "Qual ajuste altimétrico é utilizado pelo piloto para ler a altitude em relação ao Nível Médio do Mar?",
                "options": "A) QFE\nB) QNH\nC) QNE\nD) QFF",
                "answer": "B",
                "exp": "O QNH é a pressão ajustada para que o altímetro indique a altitude da aeronave acima do Nível Médio do Mar (MSL)."
            },
            {
                "q": "Qual tipo de nuvem é considerada a mais perigosa para a aviação por conter correntes ascendentes violentas, granizo e forte turbulência?",
                "options": "A) Cirrus (CI)\nB) Stratus (ST)\nC) Cumulonimbus (CB)\nD) Altocumulus (AC)",
                "answer": "C",
                "exp": "A nuvem Cumulonimbus (CB) possui grande desenvolvimento vertical, fortes correntes convectivas, formação de gelo, granizo e turbulência severa."
            },
            {
                "q": "No relatório meteorológico METAR, o que indica o grupo 'VFR' ou visibilidade operacional?",
                "options": "A) Que o aeródromo exige voo por instrumentos apenas\nB) As condições de visibilidade horizontal e teto para voo visual seguro\nC) A temperatura do motor da aeronave\nD) O número de passageiros a bordo",
                "answer": "B",
                "exp": "O METAR informa dados de visibilidade horizontal, vento, teto e fenômenos para avaliar se as condições atendem aos mínimos de voo visual (VFR)."
            }
        ]
    },
    {
        "key": "Regulamentos",
        "prefix": "Regulamentos de Tráfego Aéreo",
        "desc": "Regras de Voo Visual (VFR), classificação dos espaços aéreos (A a G), circuito de tráfego, prioridades de passagem no ar e na pista, fraseologia de radiocomunicação.",
        "fallback_title": "Regras VFR, Classes de Espaço Aéreo e Fraseologia de Torre",
        "fallback_b1": "Mínimos Meteorológicos para Voo Visual em Espaço Aéreo Controlado",
        "fallback_b2": "Ingresso no Circuito de Tráfego e Direitos de Passagem",
        "fallback_b3": "Fraseologia Padrão de Radiocomunicação sem Erros",
        "quiz": [
            {
                "q": "Qual é a regra geral para o sentido das curvas em um circuito de tráfego padrão de aeródromo?",
                "options": "A) Todas as curvas devem ser feitas para a direita\nB) Todas as curvas devem ser feitas para a esquerda\nC) O piloto escolhe o lado a cada volta\nD) Curvas em formato de zigue-zague",
                "answer": "B",
                "exp": "Conforme os Regulamentos de Tráfego Aéreo da ANAC/DECEA, o circuito de tráfego padrão é efetuado com curvas pela esquerda, salvo instrução em contrário publicada em VAC."
            },
            {
                "q": "Entre duas aeronaves em rota de convergência na mesma altitude, qual delas tem o direito de passagem?",
                "options": "A) A aeronave mais rápida\nB) A aeronave que avistar a outra à sua direita\nC) A aeronave que estiver com o transponder ligado\nD) A aeronave maior",
                "answer": "B",
                "exp": "Quando duas aeronaves se aproximam em rumos convergentes em altitudes semelhantes, a aeronave que tiver a outra à sua direita deve ceder a passagem."
            },
            {
                "q": "Qual a conduta imediata em caso de falha total de comunicação de rádio em voo VFR em espaço aéreo não controlado?",
                "options": "A) Declarar emergência via paraquedas\nB) Manter voo visual VFR, observar o tráfego do aeródromo e pousar com segurança na pista em uso\nC) Aumentar a altitude para 40.000 pés\nD) Desligar todos os instrumentos",
                "answer": "B",
                "exp": "Em caso de falha de rádio em voo visual, o piloto deve manter as regras VFR, atentar para o tráfego de aeródromo e efetuar o pouso com atenção redobrada."
            }
        ]
    },
    {
        "key": "Conhecimentos Técnicos",
        "prefix": "Conhecimentos Técnicos",
        "desc": "Funcionamento do motor a explosão 4 tempos, sistema de ignição por magnetos, carburação vs injeção, instrumentos giroscópicos e ananóides, célula e helices.",
        "fallback_title": "Motor 4 Tempos, Ignição por Magnetos e Instrumentos do Painel",
        "fallback_b1": "Ciclo Otto nos Motores Aeronáuticos: Admissão, Compressão, Combustão e Escapamento",
        "fallback_b2": "Sistema Duplo de Ignição por Magnetos e Teste de Magnetos na Pré-Voo",
        "fallback_b3": "Funcionamento do Altímetro, Velocímetro, Variômetro e Horizonte Artificial",
        "quiz": [
            {
                "q": "Quais são os quatro tempos do Ciclo Otto nos motores de aviação a pistão?",
                "options": "A) Admissão, Compressão, Combustão e Escapamento\nB) Rotação, Ignição, Pressão e Vácuo\nC) Injeção, Fogo, Fumaça e Parada\nD) Arrasto, Tração, Peso e Subida",
                "answer": "A",
                "exp": "O motor a pistão de quatro tempos opera na sequência: Admissão da mistura ar-combustível, Compressão do pistão, Combustão/Expansão e Escapamento dos gases."
            },
            {
                "q": "Por que os motores de aeronaves utilizam dois magnetos independentes para o sistema de ignição?",
                "options": "A) Para deixar o motor mais silencioso\nB) Por segurança e redundância de ignição, operando independente do sistema elétrico da bateria\nC) Para dobrar a velocidade do avião\nD) Para resfriar o óleo do motor",
                "answer": "B",
                "exp": "Os magnetos geram sua própria corrente de alta tensão para as velas. O sistema duplo garante redundância de segurança em caso de falha em um dos circuitos."
            },
            {
                "q": "Qual instrumento do painel depende exclusivamente da pressão de impacto medida pelo Tubo de Pitot?",
                "options": "A) Altímetro\nB) Velocímetro (Indicador de Velocidade)\nC) Horizonte Artificial\nD) Manômetro de Óleo",
                "answer": "B",
                "exp": "O velocímetro mede a diferença entre a pressão total (de impacto do tubo de Pitot) e a pressão estática."
            }
        ]
    },
    {
        "key": "Navegação Aérea",
        "prefix": "Navegação Aérea",
        "desc": "Navegação estimada e visual, rumos verdadeiros e magnéticos, declinação magnética, uso do computador de voo, leitura de cartas WAC/VFR e boletins NOTAM.",
        "fallback_title": "Planejamento VFR, Cartas Aeronáuticas e o Computador de Voo",
        "fallback_b1": "Projeções de Cartas WAC, Rumos, Protas e Declinação Magnética",
        "fallback_b2": "Cálculo de Consumo de Combustível, Vento e Drift no Computador de Voo",
        "fallback_b3": "Como Consultar NOTAMs e Preparar o Voo de Navegação Solo",
        "quiz": [
            {
                "q": "O que representa o ângulo formado entre o Norte Verdadeiro (Geográfico) e o Norte Magnético em uma carta aeronáutica?",
                "options": "A) Desvio de Bússola\nB) Declinação Magnética (Var)\nC) Rumo Próprio\nD) Altitude de Transição",
                "answer": "B",
                "exp": "A Declinação Magnética é o ângulo entre o meridiano verdadeiro e o meridiano magnético em determinada posição da Terra."
            },
            {
                "q": "Qual é a utilidade do NOTAM (Notice to Airmen) durante o planejamento de voo?",
                "options": "A) Informar dados sobre impostos de combustíveis\nB) Divulgar informações temporárias de segurança, interdição de pistas ou perigos à navegação aérea\nC) Registrar o nome dos passageiros do voo\nD) Medir a pressão da cabine",
                "answer": "B",
                "exp": "O NOTAM transmite informações essenciais sobre o estado operacional de auxílios à navegação, serviços, pistas e perigos temporários no espaço aéreo."
            },
            {
                "q": "Qual computador analógico de navegação é amplamente utilizado por pilotos para cálculos de vento, consumo e velocidade aerodinâmica (TAS)?",
                "options": "A) Calculadora HP 12C\nB) Computador de Voo Jeppesen/E6B\nC) Régua T\nD) GPS de Bolso",
                "answer": "B",
                "exp": "O computador de voo E6B/Jeppesen permite resolver rapidamente triângulos de vento, conversões de unidades e consumo estimado de combustível."
            }
        ]
    },
    {
        "key": "MMA",
        "prefix": "MMA – Mecânico de Manutenção Aeronáutica",
        "desc": "Inspeções de 50h, 100h e IAM (Inspeção Anual de Manutenção), entelagem de asas, reparos estruturais, manutenção preventiva vs corretiva e diretrizes de aeronavegabilidade (DA).",
        "fallback_title": "Manutenção Preventiva, Inspeções de 100h e Estruturas da Aeronave",
        "fallback_b1": "Diferença entre Manutenção Preventiva de Piloto e Manutenção Homologada de MMA",
        "fallback_b2": "Como Funciona uma Inspeção de 100 Horas e a IAM na Prática",
        "fallback_b3": "Estruturas, Entelagem, Proteção contra Corrosão e Cumprimento de DAs",
        "quiz": [
            {
                "q": "Qual é a periodicidade máxima obrigatória da Inspeção Anual de Manutenção (IAM) em aeronaves da aviação geral?",
                "options": "A) A cada 6 meses\nB) A cada 12 meses (anualmente)\nC) A cada 5 anos\nD) Somente quando o motor pifar",
                "answer": "B",
                "exp": "A IAM é realizada obrigatoriamente a cada 12 meses por oficina homologada ou mecânico credenciado pela ANAC."
            },
            {
                "q": "O que é uma Diretriz de Aeronavegabilidade (DA/DAE) emitida pela autoridade de aviação civil?",
                "options": "A) Um folheto promocional de escolas de aviação\nB) Um documento de cumprimento obrigatório para corrigir condição insegura identificada na frota\nC) O manual do proprietário da aeronave\nD) A licença do piloto",
                "answer": "B",
                "exp": "As DAs são determinações regulamentares obrigatórias para sanar deficiências ou problemas de segurança detectados em modelos de aeronaves ou componentes."
            },
            {
                "q": "Qual procedimento faz parte das atribuições de manutenção preventiva autorizadas para o piloto no diário de bordo?",
                "options": "A) Reconstrução total da asa da aeronave\nB) Troca simples de óleo do motor e pequenos retoques de pintura conforme regulamento\nC) Alteração do sistema elétrico principal\nD) Instalação de novo motor sem homologação",
                "answer": "B",
                "exp": "Os regulamentos da ANAC permitem aos pilotos realizar pequenas tarefas simples de manutenção preventiva, como complementação de óleo e pequenos ajustes regulamentados."
            }
        ]
    },
    {
        "key": "Resumo da Semana",
        "prefix": "Resumo da Semana",
        "desc": "Recapitulação dos pontos mais importantes estudados na semana (Teoria, Met, Reg, CT, Nav, MMA), principais notícias da aviação e dicas essenciais para aprovação na ANAC.",
        "fallback_title": "Recapitulação da Semana, Notícias da Aviação e Dicas para a Banca ANAC",
        "fallback_b1": "Revisão dos Pontos Críticos de Aerodinâmica, Regulamentos e Meteorologia",
        "fallback_b2": "Notícias e Destaques Recentes do Setor Aeronáutico no Brasil",
        "fallback_b3": "Estratégia de Resolução de Questões e Preparação Psicológica para o Exame ANAC",
        "quiz": [
            {
                "q": "Ao se deparar com condições meteorológicas de teto ou visibilidade abaixo dos mínimos VFR durante o voo, qual deve ser a decisão do piloto privado?",
                "options": "A) Forçar a entrada na nuvem e tentar voar por instrumentos sem habilitação\nB) Alternar para o aeródromo de apoio mais próximo ou retornar com segurança\nC) Fechar os olhos e manter o rumo\nD) Desligar o motor",
                "answer": "B",
                "exp": "A regra de ouro da aviação VFR é não prosseguir em condições marginais ou IMC. A decisão correta e segura é alternar ou regressar imediatamente."
            },
            {
                "q": "Qual item é considerado indispensável para a segurança do voo durante a inspeção de pré-voo ao redor da aeronave?",
                "options": "A) Drenar água e impurezas do combustível em cada ponto de dreno\nB) Limpar o estofamento da cabine apenas\nC) Ligar o rádio no volume máximo\nD) Tirar fotos da fuselagem",
                "answer": "A",
                "exp": "A drenagem de combustível nos tanques e filtro principal é vital para evitar contaminação por água, sujeira ou detergente antes de cada voo."
            },
            {
                "q": "Qual é a melhor metodologia para garantir 100% de aproveitamento nos exames da banca da ANAC e voo prático?",
                "options": "A) Tentar adivinhar as alternativas no dia da prova\nB) Estudar com antecedência pelos livros didáticos, fazer simulados e praticar a padronização dos checklists\nC) Decorar apenas 10 questões\nD) Não estudar a teoria",
                "answer": "B",
                "exp": "A aprovação e a segurança do voo vêm do estudo consistente nos livros oficiais, resolução de simulados por matéria e rigor no cumprimento de procedimentos."
            }
        ]
    }
]

def get_gemini_api_key():
    for key, val in os.environ.items():
        if "GEMINI" in key.upper() and ("KEY" in key.upper() or "TOKEN" in key.upper() or "API" in key.upper()):
            if val and len(val) > 5:
                return val
    return os.environ.get("GEMINI_API_KEY")

def clean_topic_title(raw_title: str) -> str:
    if not raw_title:
        return "Aviação"
    title = raw_title.strip()
    title = re.sub(r'^(?:Ep\.?|Episódio|EP\d+)\s*\d*[:\-]?\s*', '', title, flags=re.IGNORECASE).strip()
    title = re.sub(r'[\(\[\{].*?[\)\]\}]', '', title).strip()
    title = re.sub(r'^[:\-–—\s]+', '', title).strip()
    return title if title else raw_title

def generate_script_with_ai(news_items, episode_num: int = 1):
    cfg = load_config()
    podcast_title = cfg["podcast"].get("title", "Curso Básico de Piloto Privado (PPA)")
    h1_name = cfg["hosts"]["host_1"].get("name", "Cadu")
    h1_role = cfg["hosts"]["host_1"].get("role", "Aluno Piloto Privado")
    h2_name = cfg["hosts"]["host_2"].get("name", "Cmte. Fernanda")
    h2_role = cfg["hosts"]["host_2"].get("role", "Comandante e Instrutora de Voo Experiente (INVA)")

    subject_info = SUBJECT_ROTATION[(episode_num - 1) % len(SUBJECT_ROTATION)]
    target_prefix = f"EP{episode_num:02d} {subject_info['prefix']}:"

    prompt_rules = f"""
Você é o roteirista sênior do podcast educacional '{podcast_title}'.
Sua missão é gerar um roteiro de podcast LONGO, DIDÁTICO E COMPLETO (duração estimada de 18 a 22 minutos de áudio falado, com no mínimo 3.000 palavras).

OBJETIVO CENTRAL: AJUDAR PILOTOS INICIANTES NO CURSO DE PILOTO PRIVADO (PPA) E ENTUSIASTAS APAIXONADOS PELA AVIAÇÃO.

TEMA OBRIGATÓRIO DESTE EPISÓDIO:
Matéria da Semana: {subject_info['prefix']}
Descrição: {subject_info['desc']}

TÍTULO DO EPISÓDIO DEVE COMECAR ESTRITAMENTE COM: "{target_prefix}" seguido do subtítulo explicativo.

Apresentadores:
- {h1_name}: {h1_role} (Faz perguntas sobre {subject_info['prefix']}, simula dúvidas reais de alunos iniciantes e lê as perguntas do Quiz).
- {h2_name}: {h2_role} (Explica o conteúdo de {subject_info['prefix']} de forma profunda com analogias do cockpit, autoridade e entusiasmo, e responde com a justificativa técnica no Quiz).

ESTRUTURA OBRIGATÓRIA DO ROTEIRO:
1. [00:00] INTRODUÇÃO & BRIEFING (Apresentação dos temas de {subject_info['prefix']}).
2. [03:00] BLOCO 1: {subject_info['fallback_b1']} (Discussão aprofundada com múltiplos exemplos).
3. [08:30] BLOCO 2: {subject_info['fallback_b2']} (Casos práticos de voo e aplicação na ANAC).
4. [14:00] BLOCO 3: {subject_info['fallback_b3']} (Macetes de instrução de voo e cockpit).
5. [18:00] BLOCO 4: QUIZ DA BANCA ANAC & COCKPIT (Obrigatoriamente 3 perguntas interativas com 4 alternativas cada, onde {h1_name} faz a Pergunta e {h2_name} dá a resposta certa com a justificativa técnica detalhada).
6. [21:00] DEBRIEFING E ENCERRAMENTO (Recapitulação e dica final).

REGRAS DE CONTEÚDO E FALA NATURAL DA AVIAÇÃO:
1. NUNCA cite links ou URLs no meio da fala.
2. Use jargões e termos aeronáuticos reais explicados de forma simples.
3. O roteiro DEVE ser extenso e muito detalhado.

Retorne estritamente um objeto JSON com a seguinte estrutura:
{{
  "title": "{target_prefix} [Subtítulo da Aula]",
  "summary": "Resumo detalhado focado em {subject_info['prefix']} com Quiz da ANAC para pilotos iniciantes e entusiastas da aviação.",
  "chapters": [
    ["00:00", "Briefing Inicial: {subject_info['prefix']}"],
    ["03:00", "Bloco 1: {subject_info['fallback_b1']}"],
    ["08:30", "Bloco 2: {subject_info['fallback_b2']}"],
    ["14:00", "Bloco 3: {subject_info['fallback_b3']}"],
    ["18:00", "Bloco 4: Quiz da Banca ANAC & Cockpit"],
    ["21:00", "Debriefing & Conselho da Comandante"]
  ],
  "sources": [
    ["Canal Piloto - Materiais de Estudo de Aviação", "https://canalpiloto.com.br/materiais-para-estudo-de-aviacao-download/"],
    ["Guia Didático Piloto Privado", "https://pt.scribd.com/document/974659764/Guia-Piloto-Privado-de-Aviao-Parte-2-Material-Didatico"]
  ],
  "script": "[00:00] INTRODUÇÃO\\n{h1_name}: ...\\n{h2_name}: ...\\n\\n[03:00] BLOCO 1\\n..."
}}
"""

    api_key = get_gemini_api_key()
    
    formatted_news = ""
    for i, item in enumerate(news_items, 1):
        clean_t = clean_topic_title(item['title'])
        formatted_news += f"{i}. Matéria/Notícia: {clean_t}\n   Resumo: {item['summary']}\n\n"

    if api_key:
        try:
            print(f"[+] Gerando roteiro extenso com QUIZ para '{target_prefix}' via Gemini AI...")
            raw_text = None
            for target_model in ["gemini-flash-latest", "gemini-3.5-flash", "gemini-2.0-flash"]:
                try:
                    response = client.models.generate_content(
                        model=target_model,
                        contents=f"{prompt_rules}\n\nAqui estão as matérias e fontes de estudo:\n{formatted_news}",
                        config={"response_mime_type": "application/json"}
                    )
                    if response and response.text:
                        raw_text = response.text.strip()
                        print(f"[OK] Roteiro gerado com modelo: {target_model}")
                        break
                except Exception as m_err:
                    print(f"[!] Modelo '{target_model}' não disponível para esta chave: {m_err}. Tentando próximo modelo...")
                    continue
            if raw_text.startswith("```"):
                raw_text = re.sub(r'^```(?:json)?\s*', '', raw_text, flags=re.IGNORECASE)
                raw_text = re.sub(r'\s*```$', '', raw_text)
            data = json.loads(raw_text)
            
            if isinstance(data, dict):
                script_text = data.get("script") or data.get("roteiro") or data.get("dialogo")
                title_text = data.get("title") or data.get("titulo") or f"{target_prefix} {subject_info['fallback_title']}"
                if not title_text.startswith(f"EP{episode_num:02d}"):
                    title_text = f"{target_prefix} {clean_topic_title(title_text)}"
                if script_text:
                    data["script"] = script_text
                    data["title"] = title_text
                    data.setdefault("summary", f"Neste episódio do {podcast_title}, a {h2_name} e o aluno {h1_name} exploram {subject_info['prefix']} com um Quiz da ANAC ao final para pilotos iniciantes e apaixonados por aviação.")
                    data.setdefault("chapters", [["00:00", f"Briefing Inicial: {subject_info['prefix']}"]])
                    data.setdefault("sources", [
                        ["Canal Piloto - Materiais de Estudo de Aviação", "https://canalpiloto.com.br/materiais-para-estudo-de-aviacao-download/"],
                        ["Guia Didático Piloto Privado", "https://pt.scribd.com/document/974659764/Guia-Piloto-Privado-de-Aviao-Parte-2-Material-Didatico"]
                    ])
                    print(f"[OK] Roteiro extenso para '{title_text}' gerado com sucesso via Gemini AI!")
                    return data
        except Exception as e:
            print(f"[!] Aviso na API do Gemini: {e}. Utilizando gerador aeronáutico aprofundado de fallback com Quiz.")

    # Fallback didático temático extenso com QUIZ DA ANAC
    print(f"[+] Montando roteiro extenso de fallback com QUIZ para '{target_prefix}'...")
    title = f"{target_prefix} {subject_info['fallback_title']}"
    summary = f"Neste episódio completo do {podcast_title}, a {h2_name} e o aluno {h1_name} abordam os tópicos essenciais de {subject_info['prefix']} e realizam um Quiz da Banca ANAC com 3 perguntas explicadas passo a passo. Feito para pilotos iniciantes e entusiastas da aviação!"
    
    chapters = [
        ["00:00", f"Briefing Inicial & Apresentação: {subject_info['prefix']}"],
        ["03:00", f"Bloco 1: {subject_info['fallback_b1']}"],
        ["08:30", f"Bloco 2: {subject_info['fallback_b2']}"],
        ["14:00", f"Bloco 3: {subject_info['fallback_b3']}"],
        ["18:00", "Bloco 4: Quiz da Banca ANAC & Cockpit (3 Perguntas Práticas)"],
        ["21:00", "Debriefing & Dica de Ouro para Pilotos Iniciantes"]
    ]
    
    sources = [
        ["Canal Piloto - Materiais para Estudo de Aviação", "https://canalpiloto.com.br/materiais-para-estudo-de-aviacao-download/"],
        ["Guia Didático Piloto Privado", "https://pt.scribd.com/document/974659764/Guia-Piloto-Privado-de-Aviao-Parte-2-Material-Didatico"]
    ]

    quiz_items = subject_info.get("quiz", [])
    
    script_lines = [
        "[00:00] INTRODUÇÃO E BRIEFING INICIAL",
        f"{h1_name}: Sejam muito bem-vindos a mais uma aula completa do {podcast_title}! Eu sou o {h1_name}, aluno de Piloto Privado de Avião, e o objetivo do nosso canal é ajudar quem está começando a voar e todas as pessoas que adoram aviação!",
        f"{h2_name}: Olá, aviadores e entusiastas! Eu sou a {h2_name}, instrutora de voo. Hoje nossa aula é super especial sobre {subject_info['prefix']}. Preparamos uma aula completa e, no final, teremos o nosso tradicional Quiz da Banca ANAC com 3 perguntas para testar seus conhecimentos!",
        f"{h1_name}: Sensacional, Comandante! O Quiz da ANAC é a melhor parte para testar o que fixamos na memória. Vamos iniciar os trabalhos abrindo o Bloco 1?",
        f"{h2_name}: Com certeza, {h1_name}! Papel e caneta na mão, alinhando na pista para decolar!",
        
        f"\n[03:00] BLOCO 1: {subject_info['fallback_b1'].upper()}",
        f"{h1_name}: Comandante Fernanda, trazendo o nosso primeiro tópico importante em {subject_info['prefix']}: {subject_info['fallback_b1']}. Como podemos explicar esse conceito para o aluno que está estudando do zero?",
        f"{h2_name}: {h1_name}, em {subject_info['prefix']}, a física e a padronização andam lado a lado. {subject_info['desc']} Na prática de voo, você sente esses efeitos nos comandos da aeronave.",
        f"{h1_name}: E qual é o erro mais comum que os alunos cometem na hora de estudar esse assunto?",
        f"{h2_name}: O erro principal é tentar decorar as fórmulas sem entender o que está acontecendo com a aeronave no ar. Na aviação, você deve sempre associar a teoria à atitude da aeronave e ao painel de instrumentos.",
        f"{h1_name}: Entendi perfeitamente! E como a ANAC costuma abordar esse tema nas provas?",
        f"{h2_name}: A banca gosta de colocar cenários práticos! Por exemplo, perguntando o que acontece quando a velocidade reduz ou a atitude muda abruptamente.",
        
        f"\n[08:30] BLOCO 2: {subject_info['fallback_b2'].upper()}",
        f"{h1_name}: Avançando para o Bloco 2: {subject_info['fallback_b2']}. Como esse conhecimento salva o piloto de situações perigosas no voo real?",
        f"{h2_name}: Esse é um dos pontos mais vitais do nosso treinamento, {h1_name}! Um bom piloto gerencia os riscos antes da decolagem. Saber interpretar esses fatores evita tomadas de decisão precipitadas.",
        f"{h1_name}: E para quem é entusiasta e apaixonado por aviação mas não pretende voar profissionalmente, qual é a importância desse conhecimento?",
        f"{h2_name}: É fascinante porque você passa a compreender toda a operação da aviação civil! Você entende como os voos são planejados com total margem de segurança.",
        
        f"\n[14:00] BLOCO 3: {subject_info['fallback_b3'].upper()}",
        f"{h1_name}: Chegando ao Bloco 3: {subject_info['fallback_b3']}. Comandante, qual é o bisu ou a dica de ouro da instrutora para a hora do voo de instrução no aeroclube?",
        f"{h2_name}: Fazer a inspeção pré-voo rigorosa e seguir o checklist sem pressa! A disciplina no cockpit é o hábito que separa um piloto comum de um aviador excepcional.",
        f"{h1_name}: Que aula sensacional sobre {subject_info['prefix']}! E agora chega o momento mais esperado pelo pessoal..."
    ]

    # BLOCO 4: QUIZ DA BANCA ANAC
    script_lines.extend([
        "\n[18:00] BLOCO 4: QUIZ DA BANCA ANAC & COCKPIT",
        f"{h1_name}: É isso aí, pessoal! Tá na hora do nosso QUIZ DA BANCA ANAC! Preparamos 3 questões práticas sobre {subject_info['prefix']}. Vou ler cada questão com 4 alternativas, e dou alguns segundos para vocês pensarem na resposta!",
        f"{h2_name}: Excelente, {h1_name}! Quero ver todo mundo gabaritando as 3 perguntas de hoje. Vamos à primeira questão!"
    ])

    for q_idx, q_item in enumerate(quiz_items, 1):
        script_lines.extend([
            f"\n{h1_name}: Questão número {q_idx}: {q_item['q']}",
            f"{h1_name}: Opções:\n{q_item['options']}",
            f"{h1_name}: Pensem um pouquinho... Três, dois, um... Comandante Fernanda, qual é a alternativa correta?",
            f"{h2_name}: A alternativa correta é a LETRA {q_item['answer']}! {q_item['exp']}",
            f"{h1_name}: Perfeito, Comandante! Muito clara essa explicação!"
        ])

    script_lines.extend([
        "\n[21:00] DEBRIEFING E ENCERRAMENTO",
        f"{h2_name}: E assim concluímos nosso briefing e o Quiz de hoje! Parabéns a todos que acertaram as questões sobre {subject_info['prefix']}.",
        f"{h1_name}: Não se esqueçam de conferir os materiais de estudo que deixamos no link do Canal Piloto aqui na descrição do episódio. Muito obrigado a todos os alunos iniciantes e amantes da aviação!",
        f"{h2_name}: Bons estudos, excelentes voos, fiquem com Deus e até o nosso próximo episódio!",
        f"{h1_name}: Até lá, pessoal! Bons voos!"
    ])

    return {
        "title": title,
        "summary": summary,
        "chapters": chapters,
        "sources": sources,
        "script": "\n".join(script_lines)
    }
