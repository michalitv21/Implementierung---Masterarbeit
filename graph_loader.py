"""
Graph Loader for adjacency list files (.lst format)

Supports various adjacency list formats:
1. Vertex: neighbor1 neighbor2 ...
2. Vertex neighbor1 neighbor2 ...
"""

from graph import Graph, Vertex


def load_graph_from_adjacency_list(file_path):
    """
    Load a graph from an adjacency list file (.lst)
    
    File format:
    - Each line represents a vertex and its neighbors
    - Format: vertex_label: neighbor1 neighbor2 neighbor3 ...
    - Or: vertex_label neighbor1 neighbor2 neighbor3 ...
    - Lines starting with # are comments
    - Empty lines are ignored
    
    Args:
        file_path (str): Path to the .lst file
        
    Returns:
        Graph: Graph object with vertices and edges
        
    Example:
        a: b d e
        b: a c f
        c: b
        ...
    """
    vertices_dict = {}  # label -> Vertex object
    edges = []  # list of sets {v1, v2}
    adjacency_map = {}  # label -> [neighbors]
    
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Parse the line
                parts = line.split()
                if len(parts) < 1:
                    continue
                
                # Remove colon if present (e.g., "a:" becomes "a")
                vertex_label = parts[0].rstrip(':')
                neighbors = parts[1:]
                
                # Create vertex if it doesn't exist
                if vertex_label not in vertices_dict:
                    vertices_dict[vertex_label] = Vertex(vertex_label)
                
                # Store adjacency information
                adjacency_map[vertex_label] = neighbors
                
                # Create vertices for neighbors
                for neighbor in neighbors:
                    if neighbor not in vertices_dict:
                        vertices_dict[neighbor] = Vertex(neighbor)
        
        # Create edges from adjacency list (avoid duplicates)
        processed_edges = set()
        for vertex_label, neighbors in adjacency_map.items():
            for neighbor in neighbors:
                # Create a canonical edge representation (sorted tuple)
                edge_key = tuple(sorted([vertex_label, neighbor]))
                
                # Add edge only if we haven't seen it before
                if edge_key not in processed_edges:
                    edge = {vertices_dict[vertex_label], vertices_dict[neighbor]}
                    edges.append(edge)
                    processed_edges.add(edge_key)
        
        # Create and return Graph object
        vertices_list = list(vertices_dict.values())
        graph = Graph(vertices_list, edges)
        
        return graph
        
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None
    except Exception as e:
        print(f"Error loading graph from file: {e}")
        return None


def load_graph_from_edge_list(file_path):
    """
    Load a graph from an edge list file
    
    File format:
    - Each line represents an edge
    - Format: vertex1 vertex2
    - Lines starting with # are comments
    - Empty lines are ignored
    
    Args:
        file_path (str): Path to the edge list file
        
    Returns:
        Graph: Graph object with vertices and edges
        
    Example:
        a b
        a c
        b c
        ...
    """
    vertices_dict = {}  # label -> Vertex object
    edges = []  # list of sets {v1, v2}
    processed_edges = set()  # to avoid duplicates
    
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Parse the line
                parts = line.split()
                if len(parts) < 2:
                    continue
                
                v1_label = parts[0]
                v2_label = parts[1]
                
                # Create vertices if they don't exist
                if v1_label not in vertices_dict:
                    vertices_dict[v1_label] = Vertex(v1_label)
                if v2_label not in vertices_dict:
                    vertices_dict[v2_label] = Vertex(v2_label)
                
                # Create edge (avoid duplicates)
                edge_key = tuple(sorted([v1_label, v2_label]))
                if edge_key not in processed_edges:
                    edge = {vertices_dict[v1_label], vertices_dict[v2_label]}
                    edges.append(edge)
                    processed_edges.add(edge_key)
        
        # Create and return Graph object
        vertices_list = list(vertices_dict.values())
        graph = Graph(vertices_list, edges)
        
        return graph
        
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None
    except Exception as e:
        print(f"Error loading graph from file: {e}")
        return None


def save_graph_as_adjacency_list(graph, file_path):
    """
    Save a graph as an adjacency list file
    
    Args:
        graph (Graph): Graph object to save
        file_path (str): Path where to save the file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Build adjacency map
        adjacency_map = {}
        for vertex in graph.vertices:
            adjacency_map[vertex.label] = []
        
        for edge in graph.edges:
            vertices_list = list(edge)
            v1, v2 = vertices_list[0], vertices_list[1]
            adjacency_map[v1.label].append(v2.label)
            adjacency_map[v2.label].append(v1.label)
        
        # Sort neighbors for consistency
        for label in adjacency_map:
            adjacency_map[label].sort()
        
        # Write to file
        with open(file_path, 'w') as f:
            f.write("# Adjacency List Format\n")
            f.write("# vertex: neighbor1 neighbor2 ...\n\n")
            
            for label in sorted(adjacency_map.keys()):
                neighbors = " ".join(adjacency_map[label])
                f.write(f"{label}: {neighbors}\n")
        
        print(f"Graph saved to {file_path}")
        return True
        
    except Exception as e:
        print(f"Error saving graph: {e}")
        return False


if __name__ == "__main__":
    # Example usage
    
    # Example 1: Load from adjacency list
    print("Example 1: Loading from adjacency list file")
    graph = load_graph_from_adjacency_list("graph_160.lst")
    if graph:
        print(f"Loaded graph with {len(graph.vertices)} vertices and {len(graph.edges)} edges")
        print(f"Vertices: {[v.label for v in graph.vertices]}")
    