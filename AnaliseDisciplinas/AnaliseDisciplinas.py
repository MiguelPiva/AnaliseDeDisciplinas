import pandas as pd
from flask import Flask, render_template, request


# Variáveis Globais
# //////////////////////////////////////////////////////////
app = Flask(__name__)
df = pd.read_excel("AnaliseDisciplinas\catalogo_disciplinas_graduacao_2022_2023_3010.xlsx")


# Classe Disciplina
# //////////////////////////////////////////////////////////
class Disciplina:
    def __init__(self, indice) -> None:
        self.sigla = df.loc[indice, "SIGLA"]
        self.nome = df.loc[indice, "DISCIPLINA"]
        self.tpei = df.loc[indice, "TPEI"]
        self.recomendacao = df.loc[indice, "RECOMENDAÇÃO"]
        self.objetivos = df.loc[indice, "OBJETIVOS"]
        self.ementa = df.loc[indice, "EMENTA"]
        self.bibliografia_basica = df.loc[indice, "BIBLIOGRAFIA BÁSICA"]
        self.bibliografia_complementar = df.loc[indice, "BIBLIOGRAFIA COMPLEMENTAR"]
        self.concluida = df.loc[indice, "FEITO"]

    def ementa_formatada(self):
        lista_ementa = []
        ementa = self.ementa.replace(".", "\n")
        for assunto in ementa.split("\n"):
            lista_ementa.append(assunto)

        return lista_ementa


# Busca o índice da disciplina na tabela
# //////////////////////////////////////////////////////////
def pegar_índice(nome):
    indice = df.index[df['DISCIPLINA'] == nome].tolist().pop()

    return indice


# Páginas Flask
# //////////////////////////////////////////////////////////
@app.route("/", methods=["GET","POST"])
def home():
    if request.method == "POST":
        nome_disciplina = request.form["campo_disciplina"]
        try:
            indice = pegar_índice(nome_disciplina)
            disciplina = Disciplina(indice)
        except:
            return render_template("index.html", placeholder="Disciplina não encontrada")

        return render_template("index.html", placeholder=disciplina.nome, tpei=disciplina.tpei, codigo=disciplina.sigla, concluida=disciplina.concluida, recomendacao=disciplina.recomendacao, ementa=disciplina.ementa_formatada(), objetivos=disciplina.objetivos)
        
    return render_template("index.html", placeholder="Digite o nome da disciplina")


# Inicia o Flask
# //////////////////////////////////////////////////////////
if __name__ == "__main__":
    app.run(debug=True, host = "0.0.0.0", port=80) 