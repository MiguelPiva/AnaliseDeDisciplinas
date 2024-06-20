import sqlite3
from pathlib import Path
from flask import Flask, render_template, request


# Variáveis do escopo global
# //////////////////////////////////////////////////////////
ROOT_PATH = Path(__file__).parent

app = Flask(__name__)
conexao = sqlite3.connect(    ROOT_PATH / "catalogo_disciplinas.sqlite", check_same_thread=False)
cursor = conexao.cursor()
tupla_disciplinas = tuple()


# Classe Disciplina
# //////////////////////////////////////////////////////////
class Disciplina:
    def __init__(self, indice) -> None:
        disciplina = cursor.execute(
            "SELECT * FROM disciplinas WHERE id = (?);", (indice,)
        ).fetchone()
        self.sigla = disciplina[1]
        self.nome = disciplina[2]
        self.tpei = disciplina[3]
        self.objetivos = disciplina[4]
        self.ementa = disciplina[5]
        self.concluida = disciplina[6]
        self.recomendacao = disciplina[7]

    def recomendacao_formatada(self) -> list:
        recomendacao = self.recomendacao.split(";")
        for disciplina in range(len(recomendacao)):
            recomendacao[disciplina] = recomendacao[disciplina].strip()

        return recomendacao

    def ementa_formatada(self) -> list:
        lista_ementa = []
        ementa = self.ementa.replace(".", "\n")
        for assunto in ementa.split("\n"):
            lista_ementa.append(assunto)

        return lista_ementa

    def objetivos_formatados(self) -> str:
        if str(self.objetivos) == "None":
            return "Não há objetivos cadastrados para esta disciplina"
        else:
            return self.objetivos

    def procurar_recomendam(self) -> tuple:
        cursor.execute(
            'SELECT nome FROM disciplinas WHERE recomendacao LIKE (?);',
            (f"%{self.nome}%",)
        )
        recomendam = [recomenda[0] for recomenda in cursor.fetchall()]
        if len(recomendam) == 0:
            return ["Nenhuma disciplina recomenda esta disciplina"]
        else:
            return recomendam


# Lista o nome de todas as disciplinas do banco de dados
# //////////////////////////////////////////////////////////
def listar_disciplinas() -> tuple:
    cursor.execute("SELECT nome FROM disciplinas;")
    nomes_disciplinas = cursor.fetchall()
    tupla_disciplinas = tuple([nome[0] for nome in nomes_disciplinas])
    print("==> Disciplinas listadas")
    return tupla_disciplinas


# Busca o índice da disciplina na tabela do Excel
# //////////////////////////////////////////////////////////
def pegar_indice(nome) -> int:
    indice = cursor.execute(
        f"SELECT id FROM disciplinas WHERE nome = (?);", (nome,)
    ).fetchone()[0]
    print("Disciplina: ", nome, "\nÍndice: ", indice)
    return indice


# Páginas Flask
# //////////////////////////////////////////////////////////
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        nome_disciplina = request.form["campo_disciplina"]

        try:
            indice = pegar_indice(nome_disciplina)
            disciplina = Disciplina(indice)
        except:
            return render_template(
                "index.html",
                placeholder="Disciplina não encontrada",
                disciplinas=tupla_disciplinas,
            )

        return render_template(
            "index.html",
            placeholder=disciplina.nome,
            tpei=disciplina.tpei,
            codigo=disciplina.sigla,
            concluida=disciplina.concluida,
            recomendacao=disciplina.recomendacao_formatada(),
            ementa=disciplina.ementa_formatada(),
            objetivos=disciplina.objetivos_formatados(),
            recomendam=disciplina.procurar_recomendam(),
            disciplinas=tupla_disciplinas,
        )

    return render_template(
        "index.html",
        placeholder="Digite o nome da disciplina",
        disciplinas=tupla_disciplinas,
    )


# Inicia a aplicação
# //////////////////////////////////////////////////////////
if __name__ == "__main__":
    tupla_disciplinas = listar_disciplinas()
    app.run(debug=True, host="0.0.0.0", port=80)
