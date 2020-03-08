
class Graph(object):
    '''
    storage graph info by dict
    '''
    def __init__(self):
        self.__content = {}
        self.__input_degree={}

    def add_point(self, start, end=None):
        '''
        add a point to graph
        '''
        if start in self.__content:
            v = self.__content[start]
        else:
            v = set()
            self.__content[start]=v
        if end is not None and end != start:
            degree = self.__input_degree.get(end, 0)
            self.__input_degree[end] = degree + 1
            self.__input_degree.setdefault(start, 0)
            self.__content.setdefault(end,set())
            v.add(end)
    
    def empty_indegree(self):
        '''
        This method is used to get all point which in-degree is zero.\n
        CODE
        ```
        for node in graph.empty_indegree():
            pass
        ```
        '''
        return [k for (k, v) in self.__input_degree.items() if v == 0]
        


    
    def __getattr__(self,name):
        return getattr(self.__content, name)

    def __getitem__(self,index):
        return self.__content[index]

    def __str__(self):
        s = ['Graph:']
        for (k, v) in self.__content.items():
            s.append('{}  => {} \n'.format(k, v))
        return '\n'.join(s)

    def __iter__(self):
        return self.__content.__iter__()

    def remove(self, point):
        '''
        This method is used to delete a point and update in-degree.
        '''
        indegree = self.__input_degree[point]
        for node in self.__content[point]:
            self.__input_degree[node] -= 1
        del self.__content[point]
        del self.__input_degree[point]
        if indegree > 0:
            for (k, v) in self.__content.items():
                self.__content[k] = {x for x in v if x != point}
    
    def reverse(self):
        '''
        reverse this graph and return result,but it don't update itself
        '''
        graph = Graph()
        for (k, v) in self.__content.items():
            if len(v) == 0:
                graph.add_point(k)
                continue
            for value in v:
                graph.add_point(value, k)
        return graph

    def get_one_empty_indegree(self):
        '''
        Return a point which in-degree is zero. if there isn't,it will reurn `None`
        '''
        for (k,v) in self.__input_degree.items():
            if v == 0:
                return k
class StronglyConnectedGraph():
    '''
    storage strongly connected graph info by dict
    '''
    def __init__(self, graph):
        self.graph = graph
        self.scc_weights={}
        self.__content = {}
        self.__input_degree={}    
        self.compute()
    def compute(self):
        '''
        This method is used to get strongly connected graph by graph given by constructor,it wll be called in constructor
        '''
        self.scc_weights.clear()
        self.__content.clear()
        self.__input_degree.clear()  
        visite_seq=[]
        self.__loop_dfs(visite_seq)
        reverse = self.graph.reverse()
        visited = {}
        weights_map = {}
        visite_seq.reverse()
        for node in visite_seq:
            if visited.get(node):
                continue
            seq=[]
            self.__dfs(reverse,visited, node,seq)
            key=min(seq)
            self.scc_weights[key] = seq
            weights_map.update({x:key  for x in seq})
        for (key, value) in self.graph.items():
            if len(value) == 0:
                self.add_point(weights_map[key])
                continue
            for v in value:
                self.add_point(weights_map[key], weights_map[v])
        return self

    def remove(self, point):
        '''
        This method is used to delete a point and update in-degree.
        '''
        indegree = self.__input_degree[point]
        for node in self.__content.get(point,[]):
            self.__input_degree[node] -= 1
        del self.__content[point]
        del self.__input_degree[point]
        if indegree > 0:
            for (k, v) in self.__content.items():
                self.__content[k] = {x for x in v if x != point}
        del self.scc_weights[point]

    def __dfs(self, graph,visited, node,visite_seq):
        visited[node] = True
        ls= graph.get(node,[])
        for item in ls:
            if visited.get(item):
                continue
            self.__dfs(graph, visited, item, visite_seq)
        visite_seq.append(node)
            
    
    def __getattr__(self,name):
        return getattr(self.__content, name)

    def __getitem__(self,index):
        return self.__content[index]

    def __str__(self):
        s = ['Graph:']
        for (k, v) in self.__content.items():
            s.append('{}  => {} \n'.format(k, v))
        return '\n'.join(s)

    def __iter__(self):
        return self.__content.__iter__()

    def __loop_dfs(self, visite_seq):
        visited={}
        for key in self.graph:
            if not visited.get(key):
                self.__dfs(self.graph, visited, key, visite_seq)

    def add_point(self, start, end=None):
        '''
        add a point to graph
        '''
        if start in self.__content:
            v = self.__content[start]
        else:
            v = set()
            self.__content[start]=v
        if end is None or end == start:
            return
        if end in v:
            return
        degree = self.__input_degree.get(end, 0)
        self.__input_degree[end] = degree + 1
        self.__input_degree.setdefault(start, 0)
        self.__content.setdefault(end,set())
        v.add(end)
    
    def empty_indegree(self):
        '''
        This method is used to get all point which in-degree is zero.\n
        CODE
        ```
        for node in graph.empty_indegree():
            pass
        ```
        '''
        return [k for (k, v) in self.__input_degree.items() if v == 0]
    
    def get_one_empty_indegree(self):
        '''
        Return a point which in-degree is zero. if there isn't,it will reurn `None`
        '''
        for (k,v) in self.__input_degree.items():
            if v == 0:
                return k
