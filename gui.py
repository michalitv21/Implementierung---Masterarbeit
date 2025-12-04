import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import math
from graph import Graph, Vertex, minimal_degree_ordering, permutationToTreeDecomposition, minimize_TreeDecomposition
from treeDecomp import TreeDecomposition

class GraphGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Tree Decomposition Visualizer")
        self.root.geometry("1400x800")
        
        # Set appearance mode and color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Data structures
        self.vertices = {}  # label -> Vertex
        self.edges = []  # list of sets {v1, v2}
        self.graph = None
        self.tree_decomposition = None
        
        # Canvas positions for dragging
        self.vertex_positions = {}  # label -> (x, y)
        self.bag_positions = {}  # bag_label -> (x, y)
        self.dragging = None
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
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
        ctk.CTkButton(button_frame, text="Clear All", command=self.clear_all, width=85, fg_color="#d32f2f", hover_color="#9a0007").pack(side="left", padx=3)
        ctk.CTkButton(button_frame, text="Compute", command=self.compute_tree_decomposition, width=85, fg_color="#2e7d32", hover_color="#1b5e20").pack(side="left", padx=3)
        ctk.CTkButton(button_frame, text="Minimize", command=self.minimize_tree_decomposition, width=85, fg_color="#f57c00", hover_color="#e65100").pack(side="left", padx=3)
        
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
        
        # Right panel - Visualizations
        viz_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        viz_frame.grid(row=0, column=1, rowspan=2, sticky="nsew")
        viz_frame.columnconfigure(0, weight=1)
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
        
        ctk.CTkLabel(tree_frame, text="Tree Decomposition", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, sticky="w", padx=15, pady=(15, 10))
        
        self.tree_canvas = ctk.CTkCanvas(tree_frame, bg="#1a1a1a", width=800, height=350, highlightthickness=0)
        self.tree_canvas.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        self.tree_canvas.bind("<Button-1>", self.on_tree_click)
        self.tree_canvas.bind("<B1-Motion>", self.on_tree_drag)
        self.tree_canvas.bind("<ButtonRelease-1>", self.on_tree_release)
        
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
        self.tree_decomposition = None
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
        
        # Create a copy of the graph
        vertex_list = list(self.vertices.values())
        edge_list = [e.copy() for e in self.edges]
        graph_copy = Graph(vertex_list.copy(), edge_list)
        
        # Get vertex ordering
        if self.ordering_var.get() == "minimal_degree":
            ordering = minimal_degree_ordering(graph_copy)
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
            ordering = [self.vertices[l] for l in labels]
        
        # Compute tree decomposition
        graph_copy2 = Graph(vertex_list.copy(), [e.copy() for e in self.edges])
        self.tree = permutationToTreeDecomposition(graph_copy2, ordering)
        self.tree_decomposition = TreeDecomposition(self.tree.I, self.tree)
        
        self.draw_tree_decomposition()
    
    def minimize_tree_decomposition(self):
        if not self.tree_decomposition:
            messagebox.showwarning("No Tree Decomposition", "Please compute a tree decomposition first")
            return
        
        # Minimize the tree decomposition
        self.tree_decomposition = minimize_TreeDecomposition(self.tree_decomposition)
        
        # Clear bag positions to force recalculation with new structure
        self.bag_positions.clear()
        
        # Redraw the tree decomposition
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
            radius = min(self.tree_canvas.winfo_width(), self.tree_canvas.winfo_height()) / 3
            if radius == 0:
                radius = 150
            center_x = self.tree_canvas.winfo_width() / 2
            center_y = self.tree_canvas.winfo_height() / 2
            if center_x == 0:
                center_x = 400
            if center_y == 0:
                center_y = 175
            
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
            
            # Outer shadow
            self.tree_canvas.create_oval(x-r-2, y-r-2, x+r+2, y+r+2, fill="#1b5e20", 
                                         outline="", tags=f"bag_{bag.label}")
            # Main circle
            self.tree_canvas.create_oval(x-r, y-r, x+r, y+r, fill="#2e7d32", 
                                         outline="#66bb6a", width=2, tags=f"bag_{bag.label}")
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

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    app = GraphGUI(root)
    root.mainloop()
