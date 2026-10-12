import customtkinter as ctk
from google import genai
from PIL import Image
import requests
import io
import threading

# 1. CONFIGURAÇÃO VISUAL DA INTERFACE
ctk.set_appearance_mode("Dark") # Ambiente escuro e imersivo
ctk.set_default_color_theme("blue")

# 2. LIGAÇÃO PREMIUM ÀS APIS DA GOOGLE (Usa a tua API Key do AI Studio)
API_KEY = "COLA_AQUI_A_TUA_CHAVE_DO_GOOGLE"
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

# Imagem padrão inicial (Quarto Branco) gerada em link público para não precisares de assets locais
URL_IMAGEM_INICIAL = "https://unsplash.com"

class JanelaJogo(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Laboratório de IA Generativa: O Quarto Seguro")
        self.geometry("900x650")
        self.resizable(False, False)

        # Inicializar o Chat com o modelo que descobriste ativo
        self.chat = client.chats.create(
            model="gemini-3-flash-preview",
            config={"system_instruction": INSTRUCOES_DO_SISTEMA}
        )

        # --- ESTRUTURA DE LAYOUT (Grelha) ---
        self.grid_columnconfigure(0, weight=1) # Coluna da Esquerda (Imagem)
        self.grid_columnconfigure(1, weight=1) # Coluna da Direita (Texto)

        # --- PAREDE VISUAL (Ecrã Holográfico - Lado Esquerdo) ---
        self.frame_imagem = ctk.CTkFrame(self, width=420, height=450)
        self.frame_imagem.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        self.label_imagem = ctk.CTkLabel(self.frame_imagem, text="A carregar ecrãs holográficos...")
        self.label_imagem.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Carregar a primeira imagem da internet sem precisar de ficheiros locais
        self.atualizar_imagem_da_url(URL_IMAGEM_INICIAL)

        # --- CONSOLE DE NARRATIVA (Lado Direito) ---
        self.caixa_texto = ctk.CTkTextbox(self, width=420, height=450, font=("Courier New", 13))
        self.caixa_texto.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.caixa_texto.insert("0.0", CONTEXTO_INICIAL + "\n\n")
        self.caixa_texto.configure(state="disabled")

        # --- ZONA DE INPUT DO JOGADOR (Fundo) ---
        self.campo_input = ctk.CTkEntry(self, width=680, placeholder_text="Digita a tua ação ou interage com a IA do quarto...")
        self.campo_input.grid(row=1, column=0, columnspan=2, padx=(20, 160), pady=20, sticky="w")
        self.campo_input.bind("<Return>", lambda event: self.disparar_processamento())

        self.botao_enviar = ctk.CTkButton(self, text="Enviar Ação", width=120, command=self.disparar_processamento)
        self.botao_enviar.grid(row=1, column=0, columnspan=2, padx=(0, 20), pady=20, sticky="e")

    def atualizar_imagem_da_url(self, url):
        """Descarrega a imagem da internet e desenha-a no interface."""
        try:
            resposta = requests.get(url, timeout=10)
            img_data = Image.open(io.BytesIO(resposta.content))
            img_ctk = ctk.CTkImage(light_image=img_data, dark_image=img_data, size=(400, 430))
            self.label_imagem.configure(image=img_ctk, text="")
        except Exception as e:
            self.label_imagem.configure(text=f"Erro ao projetar holograma: {e}")

    def disparar_processamento(self):
        """Usa Threads para que a interface gráfica não congele enquanto a IA gera as coisas."""
        texto_jogador = self.campo_input.get().strip()
        if not texto_jogador:
            return
        
        self.campo_input.delete(0, ctk.END)
        
        self.caixa_texto.configure(state="normal")
        self.caixa_texto.insert(ctk.END, f"> Humano: {texto_jogador}\n\n")
        self.caixa_texto.see(ctk.END)
        self.caixa_texto.configure(state="disabled")
        
        self.botao_enviar.configure(state="disabled", text="A gerar...")
        
        # Corre o processo em segundo plano para o ecrã não travar
        threading.Thread(target=self.processar_jogada, args=(texto_jogador,), daemon=True).start()

    def processar_jogada(self, acao):
        try:
            # 1. GERAR TEXTO DA HISTÓRIA
            resposta_ia = self.chat.send_message(acao)
            texto_completo = resposta_ia.text
            
            # Separar a narrativa do prompt visual que pedimos nas instruções do sistema
            narrativa = texto_completo
            prompt_geracao_imagem = "A futuristic clean white testing room, minimalist, cinematic lighting"
            
            if "PROMPT_VISUAL:" in texto_completo:
                partes = texto_completo.split("PROMPT_VISUAL:")
                narrativa = partes[0].strip()
                prompt_geracao_imagem = partes[1].strip()

            # Mostrar a história no ecrã de texto
            self.caixa_texto.configure(state="normal")
            self.caixa_texto.insert(ctk.END, f"[IA]: {narrativa}\n\n")
            self.caixa_texto.see(ctk.END)
            self.caixa_texto.configure(state="disabled")

            # 2. GERAR IMAGEM DINÂMICA (IMAGEN 3) VIA API PREMIUM
            # A IA lê o que aconteceu no quarto e cria uma imagem real na hora!
            resultado_imagem = client.models.generate_images(
                model="imagen-3.0-generate-002",
                prompt=prompt_geracao_imagem,
                config={"number_of_images": 1, "aspect_ratio": "1:1"}
            )
            
            # Extrair os bytes da imagem gerada na Cloud e atualizar a parede esquerda
            bytes_imagem = resultado_imagem.generated_images[0].image.image_bytes
            img_data = Image.open(io.BytesIO(bytes_imagem))
            img_ctk = ctk.CTkImage(light_image=img_data, dark_image=img_data, size=(400, 430))
            self.label_imagem.configure(image=img_ctk, text="")

        except Exception as e:
            self.caixa_texto.configure(state="normal")
            self.caixa_texto.insert(ctk.END, f"[Erro do Sistema]: {e}\n\n")
            self.caixa_texto.configure(state="disabled")

        self.botao_enviar.configure(state="normal", text="Enviar Ação")

if __name__ == "__main__":
    app = JanelaJogo()
    app.mainloop()
