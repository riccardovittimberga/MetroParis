from database.DAO import DAO
import networkx as nx
import geopy.distance

class Model:
    def __init__(self):
        self._fermate = DAO.getAllFermate()
        self._grafo=nx.DiGraph()
        self._idMap={} #creo una mappa per avere un id associato a un oggetto ed è utile nel metodo 2 per confrontare una stazione e un oggetto, così la stazione tramite l'id viene associata ad un oggetto e confronto i due oggetti
        for f in self._fermate:
            self._idMap[f.id_fermata]=f
        self._linee=DAO.getAllLinee()
        self._lineaMap={}
        for l in self._linee:
            self._lineaMap[l.id_linea]=l
    def getBFSNodes(self,source):
        edges=nx.bfs_edges(self._grafo,source)
        visited=[]
        for u,v in edges:
            visited.append(v)
        return visited

    def getDFSNodes(self, source):
        edges=nx.dfs_edges(self._grafo,source)
        visited = []
        for u, v in edges:
            visited.append(v)
        return visited

    def buildGraph(self):
        self._grafo.add_nodes_from(self._fermate)

        #modo 1 ma si perde tanto tempo
        """for u in self._fermate:
            for v in self._fermate:
                res= DAO.getEdge(u,v)
                if len(res)>0:
                    self._grafo.add_edge(u,v)
                    print(f"Added edge between {u} and {v} to graph")"""

        #Modo 2 prendo i nodi vicini con una query e loop singolo sui nodi
        for u in self._fermate:
            vicini =DAO.getEdgesVicini(u)
            for v in vicini:
                v_nodo=self._idMap[v.id_stazA]
                self._grafo.add_edge(u,v_nodo)
                #print(f"Added edge between {u} and {v_nodo} to graph")
        #Modo 3 unica query che legge tutte le connessioni
        """allConnessioni =DAO.getAllConnessioni()
        for c in allConnessioni:
            u_nodo=self._idMap[c.id_stazP]
            v_nodo=self._idMap[c.id_stazA]
            self._grafo.add_edge(u_nodo,v_nodo)"""

    def buildGraphPesato(self):
        self._grafo.clear()
        self._grafo.add_nodes_from(self._fermate)
        self.addEdgePesati()

    def addEdgePesati(self):
        self._grafo.clear_edges()
        allConnessioni = DAO.getAllConnessioni()
        for c in allConnessioni:
            v0 = self._idMap[c.id_stazP]
            v1 = self._idMap[c.id_stazA]
            linea = self._lineaMap[c.id_linea]
            peso = self.getTraversalTime(v0, v1, linea)

            if self._grafo.has_edge(v0, v1):
                if self._grafo[v0][v1]["weight"] > peso:
                    self._grafo[v0][v1]["weight"] = peso
            else:
                self._grafo.add_edge(v0, v1, weight=peso)


    def getTraversalTime(self,v0,v1,linea):
        vel=linea.velocita
        p0=(v0.coordX,v0.coordY)
        p1=(v1.coordX,v1.coordY)
        distanza=geopy.distance.distance(p0,p1).km
        tempo=distanza/vel*60
        return tempo
    @property
    def fermate(self):
        return self._fermate

    def getNumNodes(self):
        return len(self._grafo.nodes)

    def getNumEdges(self):
        return len(self._grafo.edges)

    def getEdgeWeight(self,v1,v2):
        return self._grafo[v1][v2]["weight"]

    def getArchiPesoMaggiore(self):
        if len(self._grafo.edges)==0:
            print("Il grafo è vuoto")
            return
        else:

            edges=self._grafo.edges
            result=[]
            for u, v in edges:
                peso=self._grafo[u][v]["weight"]
                if peso>1:
                    result.append((u,v,peso))
            return result

    def getBestPath(self,v0,v1):
        costoTot,path=nx.single_source_dijkstra(self._grafo,v0,v1)
        return costoTot,path