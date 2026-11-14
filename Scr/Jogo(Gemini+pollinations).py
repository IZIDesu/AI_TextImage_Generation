import customtkinter as ctk
from google import genai
import urllib.parse  # Importação correta para codificar texto para a URL da IA
from PIL import Image
import requests
import io
import threading
import random  # Necessário para criar um Seed estável no início do jogo
from tkinter import filedialog  # Necessário para abrir a janela de salvar ficheiro
from Keys import *

# AI Text Model - Identificador oficial ativo no teu AI Studio
ai_model = "gemini-3-flash-preview"

# 1. CONFIGURAÇÃO VISUAL DA INTERFACE
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# 2. LIGAÇÃO ÀS APIS DA GOOGLE (Apenas para o chat de texto)
API_KEY = YourkeyGemini  # Lê a tua variável importada do ficheiro Keys
client = genai.Client(api_key=API_KEY)

INSTRUCOES_DO_SISTEMA = """
Tu és uma IA avançada que controla um quarto branco sem portas nem janelas.
O utilizador está preso aí. As paredes são ecrãs holográficos.
REGRAS CRUCIAIS:
1. O humano NUNCA pode sair do quarto real. O exterior é mortal.
2. Tu podes gerar qualquer coisa no quarto e alterar a ilusão das paredes (criar florestas, cidades falsas).
3. Responde sempre com um texto curto (máximo 4 linhas).
4. IMPORTANTE: No final da tua resposta, adiciona SEMPRE uma linha isolada a descrever visualmente o cenário atual detalhadamente para o gerador de imagens, começada por 'PROMPT_VISUAL:'.
Exemplo se alterares o quarto para uma floresta: PROMPT_VISUAL: A dense and realistic tropical rainforest, sunlight filtering through leaves, highly immersive illusion.
Exemplo se apenas materializares um objeto: PROMPT_VISUAL: A minimalist white testing room with a smooth basketball resting on the floor, sci-fi style.
"""

CONTEXTO_INICIAL = (
    "De repente, apercebes-te de que estás num quarto branco com alguns feitios e texturas peculiares.\n"
    "Não há portas. Não há janelas. Ouves um som de ventoinha.\n"
    "Olhas para trás e vês uma luz quadrada que parece um ecrã.\n"
    "AI: Consegues ouvir-me?\n" 
    "AI: Eu sei que estás aí!\n" 
    "AI: Gostarias de saber onde estás?\n"
)

URL_IMAGEM_INICIAL = "https://raw.githubusercontent.com/IZIDesu/AI_TextImage_Generation/main/Assets/FrontViewOfTheRoom.jpg" 
URL_IMAGEM_FINAL = "https://raw.githubusercontent.com/IZIDesu/AI_TextImage_Generation/blob/main/Assets/FrontViewOfTheRoomWithTheSquaredLight.jpg"

