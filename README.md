# ✈️ Curso Básico de Piloto Privado (PPA) - Podcast Automático com IA

> **O podcast diário automatizado que ensina o conteúdo completo da banca da ANAC, inspeção de voo e manutenção aeronáutica para pilotos iniciantes e entusiastas da aviação!**  
> Gerado 100% de forma automática via **Google Gemini AI**, **Microsoft Azure Neural TTS** e **GitHub Actions**.

- **👨‍💻 Criador do Projeto:** [Raphael Dias](https://github.com/Rapha-Dias)
- **🎧 Ouça no Spotify:** [Curso Básico de Piloto Privado (PPA) no Spotify](https://open.spotify.com/show/033YLFBFRFhv5bpJLlb6QT)
- **🌐 Site Oficial:** [https://rapha-dias.github.io/Post-do-Piloto/](https://rapha-dias.github.io/Post-do-Piloto/)

---

## 🌟 Sobre o Projeto

O **Curso Básico de Piloto Privado (PPA)** foi concebido e criado por **Raphael Dias** com o propósito de **ajudar alunos iniciantes no curso de Piloto Privado de Avião (PPA)** e **pessoas apaixonadas pela aviação civil**.

Diariamente às 07:00 AM (horário de Brasília), a Inteligência Artificial gera uma aula em áudio didática de 10 a 20 minutos, apresentada pela **Cmte. Fernanda (Instrutora INVA)** e seu aluno **Cadu**, com conversas explicativas de cockpit e um **Quiz da Banca ANAC com 3 perguntas práticas comentadas**.

---

## 📅 Grade de Programação Semanal dos Episódios

Cada dia da semana aborda uma matéria essencial do currículo aeronáutico:

| Dia da Semana | Matéria | Conteúdo da Aula |
|---|---|---|
| **Segunda-feira** | 🛩️ **Aerodinâmica e Teoria de Voo** | As 4 forças em voo (Sustentação, Arrasto, Tração e Peso), perfis de asa, ângulo de ataque e prevenção de estol (stall). |
| **Terça-feira** | ⛅ **Meteorologia Aeronáutica** | Pressão atmosférica (QNH/QFE), altimetria, leitura de METAR/TAF, nuvens Cumulonimbus (CB) e nevoeiro. |
| **Quarta-feira** | 📻 **Regulamentos de Tráfego Aéreo** | Regras VFR, classificação de espaços aéreos (Classes A a G), circuito de tráfego e fraseologia de torre. |
| **Quinta-feira** | ⚙️ **Conhecimentos Técnicos** | Motores a explosão de 4 tempos (Ciclo Otto), magnetos de ignição, carburação vs injeção, célula e painel. |
| **Sexta-feira** | 🗺️ **Navegação Aérea** | Navegação estimada e visual, rumos verdadeiros/magnéticos, computador de voo, cartas VFR/WAC e NOTAMs. |
| **Sábado** | 🛠️ **MMA – Mecânico de Manutenção** | Inspeções de 50h, 100h e IAM, entelagem, sistemas hidráulicos e diretrizes de aeronavegabilidade (DA). |
| **Domingo** | 📊 **Resumo da Semana & Notícias** | Recapitulação dos pontos mais cobrados na banca da ANAC, notícias da aviação e motivação para voo solo. |

---

## 🧠 Estrutura de Cada Aula em Áudio

- `[00:00]` **Briefing Inicial:** Introdução com os temas centrais do dia.
- `[03:00]` **Bloco 1:** Conceitos fundamentais e física aplicada à aviação.
- `[08:30]` **Bloco 2:** Cenários práticos no cockpit e aplicação em voo real.
- `[14:00]` **Bloco 3:** Macetes da instrutora e procedimentos de segurança.
- `[18:00]` **Bloco 4: Quiz da Banca ANAC & Cockpit:** 3 perguntas interativas com opções A, B, C, D e gabarito técnico comentado.
- `[21:00]` **Debriefing & Encerramento:** Dicas de estudo e conselho da Comandante.

---

## 👥 Apresentadores (Vozes Neurais da Microsoft Azure)

- 👩‍✈️ **Cmte. Fernanda (Instrutora INVA):** Voz neural didática e segura (`pt-BR-FranciscaNeural`). Piloto experiente com milhares de horas de voo, ensina a matéria da ANAC com autoridade e entusiasmo.
- 👨‍✈️ **Cadu (Aluno PPA):** Voz neural jovem (`pt-BR-AntonioNeural`). Aluno de Piloto Privado em formação, faz as perguntas práticas que todo iniciante tem na preparação para o CMA, exames da ANAC e voo solo.

---

## 📡 Onde Ouvir e Assinar

- 🎧 **Spotify Oficial:** [open.spotify.com/show/033YLFBFRFhv5bpJLlb6QT](https://open.spotify.com/show/033YLFBFRFhv5bpJLlb6QT)
- 🌐 **Site Web Interativo:** [https://rapha-dias.github.io/Post-do-Piloto/](https://rapha-dias.github.io/Post-do-Piloto/)
- 📻 **Feed RSS 2.0 (Para Spotify / Apple Podcasts):** `https://rapha-dias.github.io/Post-do-Piloto/rss.xml`
- 📚 **Materiais de Apoio Recomendados:** [Canal Piloto - Downloads de Aviação](https://canalpiloto.com.br/materiais-para-estudo-de-aviacao-download/)

---

## ⚡ Automação Diária no GitHub Actions

A automação diária em `.github/workflows/daily_podcast.yml` executa diariamente às **07:00 AM (Horário de Brasília)**.

### Configuração da API Key no GitHub:
1. Acesse o seu repositório no GitHub: `https://github.com/Rapha-Dias/Post-do-Piloto`
2. Vá em **Settings** > **Secrets and variables** > **Actions**.
3. Clique em **New repository secret** com o nome `GEMINI_API_KEY` e cole a sua chave do [Google AI Studio](https://aistudio.google.com/).

---

## 💻 Como Rodar e Testar Localmente

```bash
# 1. Clonar o repositório
git clone https://github.com/Rapha-Dias/Post-do-Piloto.git
cd Post-do-Piloto

# 2. Instalar as dependências
pip install -r requirements.txt

# 3. Executar a suíte de testes
python test_all.py

# 4. Gerar um novo episódio manualmente
$env:GEMINI_API_KEY="sua_chave_do_gemini"
python main.py
```

---

## 👤 Criador & Autor

Desenvolvido por **Raphael Dias**  
- **GitHub:** [@Rapha-Dias](https://github.com/Rapha-Dias)  
- **E-mail:** `rdias@live.com`

---

## 📄 Licença

Este projeto é open-source e disponibilizado sob a licença [MIT](LICENSE).
