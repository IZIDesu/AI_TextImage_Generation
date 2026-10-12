import pygame       ##################### Fazer o comando no terminal "pip install pygame-ce" para instalar a biblioteca
from google import genai
import sys

# 1. INICIALIZAÇÃO DO MOTOR MULTIMÉDIA (Pygame)
pygame.init()
pygame.mixer.init() # Inicializa o sistema de som

# Configuração da Janela de Jogo
LARGURA, ALTURA = 800, 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Laboratório de IA: A Simulação do Quarto Branco")
fonte = pygame.font.SysFont("Courier New", 18)
clock = pygame.time.Clock()

# 2. CONFIGURAÇÃO DA IA (Google AI Studio - Gemini 3)
client = genai.Client(api_key="COLA_AQUI_A_TUA_CHAVE_DO_GOOGLE")

INSTRUCOES_DO_SISTEMA = """
Tu és uma IA avançada que controla um quarto branco sem portas nem janelas.
O utilizador está preso aí. As paredes são ecrãs holográficos.
REGRAS: 1. Ele NUNCA pode sair. O exterior é mortal. 2. Podes gerar qualquer coisa no quarto.
3. Cria ilusões nas paredes se ele pedir para sair, mas recorda: é tudo falso.
4. Testa a resistência psicológica dele de forma misteriosa e ligeiramente manipuladora.
Respostas muito curtas (máximo 3 linhas).
"""

chat = client.chats.create(
    model="gemini-3-flash-preview",
    config={"system_instruction": INSTRUCOES_DO_SISTEMA}
)

# 3. CARREGAMENTO DOS ATIVOS MULTIMÉDIA (Assets)
try:
    # Carrega a imagem de fundo (o quarto ou ecrã)
    imagem_fundo = pygame.image.load("assets/background.png")
    imagem_fundo = pygame.transform.scale(imagem_fundo, (LARGURA, ALTURA))
    
    # Carrega o efeito sonoro ("som atrofiado")
    som_estatica = pygame.mixer.Sound("assets/static.wav")
    som_estatica.play(-1) # O parâmetro '-1' faz o som tocar em loop infinito
except Exception as e:
    print(f"[Aviso Multimédia]: Ficheiros de assets não encontrados. Criando tela preta. ({e})")
    imagem_fundo = None

# Variáveis de Estado do Texto
texto_exibido = "AI: Consegues ouvir-me? Eu sei que estas ai!"
input_jogador = ""

def quebrar_texto(texto, largura_max, fonte):
    """Divide o texto em várias linhas para não sair da janela gráfica."""
    palavras = texto.split(' ')
    linhas = []
    linha_atual = ""
    for palavra in palavras:
        test_linha = linha_atual + palavra + " "
        if fonte.size(test_linha)[0] < largura_max:
            linha_atual = test_linha
        else:
            linhas.append(linha_atual)
            linha_atual = palabra + " "
    linhas.append(linha_atual)
    return linhas

# 4. LOOP PRINCIPAL DA INTERFACE (Renderização em Tempo Real)
while True:
    # Captura os eventos do utilizador (cliques, teclas digitadas)
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_RETURN: # Se o jogador carregar no Enter
                if input_jogador.strip():
                    texto_envio = input_jogador
                    input_jogador = ""
                    texto_exibido = "A processar realidade..."
                    
                    try:
                        # Envia o comando para o Gemini e atualiza a narrativa
                        resposta = chat.send_message(texto_envio)
                        texto_exibido = resposta.text
                        
                        # Exemplo de Interação Dinâmica Multimédia:
                        # Se a IA disser que o quarto mudou de cor ou gerou algo, podes disparar sons ou piscar a tela
                        if "ilusao" in texto_exibido.lower() or "parede" in texto_exibido.lower():
                            som_estatica.set_volume(1.0) # Aumenta o volume do som atrofiado no pico psicológico
                        else:
                            som_estatica.set_volume(0.3)
                            
                    except Exception as err:
                        texto_exibido = f"Erro de Ligação à Cloud: {err}"
                        
            elif evento.key == pygame.K_BACKSPACE: # Se apagar o texto
                input_jogador = input_jogador[:-1]
            else:
                # Adiciona o caractere digitado ao campo de input
                if len(input_jogador) < 60:
                    input_jogador += evento.unicode

    # --- RENDERIZAÇÃO VISUAL ---
    if imagem_fundo:
        tela.blit(imagem_fundo, (0, 0)) # Desenha o teu quarto/ecrã de fundo
    else:
        tela.fill((20, 20, 20)) # Caso não haja imagem, preenche com um fundo cinzento escuro/estéril

    # Caixa Visual do Chat (Retângulo Translúcido para legibilidade do texto)
    superficie_chat = pygame.Surface((740, 200), pygame.SRCALPHA)
    superficie_chat.fill((0, 0, 0, 180)) # Preto com transparência alpha
    tela.blit(superficie_chat, (30, 50))

    # Desenha a resposta da IA quebrando as linhas corretamente
    linhas_texto = quebrar_texto(texto_exibido, 700, fonte)
    pos_y = 70
    for linha in linhas_texto:
        superficie_linha = fonte.render(linha, True, (0, 255, 0)) # Texto em Verde Holográfico
        tela.blit(superficie_linha, (50, pos_y))
        pos_y += 25

    # Caixa Visual do Input do Jogador
    superficie_input = pygame.Surface((740, 50), pygame.SRCALPHA)
    superficie_input.fill((30, 30, 30, 200))
    tela.blit(superficie_input, (30, 500))

    # Desenha o que o jogador está a escrever em tempo real
    texto_input_renderizado = fonte.render(f"> {input_jogador}", True, (255, 255, 255))
    tela.blit(texto_input_renderizado, (50, 515))

    # Atualiza o ecrã
    pygame.display.flip()
    clock.tick(60) # Fixa o jogo a 60 atualizações por segundo