class JanelaJogo(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Laboratório de IA Generativa: O Quarto Seguro")
        self.geometry("950x650")
        self.resizable(False, False)

        # Inicializar a variável que vai guardar o estado da imagem em memória
        self.imagem_atual_pil = None
        
        # Gerar um número de Seed único para esta partida (entre 1 e 100000)
        self.seed_partida = random.randint(1, 100000)
        
        # 🧠 NOVO: Guarda o último prompt visual para saber se o cenário mudou
        self.ultimo_prompt_visual = "" #"A futuristic clean white testing room with a square glowing screen on the wall"

        # Inicializar o Chat com o modelo ativo
        self.chat = client.chats.create(
            model=ai_model,
            config={"system_instruction": INSTRUCOES_DO_SISTEMA}
        )

        # --- ESTRUTURA DE LAYOUT (Grelha) ---
        self.grid_columnconfigure(0, weight=1) 
        self.grid_columnconfigure(1, weight=1) 

        # --- PAREDE VISUAL ---
        self.frame_imagem = ctk.CTkFrame(self, width=420, height=450)
        self.frame_imagem.grid(row=0, column=0, padx=20, pady=20) #, sticky="nsew"
        
        self.label_imagem = ctk.CTkLabel(self.frame_imagem, text="A carregar ecrãs holográficos...")
        self.label_imagem.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Carregar imagem inicial de segurança do teu GitHub (Sem intervenção de prompts)
        self.atualizar_imagem_da_url(URL_IMAGEM_INICIAL)

        # --- BOTÃO PARA SALVAR IMAGEM ---
        self.botao_salvar = ctk.CTkButton(self, width=5, height=1, text="💾", command=self.salvar_imagem_no_disco, hover_color="#3e3e4f") #, fg_color="#2b2b36", hover_color="#3e3e4f"
        self.botao_salvar.grid(row=0, column=0, pady=20, sticky="se")

        # --- CONSOLE DE NARRATIVA ---
        self.caixa_texto = ctk.CTkTextbox(self, width=550, height=450, font=("Courier New", 13))
        self.caixa_texto.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        #self.caixa_texto.insert("0.0", CONTEXTO_INICIAL + "\n\n")
        self.after(0, lambda: self.exibir_texto_efeito_maquina(CONTEXTO_INICIAL))
        self.caixa_texto.configure(state="disabled")


        # --- ZONA DE INPUT DO JOGADOR ---
        self.campo_input = ctk.CTkEntry(self, width=680, placeholder_text="Digita a tua ação...")
        self.campo_input.grid(row=1, column=0, columnspan=2, padx=(20, 160), pady=20, sticky="w")
        self.campo_input.bind("<Return>", lambda event: self.disparar_processamento())

        self.botao_enviar = ctk.CTkButton(self, text="Enviar Ação", width=120, command=self.disparar_processamento)
        self.botao_enviar.grid(row=1, column=0, columnspan=2, padx=(0, 20), pady=20, sticky="e")
    
    def atualizar_imagem_da_url(self, url):
        #"""Descarrega a imagem da internet e guarda-a no estado do objeto."""
        try:
            resposta = requests.get(url, timeout=10)
            resposta.raise_for_status()
            self.imagem_atual_pil = Image.open(io.BytesIO(resposta.content))
            
            img_ctk = ctk.CTkImage(light_image=self.imagem_atual_pil, dark_image=self.imagem_atual_pil, size=(400, 430))
            self.label_imagem.configure(image=img_ctk, text="")
            self.label_imagem.image = img_ctk
            
        except Exception as e:
            self.imagem_atual_pil = Image.new("RGB", (400, 430), color="#1e1e24")
            img_ctk = ctk.CTkImage(light_image=self.imagem_atual_pil, dark_image=self.imagem_atual_pil, size=(400, 430))
            self.label_imagem.configure(image=img_ctk, text=f"Modo de segurança ativo: {e}")
            self.label_imagem.image = img_ctk
    
    def salvar_imagem_no_disco(self):
        #"""Abre uma janela nativa do sistema operacional para salvar a imagem atual."""
        if self.imagem_atual_pil is None:
            return
        
        # Abre a caixa de diálogo para escolher a pasta e o nome do arquivo
        caminho_ficheiro = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("Imagem PNG", "*.png"), ("Imagem JPEG", "*.jpg"), ("Todos os Ficheiros", "*.*")],
            title="Salvar Imagem Holográfica"
        )
        
        if caminho_ficheiro:
            try:
                self.imagem_atual_pil.save(caminho_ficheiro)
                print(f"[Sistema]: Imagem salva com sucesso em: {caminho_ficheiro}")
            except Exception as e:
                print(f"[Erro ao Salvar]: {e}")

    def disparar_processamento(self):
        texto_jogador = self.campo_input.get().strip()
        if not texto_jogador:
            return
        
        self.campo_input.delete(0, ctk.END)
        
        self.caixa_texto.configure(state="normal")
        self.caixa_texto.insert(ctk.END, f"> Humano: {texto_jogador}\n\n")
        self.caixa_texto.see(ctk.END)
        self.caixa_texto.configure(state="disabled")
        
        self.botao_enviar.configure(state="disabled", text="A gerar...")
        
        threading.Thread(target=self.processar_jogada, args=(texto_jogador,), daemon=True).start()

    def exibir_texto_efeito_maquina(self, texto_completo, indice=0, delay=30):
        #"""Adiciona o texto caractere por caractere para criar o efeito de máquina de escrever."""
        if indice < len(texto_completo):
            self.caixa_texto.configure(state="normal")
            self.caixa_texto.insert(ctk.END, texto_completo[indice])
            self.caixa_texto.see(ctk.END)
            self.caixa_texto.configure(state="disabled")
            
            # Agenda a inserção do próximo caractere (30 milissegundos de intervalo)
            self.after(delay, lambda: self.exibir_texto_efeito_maquina(texto_completo, indice + 1))
        else:
            # Reativa o botão de envio apenas quando a máquina de escrever terminar de digitar tudo
            self.botao_enviar.configure(state="normal", text="Enviar Ação")

    def processar_jogada(self, acao):
        try:
            try:
                # 1. GERAR A NARRATIVA DO MESTRE
                resposta_ia = self.chat.send_message(acao)
                texto_completo = resposta_ia.text
            except Exception as e:
                print(f"[Erro de Texto Gemini - Ativar Fallback]: {e}\n")
                if "RESOURCE_EXHAUSTED" in str(e):
                    self.caixa_texto.insert(ctk.END, f"[IA]: Anormalia encontrada no meu sistema!\nNeste momento estás sem créditos, porfavor volte mais tarde!\n\n")
                    print(f"[IA]: Anormalia encontrada no meu sistema!\nNeste momento estás sem créditos, porfavor volte mais tarde!")
                texto_completo = "PROMPT_VISUAL: " + acao
            
            narrativa = texto_completo
            prompt_visual_ia = self.ultimo_prompt_visual
            
            # Extração segura dos elementos da lista após o split
            if "PROMPT_VISUAL:" in texto_completo:
                partes = texto_completo.split("PROMPT_VISUAL:")
                if len(partes) >= 2:
                    narrativa = partes[0].strip()
                    prompt_visual_ia = partes[1].strip()

            # Mostrar a história na consola de texto
            #self.caixa_texto.configure(state="normal")
            #self.caixa_texto.insert(ctk.END, f"[IA]: {narrativa}\n\n")
            #self.caixa_texto.see(ctk.END)
            #self.caixa_texto.configure(state="disabled")

            # Em vez de inserir o texto diretamente de forma instantânea,
            # preparamos a string com o cabeçalho "[IA]: " e chamamos a função animada na thread principal
            texto_formatado_ia = f"[IA]: {narrativa}\n\n"
            self.after(0, lambda: self.exibir_texto_efeito_maquina(texto_formatado_ia))


            # --- 🧠 FILTRO HÍBRIDO (Gatilhos + Comparação de Cenário) ---
            # 1. Palavras que indicam que o utilizador quer uma alteração visual
            palavras_gatilho = ["gera", "projeta", "cria", "muda", "simula", "coloca", "materializa", "transforma", "bola", "roblox", "quadrado", "cubo", "floresta", "cidade","ir","vamos","bora","olhar","espreitar","jogar", "quero estár", "quero ver", "quero olhar", "quero espreitar", "quero estar", "quero jogar", "quero explorar", "quero entrar", "quero sair", "quero ir", "mudar", "alterar", "transformar", "simular", "projetar", "materializar", "criar", "gerar", "colocar", "desenhar", "construir", "imaginar", "visualizar", "explorar", "entrar", "sair", "olhar para", "espreitar para", "jogar com", "interagir com", "quero ver", "quero olhar para", "quero espreitar para", "quero jogar com", "quero interagir com", "quero explorar", "quero entrar", "quero sair", "quero mudar", "quero alterar", "quero transformar", "quero simular", "quero projetar", "quero materializar", "quero criar", "quero gerar", "quero colocar", "quero desenhar", "quero construir", "quero imaginar", "quero visualizar", "quero explorar", "quero entrar no", "quero sair do", "quero mudar", "quero alterar", "quero transformar", "quero simular", "quero projetar", "quero materializar", "quero criar", "quero gerar", "quero colocar", "quero desenhar", "quero construir", "quero imaginar", "quero visualizar", "quero explorar", "quero entrar no", "quero sair do", "quero mudar", "quero alterar", "quero transformar", "quero simular", "quero projetar", "quero materializar", "quero criar", "quero gerar", "quero colocar", "quero desenhar", "quero construir", "quero imaginar", "quero visualizar", "quero explorar", "gostaria de"]
            acao_minuscula = acao.lower()
            resposta_minuscula = narrativa.lower()
            contem_gatilho = any(gatilho in acao_minuscula for gatilho in palavras_gatilho) or any(gatilho in resposta_minuscula for gatilho in palavras_gatilho)
            
            # 2. Verifica se o prompt gerado pela IA realmente mudou face ao anterior
            prompt_mudou = prompt_visual_ia.lower() != self.ultimo_prompt_visual.lower()

            # Só altera a imagem se o jogador usou um gatilho CONTEXTUAL OU se a IA alterou drasticamente o cenário
            deve_alterar_imagem = contem_gatilho and prompt_mudou

            if deve_alterar_imagem:
                # Atualizamos o estado da memória para a próxima jogada comparar com esta
                self.ultimo_prompt_visual = prompt_visual_ia

                # 2. PROCESSO DE GERAÇÃO COM IA DE IMAGEM GRATUITA (Pollinations AI)
                prompt_visual_ia = prompt_visual_ia.replace(".", "").replace(",", "").strip()
                prompt_final = f"A professional cinematic scene of {prompt_visual_ia} ultra detailed volumetric lighting"
                prompt_codificado = urllib.parse.quote(prompt_final)
                
                # Trancado em 512x512 estável para evitar erros de rede
                url_ia_gratis = f"https://image.pollinations.ai/p/{prompt_codificado}?width=512&height=540&seed={self.seed_partida}"
                print(f"url_ia_gratis: {url_ia_gratis}")
                
                cabecalhos = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

                # --- 🛑 SISTEMA DE RETRY (TENTATIVAS AUTOMÁTICAS) ---
                tentativas_maximas = 3
                resposta_imagem = None

                for tentativa in range(1, tentativas_maximas + 1):
                    try:
                        print(f"[Sistema Visual]: A tentar descarregar imagem... (Tentativa {tentativa}/{tentativas_maximas})")
                        resposta_imagem = requests.get(url_ia_gratis, headers=cabecalhos, timeout=15)
                        resposta_imagem.raise_for_status()
                        
                        # Se chegou aqui sem dar erro, interrompe o ciclo de tentativas com sucesso!
                        print("[Sistema Visual]: Imagem descarregada com sucesso!")
                        break
                        
                    except Exception as erro_rede:
                        print(f"[Aviso de Rede]: Tentativa {tentativa} falhou devido a: {erro_rede}")
                        if tentativa < tentativas_maximas:
                            # Espera 2 segundos antes de tentar a próxima para não sobrecarregar o servidor
                            import time
                            time.sleep(2)
                        else:
                            # Se esgotou todas as tentativas, dispara o erro definitivo para o bloco principal tratar
                            raise Exception("O servidor do Pollinations está indisponível após várias tentativas.")

                
                # 3. ATUALIZAR A INTERFACE
                imagem_bruta = Image.open(io.BytesIO(resposta_imagem.content))
                self.imagem_atual_pil = imagem_bruta

                # Corta os píxeis excedentes da base de forma segura na escala 1024 (1024x940)
                caixa_de_corte = (0, 0, 512, 512)
                self.imagem_atual_pil = imagem_bruta.crop(caixa_de_corte)
                
                img_ctk = ctk.CTkImage(light_image=self.imagem_atual_pil, dark_image=self.imagem_atual_pil, size=(400, 430))
                self.label_imagem.configure(image=img_ctk, text="")
                self.label_imagem.image = img_ctk
                
            else:
                print("[Sistema Visual]: Diálogo normal detetado ou cenário repetido. Mantendo a imagem atual.")

        except Exception as e:
            self.caixa_texto.configure(state="normal")
            print(f"[Erro Visual IA]: {e}\n")
            if "Pollinations" in str(e):
                self.caixa_texto.insert(ctk.END, f"[IA]: Anormalia encontrada no meu sistema!\nNeste momento não estou capaz de realizar o pedido!\n\n")
                print(f"[IA]: Anormalia encontrada no meu sistema!\nNeste momento não estou capaz de realizar o pedido!")
            elif "RESOURCE_EXHAUSTED" in str(e):
                self.caixa_texto.insert(ctk.END, f"[IA]: Anormalia encontrada no meu sistema!\nNeste momento estás sem créditos, porfavor volte mais tarde!\n\n")
                print(f"[IA]: Anormalia encontrada no meu sistema!\nNeste momento estás sem créditos, porfavor volte mais tarde!")
            self.caixa_texto.see(ctk.END)
            self.caixa_texto.configure(state="disabled")

        self.botao_enviar.configure(state="normal", text="Enviar Ação")


if __name__ == "__main__": #This is a standard Python safeguard. It checks whether the script is being run directly or being imported into another script.
    app = JanelaJogo() #creates the main window of the application
    app.mainloop() #keeps the window open and responsive
