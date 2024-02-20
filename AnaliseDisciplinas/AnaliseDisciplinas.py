import pandas as pd, plotly.graph_objects as go, networkx as nx, math
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


# Procura disciplinas que recomendam fazer a disciplina passada como parâmetro
# //////////////////////////////////////////////////////////
def procurar_dependencias(nome):
    dependencias = []
    num_linhas = len(df) - 1

    for num in range(0, num_linhas):
        if nome in df.loc[num, "RECOMENDAÇÃO"]:
            dependencias.append(df.loc[num, "DISCIPLINA"])

    return dependencias


# Cria grafo de dependências
# //////////////////////////////////////////////////////////
def criar_grafo(nome):
    G = nx.DiGraph()
    dependem_de_nome = procurar_dependencias(nome)
    posicao = 0
    ajuste = 1

    G.add_node(nome)
    G.nodes[nome]["pos"] = (0,0)
    for disciplina in dependem_de_nome:
        G.add_node(disciplina)
        G.nodes[disciplina]["pos"] = (ajuste*math.cos(posicao+ajuste), ajuste*math.sin(posicao+ajuste))
        G.add_edge(disciplina, nome)

        ajuste = ajuste + 1.3 if posicao > 5.7 else ajuste
        posicao = posicao + 0.3 if posicao < 5.7 else 0

    node_trace = go.Scatter(
        x=[G.nodes[node]["pos"][0] for node in G.nodes()],
        y=[G.nodes[node]["pos"][1] for node in G.nodes()],
        mode="markers",
        marker=dict(size=20, colorscale="Blues"),
        text=[node for node in G.nodes()],
    )

    node_adjacencies = []
    node_text = []
    for node, adjacencies in enumerate(G.adjacency()):
        node_adjacencies.append(len(adjacencies[1]))

    node_trace.marker.color = node_adjacencies

    arestas_x = []
    arestas_y = []
    for aresta in G.edges():
        x0, y0 = G.nodes[aresta[0]]['pos']
        x1, y1 = G.nodes[aresta[1]]['pos']
        arestas_x.append(x0)
        arestas_x.append(x1)
        arestas_x.append(None)
        arestas_y.append(y0)
        arestas_y.append(y1)
        arestas_y.append(None)

    edge_trace = go.Scatter(
        x = arestas_x,
        y = arestas_y,
        mode="lines"
    )  

    fig = go.Figure(data=[edge_trace, node_trace], 
                    layout=go.Layout(
                        paper_bgcolor = 'rgba(0,0,0,0)',
                        plot_bgcolor = 'rgba(0,0,0,0)',
                        margin=dict(b=5,l=5,r=5,t=5),
                        showlegend=False,
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                    ))
    
    return fig.to_html()


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

        return render_template("index.html", 
                               placeholder=disciplina.nome, 
                               tpei=disciplina.tpei, 
                               codigo=disciplina.sigla, 
                               concluida=disciplina.concluida, 
                               recomendacao=disciplina.recomendacao, 
                               ementa=disciplina.ementa_formatada(), 
                               objetivos=disciplina.objetivos,
                               grafo = criar_grafo(disciplina.nome)
                               )
        
    return render_template("index.html", placeholder="Digite o nome da disciplina")


# Inicia o Flask
# //////////////////////////////////////////////////////////
if __name__ == "__main__":
    app.run(debug=True, host = "0.0.0.0", port=80) 