import io
import base64
import random
import pickle
import matplotlib
import networkx as nx
import matplotlib.pyplot as plt
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
import heapq

# Use Agg backend for matplotlib
matplotlib.use('Agg')

NODE_NAMES = ["Seolleung", "Wangsimni", "Seoul Station", "Jamsil", "Gachon Univ", "Bokjeong", "Hongdae", "Gyodae", "Yangjae", "Gangnam"]

def create_random_graph():
    G = nx.Graph()
    nodes = NODE_NAMES
    edges = [(nodes[0], nodes[1], random.randint(1, 10)), (nodes[1], nodes[2], random.randint(1, 10)),
             (nodes[2], nodes[3], random.randint(1, 10)), (nodes[3], nodes[4], random.randint(1, 10)),
             (nodes[0], nodes[4], random.randint(1, 10)), (nodes[1], nodes[4], random.randint(1, 10)),
             (nodes[4], nodes[5], random.randint(1, 10)), (nodes[5], nodes[6], random.randint(1, 10)),
             (nodes[6], nodes[7], random.randint(1, 10)), (nodes[7], nodes[8], random.randint(1, 10)),
             (nodes[8], nodes[9], random.randint(1, 10)), (nodes[9], nodes[0], random.randint(1, 10)),
             (nodes[9], nodes[1], random.randint(1, 10))]
    G.add_nodes_from(nodes)
    G.add_weighted_edges_from(edges)
    return G

def plot_graph(G, path_edges=None):
    pos = {
        "Seolleung": (1, 3),
        "Wangsimni": (2, 2),
        "Seoul Station": (1, 1),
        "Jamsil": (2, 1),
        "Gachon Univ": (3, 2),
        "Bokjeong": (3, 3),
        "Hongdae": (1, 2),
        "Gyodae": (2, 3),
        "Yangjae": (3, 1),
        "Gangnam": (2.5, 2.5)
    }
    
    fig, ax = plt.subplots(figsize=(12, 8))
    nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=1000, font_size=12, edge_color='gray', ax=ax)
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, font_color='red', font_size=10, ax=ax)
    
    if path_edges:
        nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='red', width=2.5, ax=ax)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)
    img = base64.b64encode(buf.getvalue()).decode('utf-8')
    return img

def a_star_algorithm(graph, start, goal):
    queue = []
    heapq.heappush(queue, (0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}

    while queue:
        current = heapq.heappop(queue)[1]

        if current == goal:
            break

        for next in graph.neighbors(current):
            new_cost = cost_so_far[current] + graph[current][next].get('weight', 1)
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost
                heapq.heappush(queue, (priority, next))
                came_from[next] = current

    path = []
    if current == goal:
        while current:
            path.append(current)
            current = came_from[current]
        path.reverse()
    return path

def backtracking_algorithm(graph, start, goal):
    def backtrack(node, goal, path, visited):
        if node == goal:
            result.append(path.copy())
            return
        for next in set(graph.neighbors(node)) - visited:
            visited.add(next)
            path.append(next)
            backtrack(next, goal, path, visited)
            path.pop()
            visited.remove(next)

    result = []
    backtrack(start, goal, [start], set([start]))
    return result

@csrf_exempt
def index(request):
    if 'graph' not in request.session:
        G = create_random_graph()
        request.session['graph'] = pickle.dumps(G).decode('latin1')
    else:
        G = pickle.loads(request.session['graph'].encode('latin1'))
    
    path_edges = None
    astar_result = []
    backtracking_result = []
    
    if request.method == 'POST':
        target_node = request.POST.get('target_node')
        if target_node:
            try:
                _, path = nx.single_source_dijkstra(G, source="Gachon Univ", target=target_node)
                path_edges = list(zip(path, path[1:]))
                astar_result = a_star_algorithm(G, "Gachon Univ", target_node)
                backtracking_result = backtracking_algorithm(G, "Gachon Univ", target_node)
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                path_edges = None
                astar_result = []
                backtracking_result = []
    
    img = plot_graph(G, path_edges)
    dijkstra_path = nx.single_source_dijkstra_path(G, source="Gachon Univ")
    
    return render(request, 'index.html', {
        'img_data': img,
        'dijkstra_path': dijkstra_path,
        'astar_result': astar_result,
        'backtracking_result': backtracking_result,
    })

def new_graph(request):
    if 'graph' in request.session:
        del request.session['graph']
    return redirect('index')
