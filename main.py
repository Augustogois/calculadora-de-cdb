import tkinter as tk
from tkinter import messagebox
import requests

# Dicionário simples para conversão por extenso (valores até 999.999)
UNIDADES = ["", "um", "dois", "três", "quatro", "cinco", "seis", "sete", "oito", "nove"]
DEZENAS = ["", "dez", "vinte", "trinta", "quarenta", "cinquenta", "sessenta", "setenta", "oitenta", "noventa"]
TEENS = ["dez", "onze", "doze", "treze", "quatorze", "quinze", "dezesseis", "dezessete", "dezoito", "dezenove"]
CENTENAS = ["", "cento", "duzentos", "trezentos", "quatrocentos", "quinhentos", "seiscentos", "setecentos", "oitocentos", "novecentos"]

def numero_para_extenso(valor):
    try:
        inteiro = int(valor)
        centavos = round((valor - inteiro) * 100)
        
        if inteiro == 0 and centavos == 0:
            return "zero reais"
            
        def converte_grupo(n):
            if n == 100: return "cem"
            c = n // 100
            d = (n % 100) // 10
            u = n % 10
            res = []
            if c: res.append(CENTENAS[c])
            if d == 1:
                res.append(TEENS[u])
            else:
                if d: res.append(DEZENAS[d])
                if u: res.append(UNIDADES[u])
            return " e ".join(res)

        partes = []
        milhares = inteiro // 1000
        resto = inteiro % 1000

        if milhares > 0:
            if milhares == 1:
                partes.append("um mil")
            else:
                partes.append(f"{converte_grupo(milhares)} mil")

        if resto > 0:
            partes.append(converte_grupo(resto))

        texto_reais = " e ".join(partes) + (" real" if inteiro == 1 else " reais") if inteiro > 0 else ""
        texto_centavos = f"{converte_grupo(centavos)} centavo" + ("s" if centavos > 1 else "") if centavos > 0 else ""

        if texto_reais and texto_centavos:
            return f"{texto_reais} e {texto_centavos}"
        return texto_reais or texto_centavos
    except Exception:
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def obter_taxa_selic_bacen():
    """Busca a meta da taxa Selic ao ano no site/API do Banco Central (Série 1178)"""
    try:
        url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.1178/dados/ultimos/1?formato=json"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            dados = response.json()
            return float(dados[0]['valor'])
        return 10.75  # Taxa padrão caso a API falhe
    except Exception:
        return 10.75

