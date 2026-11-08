# Laboratório de IA Generativa: O Quarto Seguro

Um jogo de aventura textual e visual interativo desenvolvido em **Python**, onde o jogador está preso num quarto digital controlado por uma Inteligência Artificial avançada. As paredes do quarto são ecrãs holográficos que se moldam dinamicamente com base nas ações do jogador e nas decisões do mestre de jogo (IA).

Este projeto demonstra a integração prática e híbrida de modelos de linguagem (LLM) com modelos de difusão de imagem em tempo real utilizando interfaces gráficas modernas.

---

## Funcionalidades Prontas

*   **Mestre de Jogo Inteligente:** Utiliza o modelo `gemini-3-flash-preview` da Google para narrar e reagir ao contexto e histórico das ações do jogador.
*   **Geração Holográfica Dinâmica:** Integração com a API do *Pollinations AI* para atualizar o cenário visual do quarto sempre que a IA dita uma mudança de ambiente.
*   **Filtro Híbrido Contextual:** O código analisa de forma inteligente se a resposta da IA alterou o cenário antes de fazer downloads desnecessários, poupando tráfego de rede.
*   **Efeito Máquina de Escrever:** As respostas da Inteligência Artificial surgem letra a letra no terminal de forma fluida e imersiva.
*   **Mecanismo Antifalhas (Retry):** Sistema automático que deteta instabilidade ou sobrecarga na API de imagem e tenta novamente até 3 vezes com compassos de espera.
*   **Exportação de Imagens:** Botão nativo para salvar as tuas realidades simuladas favoritas diretamente no teu computador em formato `.png` ou `.jpg`.

---

## Tecnologias Utilizadas

*   **Python 3.14+**
*   **CustomTkinter:** Para a interface gráfica escura e moderna (GUI).
*   **Google GenAI SDK:** Para a ligação ao modelo Gemini.
*   **Pillow (PIL) & Requests:** Para manipulação de imagem em memória e requisições HTTP estáveis.
*   **Pollinations AI:** Como motor gratuito de geração de imagens.

---

## Como Instalar e Rodar

### 1. Clonar o Repositório
```bash
git clone https://github.com
cd NOME_DO_REPOSITORIO
```

### 2. Instalar as Dependências
Certifica-te de que tens as bibliotecas necessárias instaladas no teu ambiente Python:
```bash
pip install customtkinter google-genai pillow requests
```

### 3. Configurar as Chaves de API
Cria um ficheiro chamado `Keys.py` na mesma pasta do código principal e adiciona a tua chave do Google AI Studio:
```python
# Keys.py
YourkeyGemini = "A_TUA_CHAVE_API_AQUI"
```
> ⚠️ **Aviso:** Nunca envies o teu ficheiro `Keys.py` real para o GitHub público! Adiciona-o ao teu ficheiro `.gitignore`.

### 4. Executar o Jogo
```bash
python JanelaJogo.py
```

---

## Como Jogar 🎮

1. O jogo começa num quarto branco inicial seguro contra o exterior mortal.
2. Digita as tuas ações ou desejos no campo inferior (ex: *"podes transformar este quarto numa floresta?"* ou *"gera uma bola neste cenário"*).
3. Se a tua ação contiver gatilhos de criação e a IA alterar o prompt visual, os ecrãs holográficos do lado esquerdo vão transmutar-se para refletir a nova realidade.
4. Clica no botão **💾 Salvar Ecrã Holográfico** se quiseres guardar o cenário atualizado no teu disco rígido.

---

## 📝 Licença

Este projeto é de código aberto e livre para fins educativos e de desenvolvimento pessoal.
