import customtkinter as ctk
from google import genai
import urllib.parse  # Importação correta para codificar texto para a URL da IA
from PIL import Image
import requests
import io
import threading
import random  # Necessário para criar um Seed estável no início do jogo
from Keys import *

# AI Text Model - Identificador oficial ativo no teu AI Studio
ai_model = "gemini-3-flash-preview"

# 1. CONFIGURAÇÃO VISUAL DA INTERFACE
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# 2. LIGAÇÃO ÀS APIS DA GOOGLE (Apenas para o chat de texto)
API_KEY = YourkeyGemini  # Corrigido para ler a tua variável importada do ficheiro Keys
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

class JanelaJogo(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Laboratório de IA Generativa: O Quarto Seguro")
        self.geometry("900x650")
        self.resizable(False, False)

        # Inicializar a variável que vai guardar o estado da imagem em memória
        self.imagem_atual_pil = None
        
        # Gerar um número de Seed único para esta partida (entre 1 e 100000)
        self.seed_partida = random.randint(1, 100000)

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
        self.frame_imagem.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        self.label_imagem = ctk.CTkLabel(self.frame_imagem, text="A carregar ecrãs holográficos...")
        self.label_imagem.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Carregar imagem inicial de segurança do teu GitHub (Sem intervenção de prompts)
        self.atualizar_imagem_da_url(URL_IMAGEM_INICIAL)

        # --- CONSOLE DE NARRATIVA ---
        self.caixa_texto = ctk.CTkTextbox(self, width=420, height=450, font=("Courier New", 13))
        self.caixa_texto.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.caixa_texto.insert("0.0", CONTEXTO_INICIAL + "\n\n")
        self.caixa_texto.configure(state="disabled")

        # --- ZONA DE INPUT DO JOGADOR ---
        self.campo_input = ctk.CTkEntry(self, width=680, placeholder_text="Digita a tua ação...")
        self.campo_input.grid(row=1, column=0, columnspan=2, padx=(20, 160), pady=20, sticky="w")
        self.campo_input.bind("<Return>", lambda event: self.disparar_processamento())

        self.botao_enviar = ctk.CTkButton(self, text="Enviar Ação", width=120, command=self.disparar_processamento)
        self.botao_enviar.grid(row=1, column=0, columnspan=2, padx=(0, 20), pady=20, sticky="e")
    
    def atualizar_imagem_da_url(self, url):
        """Descarrega a imagem da internet e guarda-a no estado do objeto."""
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

    def processar_jogada(self, acao):
        try:
            try:
                # 1. GERAR A NARRATIVA DO MESTRE
                resposta_ia = self.chat.send_message(acao)
                texto_completo = resposta_ia.text
            except Exception as e:
                print(f"[Erro de Texto Gemini - Ativar Fallback]: {e}\n")
                texto_completo = "PROMPT_VISUAL: " + acao
            
            narrativa = texto_completo
            prompt_visual_ia = "" #"A minimalistic white testing room, sci-fi style"
            
            # Extração segura dos elementos da lista após o split
            if "PROMPT_VISUAL:" in texto_completo:
                partes = texto_completo.split("PROMPT_VISUAL:")
                if len(partes) >= 2:
                    narrativa = partes[0].strip()
                    prompt_visual_ia = partes[1].strip()

            # Mostrar a história na consola de texto
            self.caixa_texto.configure(state="normal")
            self.caixa_texto.insert(ctk.END, f"[IA]: {narrativa}\n\n")
            self.caixa_texto.see(ctk.END)
            self.caixa_texto.configure(state="disabled")

            # --- 🛑 NOVO FILTRO DE PALAVRAS-CHAVE ---
            # Definimos os gatilhos que dão ordem para alterar a imagem do quarto
            palavras_gatilho = ["gera", "projeta", "cria", "muda", "simula", "coloca", "materializa", "transforma", "bola", "roblox"]
            
            # Converte a ação do jogador para minúsculas para uma verificação segura
            acao_minuscula = acao.lower()
            
            # O Python verifica se ALGUMA das palavras gatilho está presente na frase do utilizador
            deve_alterar_imagem = any(gatilho in acao_minuscula for gatilho in palavras_gatilho)

            if deve_alterar_imagem:
                # 2. PROCESSO DE GERAÇÃO COM IA DE IMAGEM GRATUITA (Pollinations AI)
                prompt_visual_ia = prompt_visual_ia.replace(".", "").replace(",", "").strip()
                prompt_final = f"A professional cinematic scene of {prompt_visual_ia} ultra detailed volumetric lighting"
                prompt_codificado = urllib.parse.quote(prompt_final)
                
                # Resolução padrão estável de 512x512 para o Pollinations rodar sem erro 500 ou 402
                url_ia_gratis = f"https://image.pollinations.ai/p/{prompt_codificado}?width=512&height=540&seed={self.seed_partida}"
                print(f"url_ia_gratis: {url_ia_gratis}")
                
                cabecalhos = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                resposta_imagem = requests.get(url_ia_gratis, headers=cabecalhos, timeout=25)
                resposta_imagem.raise_for_status()
                
                # 3. ATUALIZAR A INTERFACE COM A NOVA IMAGEM GERADA
                self.imagem_atual_pil = Image.open(io.BytesIO(resposta_imagem.content))
                
                img_ctk = ctk.CTkImage(light_image=self.imagem_atual_pil, dark_image=self.imagem_atual_pil, size=(400, 430))
                self.label_imagem.configure(image=img_ctk, text="")
                self.label_imagem.image = img_ctk
  
                # 3. ATUALIZAR A INTERFACE RECORTANDO A MARGEM EXTRA PROPORCIONALMENTE
                imagem_bruta = Image.open(io.BytesIO(resposta_imagem.content))

                # Corta os píxeis excedentes da base de forma segura na escala 1024 (1024x940)
                caixa_de_corte = (0, 0, 512, 512)
                self.imagem_atual_pil = imagem_bruta.crop(caixa_de_corte)

                img_ctk = ctk.CTkImage(light_image=self.imagem_atual_pil, dark_image=self.imagem_atual_pil, size=(400, 430))
                self.label_imagem.configure(image=img_ctk, text="")
                self.label_imagem.image = img_ctk
                
            else:
                print("[Sistema Visual]: Nenhuma palavra-chave detetada. A manter o cenário atual.")

        except Exception as e:
            self.caixa_texto.configure(state="normal")
            print(f"[Erro Visual IA]: {e}\n")
            self.caixa_texto.see(ctk.END)
            self.caixa_texto.configure(state="disabled")

        self.botao_enviar.configure(state="normal", text="Enviar Ação")

if __name__ == "__main__":
    app = JanelaJogo()
    app.mainloop()
