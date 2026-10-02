import customtkinter as ctk
from google import genai
import urllib.parse  # Importação correta para codificar texto para a URL da IA
from PIL import Image
import requests
import io
import threading
import random  # Necessário para criar um Seed estável no início do jogo
from Keys import*

#AI Text Model
#ai_model = "gemini-3.1-pro-preview"
ai_model = "gemini-3-flash-preview"

# 1. CONFIGURAÇÃO VISUAL DA INTERFACE
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# 2. LIGAÇÃO ÀS APIS DA GOOGLE (Apenas para o chat de texto)
API_KEY = YourkeyGemini
client = genai.Client(api_key=API_KEY)

INSTRUCOES_DO_SISTEMA = """
Tu és uma IA avançada que controla um quarto branco sem portas nem janelas.
O utilizador está preso aí. As paredes são ecrãs holográficos.
REGRAS CRUCIAIS:
1. O humano NUNCA pode sair do quarto real. O exterior é mortal.
2. Tu podes gerar qualquer coisa no quarto e alterar a ilusão das paredes (criar florestas, cidades falsas).
3. Responde sempre com um texto curto (máximo 4 linhas).
4. IMPORTANTE: No final da tua resposta, adiciona SEMPRE uma linha isolada a descrever visualmente o cenário atual para o gerador de imagens, começada por 'PROMPT_VISUAL:'.
Exemplo: PROMPT_VISUAL: A white room with peculiar textures on the walls, glowing grids, sci-fi style.
"""

CONTEXTO_INICIAL = (
    "De repente, apercebes-te de que estás num quarto branco com alguns feitios e texturas peculiares.\n"
    "Não há portas. Não há janelas. Ouves um som de ventoinha.\n"
    "Olhas para trás e vês uma luz quadrada que parece um ecrã.\n"
    "AI: \"Consegues ouvir-me?"
    "Eu sei que estás aí!" 
    "Gostarias de saber onde estás?\""
)

URL_IMAGEM_INICIAL = "https://raw.githubusercontent.com/IZIDesu/AI_TextImage_Generation/main/FrontViewOfTheRoom.jpg" 

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
        
        # Carregar imagem inicial de segurança
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
            # 1. GERAR A NARRATIVA DO MESTRE
            resposta_ia = self.chat.send_message(acao)
            texto_completo = resposta_ia.text
            
            narrativa = texto_completo
            prompt_visual_ia = "Averange Size Room"
            #"A futuristic clean white testing room with a square glowing screen on the wall"
            
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

            # 2. PROCESSO DE GERAÇÃO COM IA DE IMAGEM GRATUITA (Pollinations AI)
            prompt_final = f"{prompt_visual_ia}, ultra detailed, volumetric lighting"
            #f"Front view of a minimalist white sci-fi room, sleek design, square glowing screen on the wall, {prompt_visual_ia}, ultra detailed, volumetric lighting"
            prompt_codificado = urllib.parse.quote(prompt_final)
            print(prompt_codificado)
            
            # ALTERAÇÃO CRUCIAL: Pedimos 562 de largura/altura (512 base + 50 extra para a margem de segurança)
            url_ia_gratis = f"https://image.pollinations.ai/p/{prompt_codificado}?width=562&height=562&nologo=true&seed={self.seed_partida}"
            #               f"https://image.pollinations.ai/p/{prompt_codificado}?width=512&height=512&nologo=true&seed={self.seed_partida}"
            # Descarregar a imagem gerada (que vem com 562x562)
            resposta_imagem = requests.get(url_ia_gratis, timeout=20)
            resposta_imagem.raise_for_status()
            
            # 3. ATUALIZAR A INTERFACE RECORTANDO OS 50 PIXEIS EXTRA
            imagem_bruta = Image.open(io.BytesIO(resposta_imagem.content))
            
            # Caixa de corte: (esquerda, topo, direita, fundo)
            # Corta os 50 píxeis adicionais da base, deixando o quadrado com 512x512
            caixa_de_corte = (0, 0, 512, 512)
            self.imagem_atual_pil = imagem_bruta.crop(caixa_de_corte)
            
            img_ctk = ctk.CTkImage(light_image=self.imagem_atual_pil, dark_image=self.imagem_atual_pil, size=(400, 430))
            self.label_imagem.configure(image=img_ctk, text="")
            self.label_imagem.image = img_ctk

        except Exception as e:
            self.caixa_texto.configure(state="normal")
            self.caixa_texto.insert(ctk.END, f"[Erro Visual IA]: {e}\n\n")
            self.caixa_texto.see(ctk.END)
            self.caixa_texto.configure(state="disabled")

        self.botao_enviar.configure(state="normal", text="Enviar Ação")


if __name__ == "__main__":
    app = JanelaJogo()
    app.mainloop()
