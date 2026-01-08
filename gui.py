import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import math
import json
import os
from graphLib import Graph, Vertex, minimal_degree_ordering, permutationToTreeDecomposition
from treeDecomp import TreeDecomposition, RootedTree, Node
from graph_loader import load_graph_from_adjacency_list, load_graph_from_edge_list

class GraphGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Tree Decomposition Visualizer")
        self.root.geometry("1400x800")
        
        # Set appearance mode and color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # File persistence
        self.graphs_file = os.path.join(os.path.dirname(__file__), "saved_graphs.json")
        
        # Data structures
        self.vertices = {}  # label -> Vertex
        self.edges = []  # list of sets {v1, v2}
        self.graph = None
        self.tree_decomposition = None
        self.rooted_tree = None  # RootedTree representation
        self.root_bag = None  # Selected root bag for rooted tree
        self.saved_graphs = {}  # name -> (vertices, edges)
        
        # Canvas positions for dragging
        self.vertex_positions = {}  # label -> (x, y)
        self.bag_positions = {}  # bag_label -> (x, y)
        self.node_positions = {}  # node_label -> (x, y) for rooted tree
        self.dragging = None
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        # Load graphs from file
        self.load_graphs_from_file()
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=0)  # Left: fixed width
        main_frame.columnconfigure(1, weight=1)  # Middle-left: expandable
        main_frame.columnconfigure(2, weight=1)  # Middle-right: expandable
        main_frame.columnconfigure(3, weight=0)  # Right: fixed width
        main_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Left panel - Controls
        control_frame = ctk.CTkFrame(main_frame, corner_radius=15)
        control_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 15))
        
        # Title
        title_label = ctk.CTkLabel(control_frame, text="Graph Editor", font=ctk.CTkFont(size=18, weight="bold"))
        title_label.grid(row=0, column=0, columnspan=4, sticky="w", padx=20, pady=(20, 15))
        
        # Vertex input section
        vertex_section = ctk.CTkFrame(control_frame, fg_color="transparent")
        vertex_section.grid(row=1, column=0, columnspan=4, sticky="ew", padx=20, pady=(0, 10))
        
        ctk.CTkLabel(vertex_section, text="Vertex:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, sticky="w", pady=5)
        self.vertex_entry = ctk.CTkEntry(vertex_section, width=120, placeholder_text="Label")
        self.vertex_entry.grid(row=0, column=1, pady=5, padx=5)
        ctk.CTkButton(vertex_section, text="Add", command=self.add_vertex, width=70, fg_color="#1f6aa5", hover_color="#144870").grid(row=0, column=2, padx=2, pady=5)
        ctk.CTkButton(vertex_section, text="Delete", command=self.delete_vertex, width=70, fg_color="#d32f2f", hover_color="#9a0007").grid(row=0, column=3, padx=2, pady=5)
        
        # Edge input section
        edge_section = ctk.CTkFrame(control_frame, fg_color="transparent")
        edge_section.grid(row=3, column=0, columnspan=4, sticky="ew", padx=20, pady=(0, 10))
        
        ctk.CTkLabel(edge_section, text="Edge:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=0, column=0, sticky="w", pady=5)
        edge_inputs = ctk.CTkFrame(edge_section, fg_color="transparent")
        edge_inputs.grid(row=0, column=1, pady=5, padx=5, sticky="w")
        self.edge_v1_entry = ctk.CTkEntry(edge_inputs, width=50, placeholder_text="v1")
        self.edge_v1_entry.pack(side="left", padx=(0, 5))
        ctk.CTkLabel(edge_inputs, text="-", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")
        self.edge_v2_entry = ctk.CTkEntry(edge_inputs, width=50, placeholder_text="v2")
        self.edge_v2_entry.pack(side="left", padx=(5, 0))
        ctk.CTkButton(edge_section, text="Add", command=self.add_edge, width=70, fg_color="#1f6aa5", hover_color="#144870").grid(row=0, column=2, padx=2, pady=5)
        ctk.CTkButton(edge_section, text="Delete", command=self.delete_edge, width=70, fg_color="#d32f2f", hover_color="#9a0007").grid(row=0, column=3, padx=2, pady=5)
        
        # List of vertices and edges
        ctk.CTkLabel(control_frame, text="Vertices:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=5, column=0, columnspan=4, sticky="w", padx=20, pady=(15, 5))
        self.vertex_list = ctk.CTkTextbox(control_frame, width=300, height=80, font=ctk.CTkFont(family="Consolas", size=10))
        self.vertex_list.grid(row=6, column=0, columnspan=4, padx=20, pady=(0, 10))
        
        ctk.CTkLabel(control_frame, text="Edges:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=7, column=0, columnspan=4, sticky="w", padx=20, pady=(5, 5))
        self.edge_list = ctk.CTkTextbox(control_frame, width=300, height=80, font=ctk.CTkFont(family="Consolas", size=10))
        self.edge_list.grid(row=8, column=0, columnspan=4, padx=20, pady=(0, 15))
        
        # Action buttons
        button_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        button_frame.grid(row=10, column=0, columnspan=4, padx=20, pady=15)
        ctk.CTkButton(button_frame, text="Clear All", command=self.clear_all, width=80, fg_color="#d32f2f", hover_color="#9a0007").pack(side="left", padx=3)
        ctk.CTkButton(button_frame, text="Compute", command=self.compute_tree_decomposition, width=80, fg_color="#2e7d32", hover_color="#1b5e20").pack(side="left", padx=3)
        
        # Ordering options
        ctk.CTkLabel(control_frame, text="Vertex Ordering:", font=ctk.CTkFont(size=12, weight="bold")).grid(row=12, column=0, columnspan=4, sticky="w", padx=20, pady=(15, 5))
        self.ordering_var = tk.StringVar(value="minimal_degree")
        
        radio_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        radio_frame.grid(row=13, column=0, columnspan=4, sticky="w", padx=20)
        ctk.CTkRadioButton(radio_frame, text="Minimal Degree", variable=self.ordering_var, value="minimal_degree").pack(anchor="w", pady=3)
        ctk.CTkRadioButton(radio_frame, text="Custom Order", variable=self.ordering_var, value="custom").pack(anchor="w", pady=3)
        
        ctk.CTkLabel(control_frame, text="Custom order (comma-separated):", font=ctk.CTkFont(size=10)).grid(row=14, column=0, columnspan=4, sticky="w", padx=20, pady=(10, 2))
        self.custom_order_entry = ctk.CTkEntry(control_frame, width=300, placeholder_text="v1, v2, v3, ...")
        self.custom_order_entry.grid(row=15, column=0, columnspan=4, padx=20, pady=(0, 20))
        
        # Right panel - Visualizations (column 1-2 for tree decomposition and rooted tree)
        viz_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        viz_frame.grid(row=0, column=1, columnspan=2, rowspan=2, sticky="nsew", padx=(0, 15))
        viz_frame.columnconfigure(0, weight=1)
        viz_frame.columnconfigure(1, weight=1)
        viz_frame.rowconfigure(0, weight=1)
        viz_frame.rowconfigure(1, weight=1)
        
        # Original graph canvas
        graph_frame = ctk.CTkFrame(viz_frame, corner_radius=15)
        graph_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        graph_frame.columnconfigure(0, weight=1)
        graph_frame.rowconfigure(1, weight=1)
        
        ctk.CTkLabel(graph_frame, text="Original Graph", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, sticky="w", padx=15, pady=(15, 10))
        
        self.graph_canvas = ctk.CTkCanvas(graph_frame, bg="#1a1a1a", width=800, height=350, highlightthickness=0)
        self.graph_canvas.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        self.graph_canvas.bind("<Button-1>", self.on_graph_click)
        self.graph_canvas.bind("<B1-Motion>", self.on_graph_drag)
        self.graph_canvas.bind("<ButtonRelease-1>", self.on_graph_release)
        
        # Tree decomposition canvas
        tree_frame = ctk.CTkFrame(viz_frame, corner_radius=15)
        tree_frame.grid(row=1, column=0, sticky="nsew")
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(1, weight=1)
        
        tree_header_frame = ctk.CTkFrame(tree_frame, fg_color="transparent")
        tree_header_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 5))
        ctk.CTkLabel(tree_header_frame, text="Tree Decomposition", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
        
        # Root selection
        ctk.CTkLabel(tree_header_frame, text="Root:", font=ctk.CTkFont(size=11)).pack(side="left", padx=(20, 5))
        self.root_var = tk.StringVar(value="")
        self.root_combo = ctk.CTkComboBox(tree_header_frame, variable=self.root_var, width=100, 
                                          values=[], command=self.on_root_changed, font=ctk.CTkFont(size=10))
        self.root_combo.pack(side="left", padx=5)
        ctk.CTkButton(tree_header_frame, text="Rooted", command=self.convert_to_rooted_tree, 
                     width=70, fg_color="#1565c0", hover_color="#0d47a1").pack(side="left", padx=5)
        
        self.tree_canvas = ctk.CTkCanvas(tree_frame, bg="#1a1a1a", width=400, height=350, highlightthickness=0)
        self.tree_canvas.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        self.tree_canvas.bind("<Button-1>", self.on_tree_click)
        self.tree_canvas.bind("<B1-Motion>", self.on_tree_drag)
        self.tree_canvas.bind("<ButtonRelease-1>", self.on_tree_release)
        
        # Rooted tree canvas
        rooted_frame = ctk.CTkFrame(viz_frame, corner_radius=15)
        rooted_frame.grid(row=1, column=1, sticky="nsew", padx=(10, 0))
        rooted_frame.columnconfigure(0, weight=1)
        rooted_frame.rowconfigure(1, weight=1)
        
        ctk.CTkLabel(rooted_frame, text="Rooted Tree", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, sticky="w", padx=15, pady=(15, 10))
        
        self.rooted_canvas = ctk.CTkCanvas(rooted_frame, bg="#1a1a1a", width=400, height=350, highlightthickness=0)
        self.rooted_canvas.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        
        # Right panel - Save/Load
        save_load_frame = ctk.CTkFrame(main_frame, corner_radius=15)
        save_load_frame.grid(row=0, column=3, rowspan=2, sticky="nsew", padx=(15, 0))
        save_load_frame.columnconfigure(0, weight=1)
        
        ctk.CTkLabel(save_load_frame, text="Save / Load", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 15))
        
        # File loading section
        ctk.CTkLabel(save_load_frame, text="Load from File", font=ctk.CTkFont(size=12, weight="bold")).grid(row=1, column=0, sticky="w", padx=20, pady=(10, 5))
        self.file_path_entry = ctk.CTkEntry(save_load_frame, width=220, placeholder_text=".lst or .txt file")
        self.file_path_entry.grid(row=2, column=0, padx=20, pady=5)
        
        file_button_frame = ctk.CTkFrame(save_load_frame, fg_color="transparent")
        file_button_frame.grid(row=3, column=0, padx=20, pady=10)
        ctk.CTkButton(file_button_frame, text="Browse", command=self.browse_file, width=95, fg_color="#9c27b0", hover_color="#6a1b9a").pack(side="left", padx=3)
        ctk.CTkButton(file_button_frame, text="Load", command=self.load_from_file, width=95, fg_color="#2e7d32", hover_color="#1b5e20").pack(side="left", padx=3)
        
        # Save section
        ctk.CTkLabel(save_load_frame, text="Save Graph", font=ctk.CTkFont(size=12, weight="bold")).grid(row=4, column=0, sticky="w", padx=20, pady=(15, 5))
        self.save_name_entry = ctk.CTkEntry(save_load_frame, width=220, placeholder_text="Graph name")
        self.save_name_entry.grid(row=5, column=0, padx=20, pady=5)
        ctk.CTkButton(save_load_frame, text="Save Graph", command=self.save_graph, width=200, fg_color="#1f6aa5", hover_color="#144870").grid(row=6, column=0, padx=20, pady=10)
        
        # Saved graphs list
        ctk.CTkLabel(save_load_frame, text="Saved Graphs", font=ctk.CTkFont(size=12, weight="bold")).grid(row=7, column=0, sticky="w", padx=20, pady=(15, 5))
        self.saved_graphs_list = ctk.CTkTextbox(save_load_frame, width=220, height=120, font=ctk.CTkFont(family="Consolas", size=9))
        self.saved_graphs_list.grid(row=8, column=0, padx=20, pady=5)
        
        # Load section
        ctk.CTkLabel(save_load_frame, text="Load Saved Graph", font=ctk.CTkFont(size=12, weight="bold")).grid(row=9, column=0, sticky="w", padx=20, pady=(15, 5))
        self.load_name_entry = ctk.CTkEntry(save_load_frame, width=220, placeholder_text="Graph name to load")
        self.load_name_entry.grid(row=10, column=0, padx=20, pady=5)
        
        button_frame = ctk.CTkFrame(save_load_frame, fg_color="transparent")
        button_frame.grid(row=11, column=0, padx=20, pady=10)
        ctk.CTkButton(button_frame, text="Load", command=self.load_graph, width=70, fg_color="#2e7d32", hover_color="#1b5e20").pack(side="left", padx=3)
        ctk.CTkButton(button_frame, text="Delete", command=self.delete_graph, width=70, fg_color="#d32f2f", hover_color="#9a0007").pack(side="left", padx=3)
        ctk.CTkButton(button_frame, text="Refresh", command=self.refresh_saved_graphs, width=70, fg_color="#f57c00", hover_color="#e65100").pack(side="left", padx=3)
        
        # Initialize saved graphs display
        self.refresh_saved_graphs()
        
    def add_vertex(self):
        label = self.vertex_entry.get().strip()
        if not label:
            messagebox.showwarning("Input Error", "Please enter a vertex label")
            return
        if label in self.vertices:
            messagebox.showwarning("Duplicate", f"Vertex '{label}' already exists")
            return
        
        self.vertices[label] = Vertex(label)
        self.vertex_entry.delete(0, tk.END)
        self.update_lists()
        self.draw_graph()
        
    def add_edge(self):
        v1_label = self.edge_v1_entry.get().strip()
        v2_label = self.edge_v2_entry.get().strip()
        
        if not v1_label or not v2_label:
            messagebox.showwarning("Input Error", "Please enter both vertex labels")
            return
        if v1_label not in self.vertices or v2_label not in self.vertices:
            messagebox.showwarning("Invalid Vertices", "Both vertices must exist")
            return
        if v1_label == v2_label:
            messagebox.showwarning("Invalid Edge", "Self-loops are not allowed")
            return
        
        edge = {self.vertices[v1_label], self.vertices[v2_label]}
        if edge in self.edges:
            messagebox.showwarning("Duplicate", "This edge already exists")
            return
        
        self.edges.append(edge)
        self.edge_v1_entry.delete(0, tk.END)
        self.edge_v2_entry.delete(0, tk.END)
        self.update_lists()
        self.draw_graph()
    
    def delete_vertex(self):
        label = self.vertex_entry.get().strip()
        if not label:
            messagebox.showwarning("Input Error", "Please enter a vertex label")
            return
        if label not in self.vertices:
            messagebox.showwarning("Not Found", f"Vertex '{label}' does not exist")
            return
        
        # Remove the vertex
        vertex = self.vertices[label]
        del self.vertices[label]
        
        # Remove all edges containing this vertex
        self.edges = [e for e in self.edges if vertex not in e]
        
        # Remove position data
        if label in self.vertex_positions:
            del self.vertex_positions[label]
        
        self.vertex_entry.delete(0, tk.END)
        self.update_lists()
        self.draw_graph()
    
    def delete_edge(self):
        v1_label = self.edge_v1_entry.get().strip()
        v2_label = self.edge_v2_entry.get().strip()
        
        if not v1_label or not v2_label:
            messagebox.showwarning("Input Error", "Please enter both vertex labels")
            return
        if v1_label not in self.vertices or v2_label not in self.vertices:
            messagebox.showwarning("Invalid Vertices", "Both vertices must exist")
            return
        
        edge = {self.vertices[v1_label], self.vertices[v2_label]}
        if edge not in self.edges:
            messagebox.showwarning("Not Found", "This edge does not exist")
            return
        
        self.edges.remove(edge)
        self.edge_v1_entry.delete(0, tk.END)
        self.edge_v2_entry.delete(0, tk.END)
        self.update_lists()
        self.draw_graph()
        
    def clear_all(self):
        self.vertices.clear()
        self.edges.clear()
        self.vertex_positions.clear()
        self.bag_positions.clear()
        self.node_positions.clear()
        self.tree_decomposition = None
        self.rooted_tree = None
        self.update_lists()
        self.draw_graph()
        self.tree_canvas.delete("all")
        
    def update_lists(self):
        self.vertex_list.delete("1.0", "end")
        self.vertex_list.insert("1.0", ", ".join(sorted(self.vertices.keys())))
        
        self.edge_list.delete("1.0", "end")
        edge_strs = [f"({sorted([str(v) for v in e])[0]}, {sorted([str(v) for v in e])[1]})" 
                    for e in self.edges]
        self.edge_list.insert("1.0", "\n".join(edge_strs))
        
    def draw_graph(self):
        self.graph_canvas.delete("all")
        if not self.vertices:
            return
        
        # Initialize positions for any new vertices
        n = len(self.vertices)
        radius = min(self.graph_canvas.winfo_width(), self.graph_canvas.winfo_height()) / 3
        if radius == 0:
            radius = 150
        center_x = self.graph_canvas.winfo_width() / 2
        center_y = self.graph_canvas.winfo_height() / 2
        if center_x == 0:
            center_x = 400
        if center_y == 0:
            center_y = 175
        
        for i, label in enumerate(sorted(self.vertices.keys())):
            if label not in self.vertex_positions:
                angle = 2 * math.pi * i / n
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                self.vertex_positions[label] = (x, y)
        
        # Draw edges with modern style
        for edge in self.edges:
            vertices_list = list(edge)
            v1_label = str(vertices_list[0])
            v2_label = str(vertices_list[1])
            x1, y1 = self.vertex_positions[v1_label]
            x2, y2 = self.vertex_positions[v2_label]
            self.graph_canvas.create_line(x1, y1, x2, y2, fill="#616161", width=3, smooth=True)
        
        # Draw vertices with modern style and gradient effect
        for label, (x, y) in self.vertex_positions.items():
            r = 25
            # Outer shadow
            self.graph_canvas.create_oval(x-r-2, y-r-2, x+r+2, y+r+2, fill="#0d47a1", outline="", tags=f"vertex_{label}")
            # Main circle
            self.graph_canvas.create_oval(x-r, y-r, x+r, y+r, fill="#1976d2", 
                                          outline="#42a5f5", width=2, tags=f"vertex_{label}")
            # Text
            self.graph_canvas.create_text(x, y, text=label, font=("Segoe UI", 12, "bold"), 
                                         fill="white", tags=f"vertex_{label}")
            
    def on_graph_click(self, event):
        item = self.graph_canvas.find_closest(event.x, event.y)[0]
        tags = self.graph_canvas.gettags(item)
        for tag in tags:
            if tag.startswith("vertex_"):
                self.dragging = tag.replace("vertex_", "")
                self.drag_start_x = event.x
                self.drag_start_y = event.y
                break
                
    def on_graph_drag(self, event):
        if self.dragging and self.dragging in self.vertex_positions:
            dx = event.x - self.drag_start_x
            dy = event.y - self.drag_start_y
            x, y = self.vertex_positions[self.dragging]
            self.vertex_positions[self.dragging] = (x + dx, y + dy)
            self.drag_start_x = event.x
            self.drag_start_y = event.y
            self.draw_graph()
            
    def on_graph_release(self, event):
        self.dragging = None
        
    def compute_tree_decomposition(self):
        if not self.vertices:
            messagebox.showwarning("No Graph", "Please add vertices first")
            return
        
        # Clear previous tree decomposition artifacts
        self.bag_positions.clear()
        self.tree_decomposition = None
        self.tree_canvas.delete("all")
        
        # Create NEW vertex objects (not references) for the computation
        vertex_map = {label: Vertex(label) for label in self.vertices.keys()}
        vertex_list = list(vertex_map.values())
        
        # Create edges with the new vertex objects
        edge_list = []
        for edge in self.edges:
            edge_vertices = list(edge)
            v1_label = str(edge_vertices[0])
            v2_label = str(edge_vertices[1])
            new_edge = {vertex_map[v1_label], vertex_map[v2_label]}
            edge_list.append(new_edge)
        
        graph_copy = Graph(vertex_list, edge_list)
        
        # Get vertex ordering
        if self.ordering_var.get() == "minimal_degree":
            ordering = minimal_degree_ordering(graph_copy)
            # Ensure ordering includes ALL vertices (append any missing ones)
            if len(ordering) != len(vertex_list):
                have = {v for v in ordering}
                missing = [v for v in vertex_list if v not in have]
                if missing:
                    # Append missing vertices in a stable label order
                    for mv in sorted(missing, key=lambda x: x.label):
                        ordering.append(mv)
            print(str([v.label for v in ordering]))
        else:
            custom_str = self.custom_order_entry.get().strip()
            if not custom_str:
                messagebox.showwarning("Input Error", "Please enter a custom ordering")
                return
            labels = [l.strip() for l in custom_str.split(",")]
            if set(labels) != set(self.vertices.keys()):
                messagebox.showwarning("Invalid Ordering", "Ordering must include all vertices exactly once")
                return
            ordering = [vertex_map[l] for l in labels]
        
        # Create a second fresh graph copy for decomposition
        vertex_map2 = {label: Vertex(label) for label in self.vertices.keys()}
        vertex_list2 = list(vertex_map2.values())
        edge_list2 = []
        for edge in self.edges:
            edge_vertices = list(edge)
            v1_label = str(edge_vertices[0])
            v2_label = str(edge_vertices[1])
            new_edge = {vertex_map2[v1_label], vertex_map2[v2_label]}
            edge_list2.append(new_edge)
        
        # Convert ordering to use vertices from vertex_map2
        ordering2 = [vertex_map2[v.label] for v in ordering]
        
        graph_copy2 = Graph(vertex_list2, edge_list2)
        self.tree = permutationToTreeDecomposition(graph_copy2, ordering2)
        print("Tree Decomposition computed.")
        print(self.tree)
        self.tree_decomposition = TreeDecomposition(self.tree.I, self.tree)
        
        # Update root selection combobox with bag labels
        bag_labels = [bag.label for bag in self.tree_decomposition.tree.I.values()]
        self.root_combo.configure(values=bag_labels)
        if bag_labels:
            self.root_var.set(bag_labels[0])
            # Find the actual bag object by label
            for vertex, bag in self.tree_decomposition.tree.I.items():
                if bag.label == bag_labels[0]:
                    self.root_bag = bag
                    break
        
        self.draw_tree_decomposition()
    
    def on_root_changed(self, choice):
        """Called when root selection combobox changes"""
        if self.tree_decomposition and choice:
            # Find the actual bag object by label
            for vertex, bag in self.tree_decomposition.tree.I.items():
                if bag.label == choice:
                    self.root_bag = bag
                    break
            self.draw_tree_decomposition()
    
    def draw_tree_decomposition(self):
        self.tree_canvas.delete("all")
        if not self.tree_decomposition:
            return
        
        bags = self.tree_decomposition.tree.I
        edges = self.tree_decomposition.tree.F
        
        if not bags:
            return
        
        # Initialize bag positions if needed
        if not self.bag_positions:
            n = len(bags)
            canvas_width = self.tree_canvas.winfo_width()
            canvas_height = self.tree_canvas.winfo_height()
            
            # Use actual canvas size or fallback to reasonable defaults
            if canvas_width <= 1:
                canvas_width = 400
            if canvas_height <= 1:
                canvas_height = 350
            
            # Calculate radius and center
            radius = min(canvas_width, canvas_height) / 3.5
            center_x = canvas_width / 2
            center_y = canvas_height / 2
            
            for i, (vertex, bag) in enumerate(bags.items()):
                angle = 2 * math.pi * i / n
                x = center_x + radius * math.cos(angle)
                y = center_y + radius * math.sin(angle)
                self.bag_positions[bag.label] = (x, y)
        
        # Draw edges between bags with modern style
        for edge in edges:
            bags_list = list(edge)
            b1_label = bags_list[0].label
            b2_label = bags_list[1].label
            if b1_label in self.bag_positions and b2_label in self.bag_positions:
                x1, y1 = self.bag_positions[b1_label]
                x2, y2 = self.bag_positions[b2_label]
                self.tree_canvas.create_line(x1, y1, x2, y2, fill="#616161", width=3, smooth=True)
        
        # Draw bags with modern style
        for vertex, bag in bags.items():
            if bag.label not in self.bag_positions:
                continue
            x, y = self.bag_positions[bag.label]
            
            # Bag content
            content = "{" + ", ".join([str(v) for v in bag.vertices]) + "}"
            
            # Calculate size based on content
            r = max(35, len(content) * 4.5)
            
            # Highlight root in different color
            is_root = self.root_bag and bag.label == self.root_bag.label
            if is_root:
                shadow_color = "#ff6f00"  # Orange shadow for root
                main_color = "#ffa726"     # Orange for root
                outline_color = "#ffb74d"  # Light orange outline
            else:
                shadow_color = "#1b5e20"
                main_color = "#2e7d32"
                outline_color = "#66bb6a"
            
            # Outer shadow
            self.tree_canvas.create_oval(x-r-2, y-r-2, x+r+2, y+r+2, fill=shadow_color, 
                                         outline="", tags=f"bag_{bag.label}")
            # Main circle
            self.tree_canvas.create_oval(x-r, y-r, x+r, y+r, fill=main_color, 
                                         outline=outline_color, width=2, tags=f"bag_{bag.label}")
            # Text
            self.tree_canvas.create_text(x, y, text=content, font=("Segoe UI", 10, "bold"), 
                                        fill="white", tags=f"bag_{bag.label}")
            
    def on_tree_click(self, event):
        item = self.tree_canvas.find_closest(event.x, event.y)[0]
        tags = self.tree_canvas.gettags(item)
        for tag in tags:
            if tag.startswith("bag_"):
                self.dragging = tag.replace("bag_", "")
                self.drag_start_x = event.x
                self.drag_start_y = event.y
                break
                
    def on_tree_drag(self, event):
        if self.dragging and self.dragging in self.bag_positions:
            dx = event.x - self.drag_start_x
            dy = event.y - self.drag_start_y
            x, y = self.bag_positions[self.dragging]
            self.bag_positions[self.dragging] = (x + dx, y + dy)
            self.drag_start_x = event.x
            self.drag_start_y = event.y
            self.draw_tree_decomposition()
            
    def on_tree_release(self, event):
        self.dragging = None
    
    def convert_to_rooted_tree(self):
        """Convert the current tree decomposition to a rooted tree and display it"""
        if not self.tree_decomposition:
            messagebox.showwarning("No Tree Decomposition", "Please compute a tree decomposition first")
            return
        
        if not self.root_bag:
            messagebox.showwarning("No Root Selected", "Please select a root bag from the dropdown")
            return
        
        try:
            tree = self.tree_decomposition.tree
            
            # Build rooted tree using the selected root
            visited = set()
            root_node = RootedTree.build_subtree(tree, self.root_bag, visited)
            print("Rooted tree constructed successfully")
            print(root_node)
            # Create RootedTree object
            self.rooted_tree = RootedTree(root_node, [])
            self.node_positions.clear()
            
            # Draw the rooted tree
            self.draw_rooted_tree()
            messagebox.showinfo("Success", f"Tree decomposition converted to rooted tree with root '{self.root_bag.label}'")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error converting to rooted tree: {str(e)}")
    
    def draw_rooted_tree(self):
        """Draw the rooted tree in hierarchical layout on the rooted tree canvas"""
        self.rooted_canvas.delete("all")
        if not self.rooted_tree:
            return
        
        # Calculate hierarchical positions
        self.node_positions.clear()
        canvas_width = self.rooted_canvas.winfo_width()
        if canvas_width <= 1:
            canvas_width = 400
        
        self._calculate_node_positions(self.rooted_tree.root, 
                                       x=canvas_width / 2,
                                       y=30,
                                       layer_height=70,
                                       layer_width=150)
        
        # Draw edges (parent to children)
        self._draw_node_edges(self.rooted_tree.root)
        
        # Draw nodes
        self._draw_nodes(self.rooted_tree.root)
    
    def _calculate_node_positions(self, node, x, y, layer_height=80, layer_width=200):
        """Calculate positions for nodes in a hierarchical tree layout"""
        self.node_positions[node.label] = (x, y)
        
        if not node.children:
            return
        
        # Calculate spacing for children
        num_children = len(node.children)
        total_width = (num_children - 1) * layer_width if num_children > 1 else 0
        start_x = x - total_width / 2
        
        for i, child in enumerate(node.children):
            child_x = start_x + i * layer_width
            child_y = y + layer_height
            self._calculate_node_positions(child, child_x, child_y, layer_height, layer_width)
    
    def _draw_node_edges(self, node):
        """Draw edges from parent to children on rooted_canvas"""
        if node.label in self.node_positions:
            x1, y1 = self.node_positions[node.label]
            
            for child in node.children:
                if child.label in self.node_positions:
                    x2, y2 = self.node_positions[child.label]
                    self.rooted_canvas.create_line(x1, y1, x2, y2, fill="#616161", width=3, smooth=True)
                    self._draw_node_edges(child)
    
    def _draw_nodes(self, node):
        """Recursively draw nodes with their labels on rooted_canvas"""
        if node.label not in self.node_positions:
            return
        
        x, y = self.node_positions[node.label]
        r = 28
        
        # Check if this is the root node
        is_root = self.rooted_tree and node.label == self.rooted_tree.root.label
        
        if is_root:
            # Highlight root in orange/golden color
            shadow_color = "#ff6f00"
            main_color = "#ffa726"
            outline_color = "#ffb74d"
        else:
            # Regular green color for other nodes
            shadow_color = "#1b5e20"
            main_color = "#2e7d32"
            outline_color = "#66bb6a"
        
        # Outer shadow
        self.rooted_canvas.create_oval(x-r-2, y-r-2, x+r+2, y+r+2, fill=shadow_color, 
                                     outline="", tags=f"node_{node.label}")
        # Main circle
        self.rooted_canvas.create_oval(x-r, y-r, x+r, y+r, fill=main_color, 
                                     outline=outline_color, width=2, tags=f"node_{node.label}")
        # Text
        self.rooted_canvas.create_text(x, y, text=node.label, font=("Segoe UI", 10, "bold"), 
                                    fill="white", tags=f"node_{node.label}")
        
        # Recursively draw children
        for child in node.children:
            self._draw_nodes(child)
    
    def browse_file(self):
        """Open file dialog to select a graph file"""
        file_types = [("Graph Files", "*.lst *.txt"), ("Adjacency List", "*.lst"), ("Edge List", "*.txt"), ("All Files", "*.*")]
        file_path = filedialog.askopenfilename(filetypes=file_types, title="Load Graph File")
        if file_path:
            self.file_path_entry.delete(0, tk.END)
            self.file_path_entry.insert(0, file_path)
    
    def load_from_file(self):
        """Load a graph from the selected file"""
        file_path = self.file_path_entry.get().strip()
        if not file_path:
            messagebox.showwarning("Input Error", "Please select a file or enter a file path")
            return
        
        if not os.path.exists(file_path):
            messagebox.showerror("File Not Found", f"File '{file_path}' does not exist")
            return
        
        try:
            # Determine file type by extension
            if file_path.endswith('.lst'):
                graph = load_graph_from_adjacency_list(file_path)
            elif file_path.endswith('.txt'):
                graph = load_graph_from_edge_list(file_path)
            else:
                # Try adjacency list first, then edge list
                graph = load_graph_from_adjacency_list(file_path)
                if not graph:
                    graph = load_graph_from_edge_list(file_path)
            
            if not graph:
                messagebox.showerror("Error", "Failed to load graph from file")
                return
            
            # Clear current graph
            self.vertices.clear()
            self.edges.clear()
            self.vertex_positions.clear()
            self.tree_decomposition = None
            self.bag_positions.clear()
            
            # Load graph data
            self.vertices = {v.label: v for v in graph.vertices}
            self.edges = graph.edges
            
            # Update UI
            self.update_lists()
            self.draw_graph()
            self.tree_canvas.delete("all")
            
            messagebox.showinfo("Success", f"Graph loaded successfully!\nVertices: {len(graph.vertices)}, Edges: {len(graph.edges)}")
            self.file_path_entry.delete(0, tk.END)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error loading graph: {str(e)}")
    
    def save_graph(self):
        name = self.save_name_entry.get().strip()
        if not name:
            messagebox.showwarning("Input Error", "Please enter a graph name")
            return
        
        if not self.vertices:
            messagebox.showwarning("Empty Graph", "Please add vertices first")
            return
        
        # Convert vertices and edges to serializable format
        vertices_data = {label: label for label in self.vertices.keys()}
        edges_data = [sorted([str(v) for v in e]) for e in self.edges]
        
        self.saved_graphs[name] = {
            "vertices": vertices_data,
            "edges": edges_data
        }
        
        self.save_graphs_to_file()
        messagebox.showinfo("Success", f"Graph '{name}' saved successfully")
        self.save_name_entry.delete(0, tk.END)
        self.refresh_saved_graphs()
    
    def load_graph(self):
        name = self.load_name_entry.get().strip()
        if not name:
            messagebox.showwarning("Input Error", "Please enter a graph name")
            return
        
        if name not in self.saved_graphs:
            messagebox.showwarning("Not Found", f"Graph '{name}' not found")
            return
        
        # Clear current graph
        self.vertices.clear()
        self.edges.clear()
        self.vertex_positions.clear()
        
        # Load graph data
        graph_data = self.saved_graphs[name]
        
        # Load vertices
        for label in graph_data["vertices"].keys():
            self.vertices[label] = Vertex(label)
        
        # Load edges
        for edge_data in graph_data["edges"]:
            if len(edge_data) == 2 and edge_data[0] in self.vertices and edge_data[1] in self.vertices:
                self.edges.append({self.vertices[edge_data[0]], self.vertices[edge_data[1]]})
        
        self.update_lists()
        self.draw_graph()
        self.load_name_entry.delete(0, tk.END)
        messagebox.showinfo("Success", f"Graph '{name}' loaded successfully")
    
    def delete_graph(self):
        name = self.load_name_entry.get().strip()
        if not name:
            messagebox.showwarning("Input Error", "Please enter a graph name")
            return
        
        if name not in self.saved_graphs:
            messagebox.showwarning("Not Found", f"Graph '{name}' not found")
            return
        
        del self.saved_graphs[name]
        self.save_graphs_to_file()
        messagebox.showinfo("Success", f"Graph '{name}' deleted successfully")
        self.load_name_entry.delete(0, tk.END)
        self.refresh_saved_graphs()
    
    def refresh_saved_graphs(self):
        self.saved_graphs_list.delete("1.0", "end")
        if not self.saved_graphs:
            self.saved_graphs_list.insert("1.0", "No saved graphs")
        else:
            graphs_text = "\n".join(sorted(self.saved_graphs.keys()))
            self.saved_graphs_list.insert("1.0", graphs_text)
    
    def load_graphs_from_file(self):
        """Load saved graphs from JSON file"""
        if os.path.exists(self.graphs_file):
            try:
                with open(self.graphs_file, 'r') as f:
                    self.saved_graphs = json.load(f)
            except Exception as e:
                print(f"Error loading graphs from file: {e}")
                self.saved_graphs = {}
        else:
            self.saved_graphs = {}
    
    def save_graphs_to_file(self):
        """Save all graphs to JSON file"""
        try:
            with open(self.graphs_file, 'w') as f:
                json.dump(self.saved_graphs, f, indent=2)
        except Exception as e:
            print(f"Error saving graphs to file: {e}")
    
    def on_closing(self):
        """Handle window closing - save graphs before exit"""
        self.save_graphs_to_file()
        self.root.destroy()

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    app = GraphGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
