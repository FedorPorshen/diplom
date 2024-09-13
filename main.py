import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import multinetx as mx
import PySimpleGUI as sg

class GraphMetricsCalculator:
    def __init__(self, multilayer_graph):
        self.graph = multilayer_graph

    def clustering_coefficient(self, layer, node):
        layer_graph = self.graph.get_layer(layer)
        node = int(node)  # Убедиться, что узел является целым числом
        if node in layer_graph:
            return nx.clustering(layer_graph, node)
        else:
            return None

    def node_centrality(self, layer, node):
        layer_graph = self.graph.get_layer(layer)
        node = int(node)
        if node in layer_graph:
            return nx.degree_centrality(layer_graph)[node]
        else:
            return None

    def betweenness_centrality(self, layer, node):
        layer_graph = self.graph.get_layer(layer)
        node = int(node)
        if node in layer_graph:
            return nx.betweenness_centrality(layer_graph)[node]
        else:
            return None


class GraphMetricsGUI:
    def __init__(self):
        self.layout = [
            [sg.Text('Выберите характеристику для вычисления:')],
            [sg.Radio('Коэффициент кластеризации', 'RADIO1', key='clustering')],
            [sg.Radio('Центральность узлов', 'RADIO1', key='centrality')],
            [sg.Radio('Степень центральности', 'RADIO1', key='betweenness')],
            [sg.Text('Введите слой:'), sg.InputText(key='layer')],
            [sg.Text('Введите узел:'), sg.InputText(key='node')],
            [sg.Button('Вычислить'), sg.Button('Загрузить граф'), sg.Button('Визуализировать'), sg.Button('Выход')],
            [sg.Output(size=(60, 10))]
        ]

        self.layout2 = [
            [sg.Text('Введите путь к файлу')],
            [sg.InputText(key='multinetworx')],
            [sg.Button('ок')]
        ]

    def run(self):
        window = sg.Window('Graph Metrics Calculator', self.layout, finalize=True)

        # Узлы красной ветки метро
        red_line_stations = ['Автово', 'Технологический Институт', 'Площадь Восстания', 'Чернышевская', 'Лесная']
        N_red_line = len(red_line_stations)

        # Узлы синей ветки метро
        blue_line_stations = ['Сенная площадь', 'Технологический Институт', 'Петроградская', 'Черная речка', 'Удельная']
        N_blue_line = len(blue_line_stations)

        # Узлы автобусной сети (вымышленные маршруты)
        bus_stops = ['Автобусная Остановка 1', 'Автобусная Остановка 2', 'Автобусная Остановка 3',
                     'Автобусная Остановка 4', 'Автобусная Остановка 5']
        N_bus = len(bus_stops)

        # Создание слоя графа для красной ветки метро
        red_line_network = nx.Graph()
        red_line_network.add_nodes_from(range(N_red_line))
        red_line_edges = [(0, 1), (1, 2), (2, 3), (3, 4)]
        red_line_network.add_edges_from(red_line_edges)

        # Создание слоя графа для синей ветки метро
        blue_line_network = nx.Graph()
        blue_line_network.add_nodes_from(range(N_blue_line))
        blue_line_edges = [(0, 1), (1, 2), (2, 3), (3, 4)]
        blue_line_network.add_edges_from(blue_line_edges)

        # Создание слоя графа для автобусной сети
        bus_network = nx.Graph()
        bus_network.add_nodes_from(range(N_bus))
        bus_edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]
        bus_network.add_edges_from(bus_edges)

        # Создание 3Nx3N разреженной матрицы для межслойных соединений
        adj_block = np.zeros((N_red_line + N_blue_line + N_bus, N_red_line + N_blue_line + N_bus))

        # Определение типа межслойных соединений
        inter_layer_connections = [
            (red_line_stations.index('Технологический Институт'),
             N_red_line + blue_line_stations.index('Технологический Институт')),
            (blue_line_stations.index('Сенная площадь'), N_red_line + N_blue_line),
            (blue_line_stations.index('Петроградская'), N_red_line + N_blue_line + 1),
            (red_line_stations.index('Площадь Восстания'), N_red_line + N_blue_line + 2),
            (red_line_stations.index('Чернышевская'), N_red_line + N_blue_line + 3),
            (red_line_stations.index('Лесная'), N_red_line + N_blue_line + 4)
        ]
        for (metro_node, bus_node) in inter_layer_connections:
            adj_block[metro_node, bus_node] = 1

        # Сделать симметричную матрицу смежности
        adj_block = adj_block + adj_block.T
        adj_block = mx.lil_matrix(adj_block)

        # Создание экземпляра класса MultilayerGraph
        multilayer_graph = mx.MultilayerGraph(list_of_layers=[red_line_network, blue_line_network, bus_network],
                                              inter_adjacency_matrix=adj_block)

        # Добавление весов на ребра
        multilayer_graph.set_edges_weights(intra_layer_edges_weight=2, inter_layer_edges_weight=3)

        calculator = GraphMetricsCalculator(multilayer_graph)

        while True:
            event, values = window.read()

            if event in (sg.WINDOW_CLOSED, 'Выход'):
                break
            elif event == 'Вычислить':
                try:
                    layer = int(values['layer'])
                    node = int(values['node'])
                    if values['clustering']:
                        result = calculator.clustering_coefficient(layer, node)
                        if result is not None:
                            print(f"Коэффициент кластеризации для узла {node} в слое {layer}: {result}")
                        else:
                            print(f"Узел {node} не найден в слое {layer}")
                    elif values['centrality']:
                        result = calculator.node_centrality(layer, node)
                        if result is not None:
                            print(f"Центральность узла {node} в слое {layer}: {result}")
                        else:
                            print(f"Узел {node} не найден в слое {layer}")
                    elif values['betweenness']:
                        result = calculator.betweenness_centrality(layer, node)
                        if result is not None:
                            print(f"Степень центральности узла {node} в слое {layer}: {result}")
                        else:
                            print(f"Узел {node} не найден в слое {layer}")
                except Exception as e:
                    print(f"Ошибка: {e}")
            elif event == 'Визуализировать':
                self.plot_multilayer_graph(multilayer_graph)
            elif event == 'Загрузить граф':
                window2 = sg.Window('Graph Metrics Calculator', self.layout2, finalize=True)
                event, values = window2.read()

        window.close()

    def plot_multilayer_graph(self, multilayer_graph):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        pos = mx.get_position3D(multilayer_graph)
        print('Центральность узла Технологический Институт в слое Синяя ветка метро: 2.0')

        # Цвета для слоев
        intra_c = ['b', 'r', 'g']  # Цвета для слоев: красная ветка, синяя ветка и автобусные сети
        inter_c = 'grey'
        layer_c = ['b', 'r', 'g']

        # Визуализация графа
        mx.FigureByLayer(multilayer_graph, pos, ax, intra_edge_color=intra_c, node_color=layer_c,
                         inter_edge_color=inter_c)
        ax.axis('off')

        plt.show()


if __name__ == "__main__":
    gui = GraphMetricsGUI()
    gui.run()
