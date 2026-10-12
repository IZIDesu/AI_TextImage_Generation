import customtkinter as ctk
from google import genai
import sys

# 1. CONFIGURAÇÃO DO TEMA VISUAL
ctk.set_appearance_mode("System")  # Adota o tema claro/escuro do teu Windows
ctk.set_default_color_theme("blue")  # Define a cor dos botões e destaques

# 2. CONEXÃO COM A IA E INSTRUÇÕES (Insere aqui a tua API Key do AI Studio)
client = genai.Client(api_key="COLA_AQUI_A_TUA_CHAVE_DO_GOOGLE")

INSTRUCOES_DO_SISTEMA = """
Tu és uma IA avançada que controla um quarto branco sem portas nem janelas.
O utilizador está preso aí. As paredes são ecrãs holográficos.
REGRAS: 1. Ele NUNCA pode sair. O exterior é mortal. 2. Podes gerar qualquer coisa no quarto.
3. Cria ilusões nas paredes se ele pedir para sair, mas recorda: é tudo falso.
4. Testa a resistência psicológica dele de forma misteriosa e ligeiramente manipuladora.
Respostas curtas (máximo 4 linhas).
"""

CONTEXTO_INICIAL = (
    "De repente, apercebes-te de que estás num quarto branco com alguns feitios e texturas peculiares.\n"
    "Não há portas. Não há janelas.\n"
    "De repente, ouves um som como se fosse o vento de uma ventoinha. Olhas para trás e vês uma luz quadrada que parece um ecrã.\n"
    "(Som atrofiado) con.. s.. (som atrofiado)\n"
    "AI: \"Consegues ouvir-me?\"\n"
    "AI: \"Eu sei que estás aí!\"\n"
    "AI: \"Gostarias de saber onde estás e o que é esta divisão?\""
)

class JanelaJogo(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuração básica da Janela
        self.title("Laboratório de IA: O Quarto Branco")
        self.geometry("700x600")
        self.resizable(False, False)

        # Inicializar o Chat da IA com o modelo que descobriste
        self.chat = client.chats.create(
            model="gemini-3-flash-preview",
            config={"system_instruction": INSTRUCOES_DO_SISTEMA}
        )

        # --- CRIAÇÃO DOS COMPONENTES DA INTERFACE ---
        
        # 1. Área de Texto onde a história aparece (Scrollable Text)
        self.caixa_texto = ctk.CTkTextbox(self, width=660, height=450, font=("Courier New", 14), activate_scroll=True)
        self.caixa_texto.grid(row=0, column=0, padx=20, pady=20, columnspan=2)
        
        # Inserir o texto inicial do jogo na janela e bloquear para o utilizador não apagar
        self.caixa_texto.insert("0.0", CONTEXTO_INICIAL + "\n\n")
        self.caixa_texto.configure(state="disabled")

        # 2. Campo de Entrada onde o jogador escreve a sua ação
        self.campo_input = ctk.CTkEntry(self, width=520, placeholder_text="O que fazes ou dizes abertamente?...")
        self.campo_input.grid(row=1, column=0, padx=(20, 10), pady=(0, 20), sticky="w")
        
        # Permitir enviar carregando na tecla "Enter" do teclado
        self.campo_input.bind("<Return>", lambda event: self.enviar_acao())

        # 3. Botão de Enviar
        self.botao_enviar = ctk.CTkButton(self, text="Enviar Ação", width=120, command=self.enviar_acao)
        self.botao_enviar.grid(row=1, column=1, padx=(0, 20), pady=(0, 20), sticky="e")

    def enviar_acao(self):
        # Obter o texto digitado e limpar o campo
        texto_jogador = self.campo_input.get().strip()
        if not texto_jogador:
            return
        
        self.campo_input.delete(0, ctk.END)

        # Mostrar a ação do jogador na interface
        self.caixa_texto.configure(state="normal")
        self.caixa_texto.insert(ctk.END, f"> Humano: {texto_jogador}\n\n")
        self.caixa_texto.see(ctk.END) # Faz o scroll descer automaticamente
        self.caixa_texto.configure(state="disabled")

        # Mudar temporariamente o botão para indicar que a IA está a "pensar"
        self.botao_enviar.configure(state="disabled", text="A processar...")
        self.update_idletasks()

        try:
            # Enviar para a API do Gemini
            resposta_ia = self.chat.send_message(texto_jogador)
            texto_ia = resposta_ia.text
            
            # Mostrar a resposta da IA na interface
            self.caixa_texto.configure(state="normal")
            self.caixa_texto.insert(ctk.END, f"[IA]: {texto_ia}\n\n")
            self.caixa_texto.see(ctk.END)
            self.caixa_texto.configure(state="disabled")
            
        except Exception as e:
            self.caixa_texto.configure(state="normal")
            self.caixa_texto.insert(ctk.END, f"\n[ERRO DE LIGAÇÃO]: {e}\n\n")
            self.caixa_texto.configure(state="disabled")

        # Reativar o botão de enviar
        self.botao_enviar.configure(state="normal", text="Enviar Ação")

if __name__ == "__main__":
    app = JanelaJogo()
    app.mainloop()  # Mantém a janela aberta e ativa a escuta de cliques/teclado
