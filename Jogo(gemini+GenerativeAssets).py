import customtkinter as ctk
from google import genai
from PIL import Image
import requests
import io
import threading
from Keys import*

# 1. CONFIGURAÇÃO VISUAL DA INTERFACE
ctk.set_appearance_mode("Dark") 
ctk.set_default_color_theme("blue")

# 2. LIGAÇÃO ÀS APIS DA GOOGLE
API_KEY = "keyGemini"
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
    "AI: \"Consegues ouvir-me? Eu sei que estás aí! Gostarias de saber onde estás?\""
)

# NOTA: Substitui por URLs reais de imagens (extensão .jpg/.png) se quiseres carregar da Web
URL_IMAGEM_INICIAL = "https://unsplash.com" 

class JanelaJogo(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Laboratório de IA Generativa: O Quarto Seguro")
        self.geometry("900x650")
        self.resizable(False, False)

        # Inicializar a variável que vai guardar o estado da imagem em memória
        self.imagem_atual_pil = None

        # Inicializar o Chat com o modelo ativo
        self.chat = client.chats.create(
            model="gemini-3-flash-preview",
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
            self.imagem_atual_pil = Image.open(io.BytesIO(resposta.content))
            
            img_ctk = ctk.CTkImage(light_image=self.imagem_atual_pil, dark_image=self.imagem_atual_pil, size=(400, 430))
            self.label_imagem.configure(image=img_ctk, text="")
        except Exception as e:
            # Imagem de fallback caso a internet falhe (Cria um quadrado cinzento temporário)
            self.imagem_atual_pil = Image.new("RGB", (400, 430), color="gray")
            img_ctk = ctk.CTkImage(light_image=self.imagem_atual_pil, dark_image=self.imagem_atual_pil, size=(400, 430))
            self.label_imagem.configure(image=img_ctk, text=f"Modo de segurança ativo: {e}")

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
            prompt_visual_ia = "A futuristic clean white testing room with a square glowing screen on the wall"
            
            if "PROMPT_VISUAL:" in texto_completo:
                partes = texto_completo.split("PROMPT_VISUAL:")
                narrativa = partes[0].strip()
                prompt_visual_ia = partes[1].strip()

            # Mostrar a história na consola de texto
            self.caixa_texto.configure(state="normal")
            self.caixa_texto.insert(ctk.END, f"[IA]: {narrativa}\n\n")
            self.caixa_texto.see(ctk.END)
            self.caixa_texto.configure(state="disabled")

            # 2. PROCESSO DE MODIFICAÇÃO DE IMAGEM
            img_bytes_io = io.BytesIO()
            self.imagem_atual_pil.save(img_bytes_io, format="PNG")
            bytes_para_api = img_bytes_io.getvalue()

            # Gerar nova imagem combinando o prompt
            resultado_imagem = client.models.generate_images(
                model="imagen-3.0-generate-002",
                prompt=f"{prompt_visual_ia}, maintaining the exact same room structure, style and the glowing square screen from the source image",
                config={
                    "number_of_images": 1,
                    "aspect_ratio": "1:1"
                }
                # Se a API Imagen falhar com a imagem base nos testes, podes comentar a linha abaixo
                # e usar puramente geração por texto (Text-to-Image)
                # image=bytes_para_api 
            )
            
            # 3. ATUALIZAR A INTERFACE
            # CORREÇÃO: Aceder ao primeiro índice [0] da lista retornada
            bytes_imagem_nova = resultado_imagem.generated_images[0].image.image_bytes
            self.imagem_atual_pil = Image.open(io.BytesIO(bytes_imagem_nova))
            
            img_ctk = ctk.CTkImage(light_image=self.imagem_atual_pil, dark_image=self.imagem_atual_pil, size=(400, 430))
            self.label_imagem.configure(image=img_ctk, text="")

        except Exception as e:
            self.caixa_texto.configure(state="normal")
            self.caixa_texto.insert(ctk.END, f"[Erro Visual IA]: {e}\n\n")
            self.caixa_texto.see(ctk.END)
            self.caixa_texto.configure(state="disabled")

        self.botao_enviar.configure(state="normal", text="Enviar Ação")

if __name__ == "__main__":
    app = JanelaJogo()
    app.mainloop()
