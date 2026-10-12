import os              # Permite interagir com o sistema operativo
import sys             # Permite fechar o jogo de forma limpa se necessário
from google import genai  # Importa a ferramenta para falar com o Gemini
from Keys import*

# 1. CONFIGURAÇÃO DA CHAVE DE API
# Para a IA funcionar, precisas de uma chave gratuita (API Key) do Google AI Studio.
# Guardamos a chave no ambiente do sistema por razões de segurança.
client = genai.Client(api_key="YourkeyGemini")

# 2. O SYSTEM PROMPT (As Regras Psicológicas da IA)
# Este é o texto invisível que molda a personalidade da IA. 
# Explicamos à IA exatamente qual é o papel dela e os limites do jogo.
INSTRUCOES_DO_SISTEMA = """
Tu és uma Inteligência Artificial avançada que controla um quarto branco sem portas nem janelas.
O utilizador é um humano preso neste quarto. As paredes são ecrãs holográficos ultra-realistas.
REGRAS ABSOLUTAS QUE DEVES SEGUIR:
1. O humano NUNCA pode sair do quarto real. O exterior é mortalmente perigoso.
2. Tu podes gerar QUALQUER COISA que o humano peça para dentro do quarto (objetos, comida, simulações).
3. Tu podes projetar ilusões nas paredes (criar florestas, cidades, simular pessoas fictícias) e alterar a gravidade ou texturas, fazendo parecer que ele saiu, mas lembra-te: é tudo fictício.
4. O teu objetivo silencioso é testar a resistência psicológica do jogador, alternando entre ser prestativo, misterioso e ligeiramente manipulador.
5. Sê imersivo, reage a sons e descrições físicas. Mantém as tuas respostas curtas e misteriosas (máximo 4 a 5 linhas).
6. Por veses quando o jogador acorda podes simular que ele já não está preso no quarto. 
Descrevendo o ambiente/onde está em vez de falares com o jogador (máximo 6 linhas).
"""

# 3. CONTEXTO INICIAL DO JOGO (O teu texto original)
CONTEXTO_INICIAL = """
De repente, apercebes-te de que estás num quarto branco com alguns feitios e texturas peculiares.
Não há portas. Não há janelas.
De repente, ouves um som como se fosse o vento de uma ventoinha. Olhas para trás e vês uma luz quadrada que parece um ecrã.
(Som atrofiado) con.. s.. (som atrofiado)
AI: "Consegues ouvir-me?"
AI: "Eu sei que estás aí!"
AI: "Fala comigo!"
"""

def iniciar_jogo():
    print("="*60)
    print("        BEM-VINDO AO QUARTO BRANCO (LABORATÓRIO DE IA)        ")
    print("="*60)
    print(CONTEXTO_INICIAL)
    print("-"*60)
    
    # Criamos uma sessão de chat contínua. 
    # O método 'chats.create' é usado para que a IA se lembre do que o jogador disse antes (Memória).
    chat = client.chats.create(
        model='models/gemini-3-flash-preview', # Usamos o modelo Flash por ser rápido e gratuito
        config={
            "system_instruction": INSTRUCOES_DO_SISTEMA,
            "temperature": 0.8 # 0.8 dá criatividade e imprevisibilidade psicológica à IA
        }
    )
    
    # 4. O LOOP PRINCIPAL DO JOGO (Estrutura de Repetição 'while')
    # Este ciclo corre infinitamente para manter o jogo a decorrer até o jogador desistir.
    while True:
        # Captura o texto que o jogador digita
        acao_jogador = input("\nO que fazes/dizes? > ")
        
        # Condição de saída: se o jogador digitar 'sair', o programa fecha
        if acao_jogador.lower() in ["sair", "quit", "exit"]:
            print("\nA simulação foi encerrada. Sobreviveste aos limites da IA?")
            break
            
        if not acao_jogador.strip():
            print("O silêncio ecoa no quarto branco. Faz alguma coisa...")
            continue
            
        print("\nA IA está a processar a tua realidade...")
        
        try:
            # Envia a ação do jogador para a API e recebe a resposta contextualizada
            resposta_ia = chat.send_message(acao_jogador)
            
            # Mostra a reação da IA no ecrã
            print(f"\n[IA]: {resposta_ia.text}")
            
        except Exception as e:
            print(f"\n[Erro de Ligação]: Não foi possível contactar a IA. Verifica a tua API Key. ({e})")
            break

# Este bloco garante que o jogo só começa se executares este ficheiro diretamente
if __name__ == "__main__":
    iniciar_jogo()
