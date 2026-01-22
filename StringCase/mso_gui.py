import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from mso import MSO_Parser
from itertools import product

class MSO_GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MSO Formula Tester")
        self.root.geometry("1200x900")
        
        # Set appearance mode and color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Data
        self.alphabet = {'a', 'b', 'c'}
        self.formula_text = ""
        self.test_word = ""
        self.last_result = None
        self.test_words = []
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface"""
        main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(5, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(main_frame, text="MSO Formula Tester", font=("Arial", 20, "bold"))
        title_label.grid(row=0, column=0, columnspan=7, pady=(0, 10))
        
        # ===== FORMULA INPUT SECTION =====
        formula_label = ctk.CTkLabel(main_frame, text="Enter MSO Formula:", font=("Arial", 12, "bold"))
        formula_label.grid(row=1, column=0, columnspan=7, sticky="w", pady=(10, 5))
        
        # Formula text area
        self.formula_text_widget = ctk.CTkTextbox(main_frame, height=80, wrap="word")
        self.formula_text_widget.grid(row=2, column=0, columnspan=7, sticky="nsew", pady=(0, 10))
        main_frame.grid_rowconfigure(2, weight=0)
        
        # Buttons frame for formula symbols
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.grid(row=3, column=0, columnspan=7, sticky="ew", pady=(10, 10))
        
        # All available symbols
        symbols = [
            ("∃", "∃"),
            ("∀", "∀"),
            ("∧", "and(,)"),
            ("∨", "or(,)"),
            ("¬", "not()"),
            ("→", "->(,)"),
            ("↔", "<->(,)"),
            ("≤", "le(,)"),
            ("<", "and(le(,),not(le(,)))"),
            ("∈", "in(,)"),
            ("P_a", "P_a()"),
            ("P_b", "P_b()"),
            ("P_c", "P_c()"),
            ("card_eq", "card_eq(,)"),
            ("(", "("),
            (")", ")"),
            ("x", "x"),
            ("y", "y"),
            ("z", "z"),
            ("X", "X"),
            ("Y", "Y"),
            ("Z", "Z"),
        ]
        
        col = 0
        row = 0
        for display, insert_text in symbols:
            btn = ctk.CTkButton(
                buttons_frame,
                text=display,
                width=50,
                height=28,
                font=("Arial", 10),
                command=lambda text=insert_text: self.insert_symbol(text)
            )
            btn.grid(row=row, column=col, padx=2, pady=2)
            col += 1
            if col >= 7:
                col = 0
                row += 1
        
        # ===== CONFIG SECTION =====
        config_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        config_frame.grid(row=4, column=0, columnspan=7, sticky="ew", pady=(10, 10))
        
        # Alphabet
        alphabet_label = ctk.CTkLabel(config_frame, text="Alphabet:", font=("Arial", 11, "bold"))
        alphabet_label.grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        self.alphabet_input = ctk.CTkEntry(config_frame, width=200, placeholder_text="e.g., 'a,b,c'")
        self.alphabet_input.insert(0, "a,b,c")
        self.alphabet_input.grid(row=0, column=1, sticky="ew", padx=(0, 20))
        
        update_words_btn = ctk.CTkButton(
            config_frame,
            text="Generate Test Words",
            width=150,
            command=self.generate_test_words
        )
        update_words_btn.grid(row=0, column=2, padx=(0, 20))
        
        clear_btn = ctk.CTkButton(
            config_frame,
            text="Clear Formula",
            width=100,
            command=lambda: self.formula_text_widget.delete("1.0", tk.END)
        )
        clear_btn.grid(row=0, column=3, padx=(0, 20))
        
        config_frame.grid_columnconfigure(1, weight=1)
        
        # ===== MAIN CONTENT FRAME =====
        content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_frame.grid(row=5, column=0, columnspan=7, sticky="nsew", pady=(10, 0))
        main_frame.grid_rowconfigure(5, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        
        # ===== LEFT SIDE: TEST WORDS =====
        left_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left_frame.grid_rowconfigure(1, weight=1)
        
        words_label = ctk.CTkLabel(left_frame, text="Test Words:", font=("Arial", 12, "bold"))
        words_label.grid(row=0, column=0, sticky="w")
        
        # Test words listbox with scrollbar
        listbox_frame = ctk.CTkFrame(left_frame)
        listbox_frame.grid(row=1, column=0, sticky="nsew")
        listbox_frame.grid_rowconfigure(0, weight=1)
        listbox_frame.grid_columnconfigure(0, weight=1)
        
        self.test_words_listbox = tk.Listbox(listbox_frame, height=20, width=30)
        self.test_words_listbox.grid(row=0, column=0, sticky="nsew")
        self.test_words_listbox.bind('<<ListboxSelect>>', self.on_word_select)
        
        scrollbar = ctk.CTkScrollbar(listbox_frame, command=self.test_words_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.test_words_listbox.config(yscrollcommand=scrollbar.set)
        
        # Generate initial test words
        self.generate_test_words()
        
        # ===== RIGHT SIDE: RUN AND RESULTS =====
        right_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.grid_rowconfigure(3, weight=1)
        
        # Test word input
        word_label = ctk.CTkLabel(right_frame, text="Selected/Custom Test Word:", font=("Arial", 11, "bold"))
        word_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.word_input = ctk.CTkEntry(right_frame, width=300, placeholder_text="Enter word or select from list")
        self.word_input.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        # Run button
        run_button = ctk.CTkButton(
            right_frame,
            text="Run Formula",
            width=150,
            height=40,
            font=("Arial", 14, "bold"),
            command=self.run_formula
        )
        run_button.grid(row=2, column=0, pady=(0, 10))
        
        # Result section
        result_label = ctk.CTkLabel(right_frame, text="Result:", font=("Arial", 12, "bold"))
        result_label.grid(row=4, column=0, sticky="w", pady=(10, 5))
        
        self.result_text = ctk.CTkTextbox(right_frame, height=200, wrap="word", state="disabled")
        self.result_text.grid(row=5, column=0, sticky="nsew")
        right_frame.grid_rowconfigure(5, weight=1)
    
    def insert_symbol(self, symbol):
        """Insert a symbol at cursor position"""
        self.formula_text_widget.insert(tk.END, symbol)
    
    def generate_test_words(self):
        """Generate all words from empty string to length 7 with current alphabet"""
        try:
            alphabet_input = self.alphabet_input.get().strip()
            alphabet = sorted(list(set(s.strip() for s in alphabet_input.split(','))))
            
            self.test_words = [""]  # Start with empty string
            
            # Generate words of length 1 to 7
            for length in range(1, 8):
                for combo in product(alphabet, repeat=length):
                    self.test_words.append("".join(combo))
            
            # Update listbox
            self.test_words_listbox.delete(0, tk.END)
            for word in self.test_words:
                display_word = word if word else "(empty)"
                self.test_words_listbox.insert(tk.END, display_word)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate test words: {e}")
    
    def on_word_select(self, event):
        """Handle selection from test words listbox"""
        selection = self.test_words_listbox.curselection()
        if selection:
            idx = selection[0]
            word = self.test_words[idx]
            self.word_input.delete(0, tk.END)
            self.word_input.insert(0, word)
    
    def run_formula(self):
        """Parse and run the MSO formula on the test word"""
        try:
            formula = self.formula_text_widget.get("1.0", tk.END).strip()
            word = self.word_input.get().strip()
            alphabet_input = self.alphabet_input.get().strip()
            
            if not formula:
                messagebox.showerror("Error", "Please enter a formula")
                return
            
            if not word:
                messagebox.showerror("Error", "Please enter a test word")
                return
            
            # Parse alphabet
            try:
                alphabet = set(alphabet_input.split(','))
                alphabet = {s.strip() for s in alphabet}
            except:
                messagebox.showerror("Error", "Invalid alphabet format")
                return
            
            # Validate word characters
            for char in word:
                if char not in alphabet:
                    messagebox.showerror("Error", f"Character '{char}' not in alphabet: {alphabet}")
                    return
            
            # Calculate k (number of variables in formula)
            k = self.count_variables(formula)
            
            # Create parser and build automaton
            parser = MSO_Parser(alphabet, k)
            ast = parser.build_ast(formula)
            automaton = parser.build_automaton(ast)
            
            # Run the word on the automaton
            result = automaton.nfa_run(word)
            
            # Display result
            self.display_result(formula, word, result, alphabet)
            
        except Exception as e:
            self.display_error(str(e))
    
    def count_variables(self, formula):
        """Count the number of variables in the formula to determine k"""
        import re
        
        # Count first-order variables (lowercase)
        first_order = set(re.findall(r'\b[a-z]\b', formula))
        # Count second-order variables (uppercase)
        second_order = set(re.findall(r'\b[A-Z]\b', formula))
        
        total = len(first_order) + len(second_order)
        return max(total, 1)  # At least k=1
    
    def display_result(self, formula, word, result, alphabet):
        """Display the result in a formatted way"""
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", tk.END)
        
        result_text = f"""
Formula: {formula}

Test Word: '{word}'
Alphabet: {', '.join(sorted(alphabet))}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Result: {'✓ ACCEPTED' if result else '✗ REJECTED'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        self.result_text.insert(tk.END, result_text)
        self.result_text.configure(state="disabled")
        
        # Change text color based on result
        if result:
            self.result_text.tag_config("accepted", foreground="lime")
            self.result_text.tag_add("accepted", "13.0", "13.20")
        else:
            self.result_text.tag_config("rejected", foreground="red")
            self.result_text.tag_add("rejected", "13.0", "13.20")
    
    def display_error(self, error_msg):
        """Display error message"""
        self.result_text.configure(state="normal")
        self.result_text.delete("1.0", tk.END)
        
        error_text = f"""
ERROR:

{error_msg}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Make sure your formula is well-formed and all variables are properly quantified.
"""
        
        self.result_text.insert(tk.END, error_text)
        self.result_text.configure(state="disabled")
        self.result_text.tag_config("error", foreground="red")
        self.result_text.tag_add("error", "1.0", "1.10")


if __name__ == "__main__":
    root = ctk.CTk()
    app = MSO_GUI(root)
    root.mainloop()
