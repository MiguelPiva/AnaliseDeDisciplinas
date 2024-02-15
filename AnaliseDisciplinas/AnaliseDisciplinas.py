import pandas as pd, plotly.graph_objects as go, networkx as nx
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


# Cria grafo de dependências
# //////////////////////////////////////////////////////////
def criar_grafo():
    ''' Testando a criação de um grafo '''
    G = nx.random_geometric_graph(200, 0.125)

    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    node_x = []
    node_y = []
    for node in G.nodes():
        x, y = G.nodes[node]['pos']
        node_x.append(x)
        node_y.append(y)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            # colorscale options
            #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
            #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
            #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
            colorscale='YlGnBu',
            reversescale=True,
            color=[],
            size=10,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            ),
            line_width=2))
    
    node_adjacencies = []
    node_text = []
    for node, adjacencies in enumerate(G.adjacency()):
        node_adjacencies.append(len(adjacencies[1]))
        node_text.append('# of connections: '+str(len(adjacencies[1])))

    node_trace.marker.color = node_adjacencies
    node_trace.text = node_text

    fig = go.Figure(data=[edge_trace, node_trace],
             layout=go.Layout(
                title='<br>Network graph made with Python',
                titlefont_size=16,
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                paper_bgcolor = 'rgba(0,0,0,0)',
                plot_bgcolor = 'rgba(0,0,0,0)'
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
                               grafo = criar_grafo()
                               )
        
    return render_template("index.html", placeholder="Digite o nome da disciplina")


# Inicia o Flask
# //////////////////////////////////////////////////////////
if __name__ == "__main__":
    app.run(debug=True, host = "0.0.0.0", port=80) 