import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import math
from treeDecomp import Node, RootedTree
from treeAutomata import TreeAutomaton
from itertools import product

class TreeAutomatonGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Tree Automaton Visualizer")
        self.root.geometry("1600x900")
        
        # Set appearance mode and color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Data structures
        self.nodes = []  # List of all nodes in the tree
        self.rooted_tree = None
        self.automaton = None
        self.evaluation_results = {}  # node -> set of states
        self.current_step = 0
        self.evaluation_steps = []  # List of (node, states) tuples for stepwise visualization
        self.next_node_id = 1  # Auto-increment counter for node IDs
        
        # Canvas positions
        self.node_positions = {}  # node -> (x, y)
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
        main_frame.columnconfigure(0, weight=0)  # Left panel
        main_frame.columnconfigure(1, weight=1)  # Middle panel (tree)
        main_frame.columnconfigure(2, weight=0)  # Right panel
        main_frame.rowconfigure(0, weight=1)
        
        # Left panel - Tree construction
        tree_panel = ctk.CTkFrame(main_frame, corner_radius=15)
        tree_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        
        ctk.CTkLabel(tree_panel, text="Tree Builder", font=ctk.CTkFont(size=18, weight="bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(20, 15))
        
        # Node creation section
        ctk.CTkLabel(tree_panel, text="Add Node:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=1, column=0, columnspan=2, sticky="w", padx=20, pady=(10, 5))
        
        ctk.CTkLabel(tree_panel, text="Label:", font=ctk.CTkFont(size=11)).grid(
            row=2, column=0, sticky="w", padx=20, pady=5)
        self.node_label_entry = ctk.CTkEntry(tree_panel, width=150, placeholder_text="e.g., 'and', '0', '1'")
        self.node_label_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        
        ctk.CTkLabel(tree_panel, text="Parent ID:", font=ctk.CTkFont(size=11)).grid(
            row=3, column=0, sticky="w", padx=20, pady=5)
        self.parent_id_entry = ctk.CTkEntry(tree_panel, width=150, placeholder_text="Leave empty for root")
        self.parent_id_entry.grid(row=3, column=1, padx=10, pady=5, sticky="w")
        
        ctk.CTkButton(tree_panel, text="Add Node", command=self.add_node, 
                     width=180, fg_color="#1f6aa5", hover_color="#144870").grid(
            row=4, column=0, columnspan=2, padx=20, pady=10)
        
        # Tree list
        ctk.CTkLabel(tree_panel, text="Tree Nodes:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=5, column=0, columnspan=2, sticky="w", padx=20, pady=(15, 5))
        self.tree_list = ctk.CTkTextbox(tree_panel, width=280, height=120, 
                                        font=ctk.CTkFont(family="Consolas", size=10))
        self.tree_list.grid(row=6, column=0, columnspan=2, padx=20, pady=(0, 10))
        
        # Quick tree templates
        ctk.CTkLabel(tree_panel, text="Templates:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=7, column=0, columnspan=2, sticky="w", padx=20, pady=(15, 5))
        ctk.CTkButton(tree_panel, text="Boolean Expression", command=self.load_boolean_template,
                     width=180, fg_color="#9c27b0", hover_color="#6a1b9a").grid(
            row=8, column=0, columnspan=2, padx=20, pady=5)
        
        ctk.CTkButton(tree_panel, text="Clear Tree", command=self.clear_tree,
                     width=180, fg_color="#d32f2f", hover_color="#9a0007").grid(
            row=9, column=0, columnspan=2, padx=20, pady=(5, 20))
        
        # Middle panel - Tree visualization
        viz_frame = ctk.CTkFrame(main_frame, corner_radius=15)
        viz_frame.grid(row=0, column=1, sticky="nsew")
        viz_frame.columnconfigure(0, weight=1)
        viz_frame.rowconfigure(1, weight=1)
        
        # Header with controls
        header_frame = ctk.CTkFrame(viz_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 10))
        
        ctk.CTkLabel(header_frame, text="Tree & Evaluation", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
        
        # Step controls
        step_control_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        step_control_frame.pack(side="right")
        
        self.prev_button = ctk.CTkButton(step_control_frame, text="◀ Prev", 
                                        command=self.prev_step, width=70,
                                        fg_color="#455a64", hover_color="#263238")
        self.prev_button.pack(side="left", padx=2)
        
        self.step_label = ctk.CTkLabel(step_control_frame, text="Step: 0/0",
                                      font=ctk.CTkFont(size=11, weight="bold"))
        self.step_label.pack(side="left", padx=10)
        
        self.next_button = ctk.CTkButton(step_control_frame, text="Next ▶", 
                                        command=self.next_step, width=70,
                                        fg_color="#455a64", hover_color="#263238")
        self.next_button.pack(side="left", padx=2)
        
        ctk.CTkButton(step_control_frame, text="Reset", command=self.reset_visualization,
                     width=70, fg_color="#f57c00", hover_color="#e65100").pack(side="left", padx=5)
        
        # Canvas for tree
        self.tree_canvas = ctk.CTkCanvas(viz_frame, bg="#1a1a1a", width=800, height=800, 
                                         highlightthickness=0)
        self.tree_canvas.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        self.tree_canvas.bind("<Button-1>", self.on_canvas_click)
        self.tree_canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.tree_canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        
        # Right panel - Automaton definition
        automaton_panel = ctk.CTkFrame(main_frame, corner_radius=15)
        automaton_panel.grid(row=0, column=2, sticky="nsew", padx=(15, 0))
        
        ctk.CTkLabel(automaton_panel, text="Automaton", 
                    font=ctk.CTkFont(size=18, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=20, pady=(20, 15))
        
        # States
        ctk.CTkLabel(automaton_panel, text="States (comma-separated):", 
                    font=ctk.CTkFont(size=11, weight="bold")).grid(
            row=1, column=0, sticky="w", padx=20, pady=(10, 5))
        self.states_entry = ctk.CTkEntry(automaton_panel, width=280, 
                                         placeholder_text="e.g., q0, q1, q2")
        self.states_entry.grid(row=2, column=0, padx=20, pady=(0, 10))
        
        # Input symbols
        ctk.CTkLabel(automaton_panel, text="Input Symbols (comma-separated):", 
                    font=ctk.CTkFont(size=11, weight="bold")).grid(
            row=3, column=0, sticky="w", padx=20, pady=5)
        self.symbols_entry = ctk.CTkEntry(automaton_panel, width=280, 
                                          placeholder_text="e.g., 0, 1, and, or, not")
        self.symbols_entry.grid(row=4, column=0, padx=20, pady=(0, 10))
        
        # Final states
        ctk.CTkLabel(automaton_panel, text="Final States (comma-separated):", 
                    font=ctk.CTkFont(size=11, weight="bold")).grid(
            row=5, column=0, sticky="w", padx=20, pady=5)
        self.final_states_entry = ctk.CTkEntry(automaton_panel, width=280, 
                                               placeholder_text="e.g., q1")
        self.final_states_entry.grid(row=6, column=0, padx=20, pady=(0, 10))
        
        # Transitions
        ctk.CTkLabel(automaton_panel, text="Transitions:", 
                    font=ctk.CTkFont(size=11, weight="bold")).grid(
            row=7, column=0, sticky="w", padx=20, pady=(10, 5))
        
        ctk.CTkLabel(automaton_panel, text="Format: symbol,state1,state2,...->result", 
                    font=ctk.CTkFont(size=9)).grid(
            row=8, column=0, sticky="w", padx=20, pady=(0, 5))
        
        self.transitions_text = ctk.CTkTextbox(automaton_panel, width=280, height=250,
                                               font=ctk.CTkFont(family="Consolas", size=9))
        self.transitions_text.grid(row=9, column=0, padx=20, pady=(0, 10))
        
        # Buttons
        ctk.CTkButton(automaton_panel, text="Load Boolean Automaton", 
                     command=self.load_boolean_automaton, width=280,
                     fg_color="#9c27b0", hover_color="#6a1b9a").grid(
            row=10, column=0, padx=20, pady=5)
        
        ctk.CTkButton(automaton_panel, text="Create Automaton", 
                     command=self.create_automaton, width=280,
                     fg_color="#1f6aa5", hover_color="#144870").grid(
            row=11, column=0, padx=20, pady=5)
        
        ctk.CTkButton(automaton_panel, text="Run Automaton", 
                     command=self.run_automaton, width=280,
                     fg_color="#2e7d32", hover_color="#1b5e20").grid(
            row=12, column=0, padx=20, pady=(15, 10))
        
        # Result display
        ctk.CTkLabel(automaton_panel, text="Result:", 
                    font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=13, column=0, sticky="w", padx=20, pady=(15, 5))
        self.result_label = ctk.CTkLabel(automaton_panel, text="Not evaluated", 
                                        font=ctk.CTkFont(size=11),
                                        text_color="#9e9e9e")
        self.result_label.grid(row=14, column=0, sticky="w", padx=20, pady=(0, 20))
        
        self.update_step_buttons()
        
    def add_node(self):
        """Add a node to the tree"""
        label = self.node_label_entry.get().strip()
        parent_id_str = self.parent_id_entry.get().strip()
        
        if not label:
            messagebox.showwarning("Input Error", "Please enter a node label")
            return
        
        # Assign the next available ID
        node_id = self.next_node_id
        self.next_node_id += 1
        
        new_node = Node(label, node_id, [])
        
        if not parent_id_str:
            # This is the root
            if self.rooted_tree is not None:
                response = messagebox.askyesno("Root Exists", 
                    "A root already exists. Replace the entire tree?")
                if not response:
                    # Decrement ID counter since we didn't use it
                    self.next_node_id -= 1
                    return
                self.nodes = []
                self.rooted_tree = None
            
            nodes_list = [new_node]
            self.nodes = nodes_list
            self.rooted_tree = RootedTree(new_node, nodes_list)
        else:
            # Find parent node by ID
            try:
                parent_id = int(parent_id_str)
            except ValueError:
                messagebox.showwarning("Input Error", "Parent ID must be an integer")
                # Decrement ID counter since we didn't use it
                self.next_node_id -= 1
                return
            
            parent_node = None
            for node in self.nodes:
                if node.id == parent_id:
                    parent_node = node
                    break
            
            if parent_node is None:
                messagebox.showwarning("Parent Not Found", 
                    f"No node with ID {parent_id} found")
                # Decrement ID counter since we didn't use it
                self.next_node_id -= 1
                return
            
            parent_node.add_child(new_node)
            self.nodes.append(new_node)
            if self.rooted_tree:
                self.rooted_tree.nodes = self.nodes
        
        self.node_label_entry.delete(0, tk.END)
        self.parent_id_entry.delete(0, tk.END)
        self.update_tree_list()
        self.draw_tree()
        
    def clear_tree(self):
        """Clear the entire tree"""
        self.nodes = []
        self.rooted_tree = None
        self.evaluation_results = {}
        self.current_step = 0
        self.evaluation_steps = []
        self.node_positions = {}
        self.next_node_id = 1  # Reset ID counter
        self.update_tree_list()
        self.draw_tree()
        self.update_step_buttons()
        self.result_label.configure(text="Not evaluated", text_color="#9e9e9e")
        
    def load_boolean_template(self):
        """Load the boolean expression example tree"""
        self.clear_tree()
        
        # Create the same tree from the example with label and id
        node1 = Node("0", 1, [])
        node2 = Node("1", 2, [])
        node3 = Node("0", 3, [])
        node4 = Node("or", 4, [node1, node2])
        node5 = Node("1", 5, [])
        node6 = Node("not", 6, [node3])
        node7 = Node("not", 7, [node4])
        node8 = Node("or", 8, [node5, node6])
        node9 = Node("and", 9, [node7, node8])
        
        self.nodes = [node1, node2, node3, node4, node5, node6, node7, node8, node9]
        self.rooted_tree = RootedTree(node9, self.nodes)
        
        self.update_tree_list()
        self.draw_tree()
        messagebox.showinfo("Template Loaded", "Boolean expression tree loaded successfully")
        
    def update_tree_list(self):
        """Update the tree nodes list display"""
        self.tree_list.delete("1.0", tk.END)
        if self.rooted_tree:
            self.tree_list.insert("1.0", f"Root: {self.rooted_tree.root.label} (ID: {self.rooted_tree.root.id})\n\n")
            self.tree_list.insert(tk.END, "All nodes:\n")
            for i, node in enumerate(self.nodes):
                children_labels = [f"{c.label}({c.id})" for c in node.children]
                children_str = ", ".join(children_labels) if children_labels else "leaf"
                self.tree_list.insert(tk.END, f"{i+1}. {node.label}({node.id}) -> [{children_str}]\n")
        else:
            self.tree_list.insert("1.0", "No tree created yet")
            
    def draw_tree(self):
        """Draw the tree on the canvas"""
        self.tree_canvas.delete("all")
        if not self.rooted_tree:
            return
        
        # Calculate positions
        self.node_positions.clear()
        canvas_width = self.tree_canvas.winfo_width()
        canvas_height = self.tree_canvas.winfo_height()
        if canvas_width <= 1:
            canvas_width = 800
        if canvas_height <= 1:
            canvas_height = 800
        
        # Use improved layout algorithm
        self._calculate_positions_improved(self.rooted_tree.root, 
                                          x=canvas_width / 2, 
                                          y=50,
                                          layer_height=120,
                                          min_spacing=100)
        
        # Draw edges
        self._draw_edges(self.rooted_tree.root)
        
        # Draw nodes
        self._draw_nodes(self.rooted_tree.root)
        
    def _calculate_positions_improved(self, node, x, y, layer_height=120, min_spacing=100):
        """Calculate positions using improved layout algorithm that prevents overlapping"""
        self.node_positions[node] = (x, y)
        
        if not node.children:
            return
        
        # Calculate the total width needed for this subtree
        num_children = len(node.children)
        
        # Recursively calculate widths for all children first
        child_widths = []
        for child in node.children:
            width = self._get_subtree_width(child, min_spacing)
            child_widths.append(width)
        
        # Calculate positions for children with proper spacing
        total_width = sum(child_widths) + (num_children - 1) * min_spacing
        start_x = x - total_width / 2
        
        current_x = start_x
        for i, child in enumerate(node.children):
            # Position child at the center of its allocated space
            child_x = current_x + child_widths[i] / 2
            child_y = y + layer_height
            self._calculate_positions_improved(child, child_x, child_y, layer_height, min_spacing)
            current_x += child_widths[i] + min_spacing
    
    def _get_subtree_width(self, node, min_spacing=100):
        """Calculate the total width needed to render a subtree"""
        node_radius = 30
        
        if not node.children or len(node.children) == 0:
            # Leaf node - just the node itself
            return node_radius * 2 + 20
        
        # For internal nodes, sum the widths of all children plus spacing
        total_width = 0
        for child in node.children:
            total_width += self._get_subtree_width(child, min_spacing)
        
        # Add spacing between children
        if len(node.children) > 1:
            total_width += (len(node.children) - 1) * min_spacing
        
        # Ensure minimum width for the node itself
        return max(total_width, node_radius * 2 + 20)
            
    def _draw_edges(self, node):
        """Draw edges from parent to children"""
        if node not in self.node_positions:
            return
        
        x1, y1 = self.node_positions[node]
        
        for child in node.children:
            if child in self.node_positions:
                x2, y2 = self.node_positions[child]
                self.tree_canvas.create_line(x1, y1, x2, y2, 
                                            fill="#616161", width=3, smooth=True)
                self._draw_edges(child)
                
    def _draw_nodes(self, node):
        """Draw nodes with labels and state information"""
        if node not in self.node_positions:
            return
        
        x, y = self.node_positions[node]
        r = 30
        
        # Determine color based on evaluation state
        if self.current_step > 0 and node in self.evaluation_results:
            # Node has been evaluated
            node_states = self.evaluation_results[node]
            if node_states is None:
                # Invalid symbol
                color = "#d32f2f"
                outline = "#f44336"
            elif len(node_states) > 0:
                # Has valid states
                if node == self.rooted_tree.root and self.automaton and node_states & self.automaton.final_states:
                    # Root is in final state - success!
                    color = "#2e7d32"
                    outline = "#66bb6a"
                else:
                    color = "#1976d2"
                    outline = "#64b5f6"
            else:
                # No valid states
                color = "#f57c00"
                outline = "#ffb74d"
        else:
            # Not yet evaluated
            color = "#424242"
            outline = "#757575"
        
        # Highlight current step
        if (self.current_step > 0 and self.current_step <= len(self.evaluation_steps) and 
            self.evaluation_steps[self.current_step - 1][0] == node):
            # Draw extra outline for current node
            self.tree_canvas.create_oval(x-r-4, y-r-4, x+r+4, y+r+4, 
                                        fill="", outline="#ffeb3b", width=3,
                                        tags=f"node_{id(node)}")
        
        # Shadow
        self.tree_canvas.create_oval(x-r-2, y-r-2, x+r+2, y+r+2, 
                                    fill="#000000", outline="",
                                    tags=f"node_{id(node)}")
        # Main circle
        self.tree_canvas.create_oval(x-r, y-r, x+r, y+r, 
                                    fill=color, outline=outline, width=2,
                                    tags=f"node_{id(node)}")
        # Label
        self.tree_canvas.create_text(x, y, text=node.label, 
                                    font=("Segoe UI", 11, "bold"), 
                                    fill="white", tags=f"node_{id(node)}")
        
        # ID annotation (smaller text below label)
        self.tree_canvas.create_text(x, y + 10, text=f"#{node.id}", 
                                    font=("Segoe UI", 8), 
                                    fill="#bdbdbd", tags=f"node_{id(node)}")
        
        # State annotation below node
        if node in self.evaluation_results and self.evaluation_results[node] is not None:
            states_str = "{" + ", ".join(sorted(self.evaluation_results[node])) + "}"
            self.tree_canvas.create_text(x, y + r + 15, text=states_str,
                                        font=("Consolas", 9), 
                                        fill="#bdbdbd", tags=f"state_{id(node)}")
        
        # Recursively draw children
        for child in node.children:
            self._draw_nodes(child)
            
    def on_canvas_click(self, event):
        """Handle mouse click for dragging"""
        item = self.tree_canvas.find_closest(event.x, event.y)[0]
        tags = self.tree_canvas.gettags(item)
        for tag in tags:
            if tag.startswith("node_"):
                self.dragging = tag
                self.drag_start_x = event.x
                self.drag_start_y = event.y
                break
                
    def on_canvas_drag(self, event):
        """Handle mouse drag"""
        if self.dragging:
            # Find the node being dragged
            for node, pos in self.node_positions.items():
                if f"node_{id(node)}" == self.dragging:
                    dx = event.x - self.drag_start_x
                    dy = event.y - self.drag_start_y
                    x, y = pos
                    self.node_positions[node] = (x + dx, y + dy)
                    self.drag_start_x = event.x
                    self.drag_start_y = event.y
                    self.draw_tree()
                    break
                    
    def on_canvas_release(self, event):
        """Handle mouse release"""
        self.dragging = None
        
    def load_boolean_automaton(self):
        """Load the example boolean automaton"""
        self.states_entry.delete(0, tk.END)
        self.states_entry.insert(0, "q0, q1")
        
        self.symbols_entry.delete(0, tk.END)
        self.symbols_entry.insert(0, "0, 1, and, or, not")
        
        self.final_states_entry.delete(0, tk.END)
        self.final_states_entry.insert(0, "q1")
        
        self.transitions_text.delete("1.0", tk.END)
        transitions = [
            "0->q0",
            "1->q1",
            "or,q0,q0->q0",
            "or,q0,q1->q1",
            "or,q1,q0->q1",
            "or,q1,q1->q1",
            "and,q0,q0->q0",
            "and,q0,q1->q0",
            "and,q1,q0->q0",
            "and,q1,q1->q1",
            "not,q0->q1",
            "not,q1->q0",
        ]
        self.transitions_text.insert("1.0", "\n".join(transitions))
        
        messagebox.showinfo("Automaton Loaded", "Boolean automaton template loaded")
        
    def create_automaton(self):
        """Create the automaton from the input fields"""
        try:
            # Parse states
            states_str = self.states_entry.get().strip()
            if not states_str:
                messagebox.showwarning("Input Error", "Please enter states")
                return
            states = {s.strip() for s in states_str.split(",")}
            
            # Parse input symbols
            symbols_str = self.symbols_entry.get().strip()
            # Allow empty input symbols; we'll infer from transitions if needed
            input_symbols = {s.strip() for s in symbols_str.split(",")} if symbols_str else set()
            
            # Parse final states
            final_str = self.final_states_entry.get().strip()
            if not final_str:
                messagebox.showwarning("Input Error", "Please enter final states")
                return
            final_states = {s.strip() for s in final_str.split(",")}
            
            # Validate final states are in states
            if not final_states.issubset(states):
                messagebox.showwarning("Invalid Input", 
                    "Final states must be a subset of states")
                return
            
            # Parse transitions
            transitions_text = self.transitions_text.get("1.0", tk.END).strip()
            if not transitions_text:
                messagebox.showwarning("Input Error", "Please enter transitions")
                return
            
            transitions = {}
            for line in transitions_text.split("\n"):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                
                try:
                    left, right = line.split("->")
                    left_parts = [p.strip() for p in left.split(",")]
                    result_state = right.strip()
                    
                    if result_state not in states:
                        messagebox.showwarning("Invalid Transition", 
                            f"State '{result_state}' not in states")
                        return
                    
                    key = tuple(left_parts)
                    if key not in transitions:
                        transitions[key] = set()
                    transitions[key].add(result_state)
                    
                except ValueError:
                    messagebox.showwarning("Invalid Transition", 
                        f"Invalid transition format: {line}")
                    return
            
            # Infer input symbols from transitions if not provided, or merge
            symbols_from_transitions = {k[0] for k in transitions.keys() if len(k) >= 1}
            if not input_symbols:
                input_symbols = symbols_from_transitions
            else:
                # Merge any symbols referenced in transitions
                missing = symbols_from_transitions - input_symbols
                if missing:
                    input_symbols = input_symbols.union(missing)
                    # Inform the user we auto-added symbols
                    messagebox.showinfo(
                        "Symbols Updated",
                        f"Added symbols from transitions: {', '.join(sorted(missing))}"
                    )

            # Create the automaton
            self.automaton = TreeAutomaton(
                states=states,
                input_symbols=input_symbols,
                final_states=final_states,
                transitions=transitions
            )
            
            messagebox.showinfo("Success", "Automaton created successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error creating automaton: {str(e)}")
            
    def run_automaton(self):
        """Run the automaton on the tree with step-by-step evaluation"""
        if not self.automaton:
            messagebox.showwarning("No Automaton", "Please create an automaton first")
            return
        
        if not self.rooted_tree:
            messagebox.showwarning("No Tree", "Please create a tree first")
            return
        
        try:
            # Reset evaluation
            self.evaluation_results = {}
            self.evaluation_steps = []
            self.current_step = 0
            
            # Perform evaluation and collect steps
            self._evaluate_with_steps(self.rooted_tree.root)
            
            # Show result
            root_states = self.evaluation_results[self.rooted_tree.root]
            if root_states is None:
                result_text = "Invalid symbol at root"
                color = "#f44336"
            elif len(root_states & self.automaton.final_states) > 0:
                result_text = f"ACCEPTED - Final states: {root_states & self.automaton.final_states}"
                color = "#66bb6a"
            else:
                result_text = f"REJECTED - States: {root_states}"
                color = "#f57c00"
            
            self.result_label.configure(text=result_text, text_color=color)
            
            # Start visualization from beginning
            self.current_step = 0
            self.update_step_buttons()
            self.draw_tree()
            
            messagebox.showinfo("Evaluation Complete", 
                f"Automaton evaluated tree in {len(self.evaluation_steps)} steps")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error running automaton: {str(e)}")
            
    def _evaluate_with_steps(self, node):
        """Recursively evaluate nodes and collect steps"""
        # First evaluate children
        for child in node.children:
            self._evaluate_with_steps(child)
        
        # Then evaluate this node
        if node.label in self.automaton.input_symbols:
            if node.is_leaf():
                key = (node.label,)
                next_state = self.automaton.transitions.get(key, set())
                self.evaluation_results[node] = next_state
                self.evaluation_steps.append((node, next_state))
            else:
                child_states_lists = [self.evaluation_results[child] for child in node.children]
                possible_states = set()
                
                for child_states in product(*child_states_lists):
                    key = (node.label,) + child_states
                    possible_states.update(self.automaton.transitions.get(key, set()))
                
                self.evaluation_results[node] = possible_states
                self.evaluation_steps.append((node, possible_states))
        else:
            self.evaluation_results[node] = None
            self.evaluation_steps.append((node, None))
            
    def next_step(self):
        """Move to the next evaluation step"""
        if self.current_step < len(self.evaluation_steps):
            self.current_step += 1
            self.update_step_buttons()
            self.draw_tree()
            
    def prev_step(self):
        """Move to the previous evaluation step"""
        if self.current_step > 0:
            self.current_step -= 1
            # Clear evaluation results for nodes after current step
            if self.current_step == 0:
                self.evaluation_results = {}
            else:
                # Keep only the results up to current step
                temp_results = {}
                for i in range(self.current_step):
                    node, states = self.evaluation_steps[i]
                    temp_results[node] = states
                self.evaluation_results = temp_results
            
            self.update_step_buttons()
            self.draw_tree()
            
    def reset_visualization(self):
        """Reset to the beginning of the visualization"""
        self.current_step = 0
        self.evaluation_results = {}
        self.update_step_buttons()
        self.draw_tree()
        
    def update_step_buttons(self):
        """Update the step control buttons and label"""
        if len(self.evaluation_steps) == 0:
            self.prev_button.configure(state="disabled")
            self.next_button.configure(state="disabled")
            self.step_label.configure(text="Step: 0/0")
        else:
            # Update label
            self.step_label.configure(text=f"Step: {self.current_step}/{len(self.evaluation_steps)}")
            
            # Update buttons
            if self.current_step == 0:
                self.prev_button.configure(state="disabled")
            else:
                self.prev_button.configure(state="normal")
            
            if self.current_step >= len(self.evaluation_steps):
                self.next_button.configure(state="disabled")
            else:
                self.next_button.configure(state="normal")
                
            # Apply evaluation results up to current step
            temp_results = {}
            for i in range(self.current_step):
                node, states = self.evaluation_steps[i]
                temp_results[node] = states
            self.evaluation_results = temp_results


if __name__ == "__main__":
    root = ctk.CTk()
    app = TreeAutomatonGUI(root)
    root.mainloop()