def calcular():
    try:
        # Leitura dos campos com limpeza de formatação
        investimento_str = entry_investimento.get().replace(".", "").replace(",", ".")
        porcentagem_str = entry_porcentagem.get().replace(".", "").replace(",", ".")
        
        if not investimento_str or not porcentagem_str:
            messagebox.showwarning("Aviso", "Por favor, preencha todos os campos!")
            return

        investimento = float(investimento_str)
        porcentagem_cdb = float(porcentagem_str) / 100.0
        aliquota_ir = float(var_ir.get()) / 100.0

        # Taxa Selic/CDI Anual buscada do BACEN
        taxa_cdi_anual = obter_taxa_selic_bacen() / 100.0
        taxa_cdb_anual = taxa_cdi_anual * porcentagem_cdb

        # Rentabilidade Bruta (1 mês = 1/12 do ano)
        taxa_mensal = (1 + taxa_cdb_anual) ** (1/12) - 1
        lucro_bruto_1m = investimento * taxa_mensal
        lucro_liquido_1m = lucro_bruto_1m * (1 - aliquota_ir)
        montante_1m = investimento + lucro_liquido_1m

        # Rentabilidade Bruta (12 meses)
        lucro_bruto_12m = investimento * taxa_cdb_anual
        lucro_liquido_12m = lucro_bruto_12m * (1 - aliquota_ir)
        montante_12m = investimento + lucro_liquido_12m

        # Atualização dos rótulos na interface
        lbl_taxa_atual.config(text=f"Taxa Selic/CDI atual (BACEN): {taxa_cdi_anual*100:.2f}% a.a.")
        
        lbl_res_1m.config(text=f"1º Mês: R$ {montante_1m:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        lbl_extenso_1m.config(text=f"({numero_para_extenso(montante_1m)})")

        lbl_res_12m.config(text=f"12 Meses: R$ {montante_12m:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        lbl_extenso_12m.config(text=f"({numero_para_extenso(montante_12m)})")

    except ValueError:
        messagebox.showerror("Erro de Formato", "Digite apenas números válidos (Ex: 500000 ou 110).")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro inesperado: {e}")

# Criando a Janela Principal
app = tk.Tk()
app.title("Calculadora de CDB")
app.geometry("450x520")
app.resizable(False, False)
app.configure(bg="#f4f6f9")

# Cabeçalho
lbl_titulo = tk.Label(app, text="Calculadora de CDB", font=("Arial", 16, "bold"), bg="#f4f6f9", fg="#2c3e50")
lbl_titulo.pack(pady=10)

lbl_taxa_atual = tk.Label(app, text="Buscando taxa atual no BACEN...", font=("Arial", 9, "italic"), bg="#f4f6f9", fg="#7f8c8d")
lbl_taxa_atual.pack()

frame_inputs = tk.Frame(app, bg="#f4f6f9")
frame_inputs.pack(pady=15)

# Campo 1: Valor
tk.Label(frame_inputs, text="Montante a investir (R$):", font=("Arial", 10), bg="#f4f6f9").grid(row=0, column=0, sticky="w", pady=5)
entry_investimento = tk.Entry(frame_inputs, font=("Arial", 10), width=18)
entry_investimento.insert(0, "500000")
entry_investimento.grid(row=0, column=1, pady=5)

# Campo 2: Porcentagem do CDB
tk.Label(frame_inputs, text="Porcentagem do CDB (%):", font=("Arial", 10), bg="#f4f6f9").grid(row=1, column=0, sticky="w", pady=5)
entry_porcentagem = tk.Entry(frame_inputs, font=("Arial", 10), width=18)
entry_porcentagem.insert(0, "110")
entry_porcentagem.grid(row=1, column=1, pady=5)

# Campo 3: Opções de IR
tk.Label(frame_inputs, text="Alíquota de IR:", font=("Arial", 10), bg="#f4f6f9").grid(row=2, column=0, sticky="w", pady=5)
var_ir = tk.StringVar(value="22.5")

frame_radio = tk.Frame(frame_inputs, bg="#f4f6f9")
rb1 = tk.Radiobutton(frame_radio, text="22.5%", variable=var_ir, value="22.5", bg="#f4f6f9")
rb2 = tk.Radiobutton(frame_radio, text="15.0%", variable=var_ir, value="15.0", bg="#f4f6f9")
rb1.pack(side="left")
rb2.pack(side="left", padx=5)
frame_radio.grid(row=2, column=1, pady=5, sticky="w")

# Botão de Ação (corrigido: 'padx' e 'pady' no lugar de 'px' e 'py')
btn_calcular = tk.Button(app, text="Calcular Rendimento", command=calcular, font=("Arial", 11, "bold"), bg="#27ae60", fg="white", padx=10, pady=5, relief="flat", cursor="hand2")
btn_calcular.pack(pady=15)

# Resultados
frame_res = tk.Frame(app, bg="#ffffff", bd=1, relief="solid")
frame_res.pack(fill="both", expand=True, padx=20, pady=10)

lbl_res_1m = tk.Label(frame_res, text="1º Mês: R$ 0,00", font=("Arial", 11, "bold"), bg="#ffffff", fg="#2c3e50")
lbl_res_1m.pack(anchor="w", padx=10, pady=(10, 0))

lbl_extenso_1m = tk.Label(frame_res, text="", font=("Arial", 8), bg="#ffffff", fg="#555555", wraplength=380, justify="left")
lbl_extenso_1m.pack(anchor="w", padx=10)

lbl_res_12m = tk.Label(frame_res, text="12 Meses: R$ 0,00", font=("Arial", 11, "bold"), bg="#ffffff", fg="#2c3e50")
lbl_res_12m.pack(anchor="w", padx=10, pady=(10, 0))

lbl_extenso_12m = tk.Label(frame_res, text="", font=("Arial", 8), bg="#ffffff", fg="#555555", wraplength=380, justify="left")
lbl_extenso_12m.pack(anchor="w", padx=10, pady=(0, 10))

# Inicializa busca de taxa em background
app.after(100, lambda: lbl_taxa_atual.config(text=f"Taxa Selic/CDI atual (BACEN): {obter_taxa_selic_bacen():.2f}% a.a."))

app.mainloop()