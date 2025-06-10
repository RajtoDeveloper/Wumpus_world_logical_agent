from pyswip import Prolog
import tkinter as tk
from tkinter import messagebox, simpledialog, Toplevel, font
from PIL import Image, ImageTk
import time

class WumpusWorldGUI:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1000x700")
        self.root.title("Wumpus World Game")
        self.setup_custom_styles()
        self.action_log = []
        self.show_rules()
        
    def setup_custom_styles(self):
        # Custom color scheme
        self.bg_color = "#f0f2f5"
        self.cell_bg = "#ffffff"
        self.agent_color = "#4fc3f7"
        self.gold_color = "#ffd700"
        self.danger_color = "#ff5252"
        self.safe_color = "#66bb6a"
        self.text_color = "#333333"
        self.log_bg = "#2c3e50"
        self.log_text = "#ecf0f1"
        
        # Configure root window
        self.root.configure(bg=self.bg_color)
        
    def show_rules(self):
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Rules frame
        rules_frame = tk.Frame(self.root, bg=self.bg_color, padx=20, pady=20)
        rules_frame.pack(expand=True, fill=tk.BOTH)
        
        # Rules text
        rules_text = """🌍 Wumpus World Game Rules 🌍

1. The world is a 4x4 grid
2. You start at (1,1) facing right
3. Dangers:
   - Wumpus: Kills you if you enter its room (stench nearby)
   - Pits: Kill you if you fall in (breeze nearby)
4. Goal: Find the gold and return to (1,1) to win
5. Actions:
   - Move to adjacent squares
   - Shoot arrow (one direction, costs 10 points)
   - Grab gold when you find it
   - Climb out at (1,1) with gold to win

🕵️‍♀️ Percepts:
- Stench: Wumpus nearby
- Breeze: Pit nearby
- Glitter: Gold in current room
- Scream: Wumpus killed
"""
        rules_label = tk.Label(rules_frame, text=rules_text, justify=tk.LEFT, 
                             font=('Poppins', 12), bg=self.bg_color, fg=self.text_color)
        rules_label.pack(pady=20)
        
        # Start button with modern style
        ok_btn = tk.Button(rules_frame, text="START GAME", command=self.start_game, 
                          font=('Poppins', 14, 'bold'), bg="#4CAF50", fg="white",
                          relief=tk.FLAT, bd=0, padx=30, pady=10,
                          activebackground="#2E7D32", activeforeground="white")
        ok_btn.pack(pady=20)
        self.create_button_hover_effect(ok_btn, "#4CAF50", "#2E7D32")
        
    def start_game(self):
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        self.root.title("Wumpus Game Logical Agent")
        self.prolog = Prolog()
        self.setup_prolog()
        self.create_widgets()
        self.update_display()
        
    def setup_prolog(self):
        # Initialize dynamic predicates
        self.prolog.assertz(":- dynamic([breeze/1, stench/1, glitter/1, wumpus_location/1, pit_location/1, gold_location/1, agent_location/1, timer/1, score/1, wumpus_final_location/1, has_gold/1, wumpus_dead/1])")
        
        # Add adjacent facts
        for x in range(1, 5):
            for y in range(1, 5):
                if x < 4:
                    self.prolog.assertz(f"adjacent([{x},{y}], [{x+1},{y}])")
                if x > 1:
                    self.prolog.assertz(f"adjacent([{x},{y}], [{x-1},{y}])")
                if y < 4:
                    self.prolog.assertz(f"adjacent([{x},{y}], [{x},{y+1}])")
                if y > 1:
                    self.prolog.assertz(f"adjacent([{x},{y}], [{x},{y-1}])")
        
        # Initialize game elements
        self.prolog.assertz("gold_location([3,3])")
        self.prolog.assertz("wumpus_location([4,4])")
        self.prolog.assertz("pit_location([1,4])")
        self.prolog.assertz("pit_location([3,1])")
        self.prolog.assertz("agent_location([1,1])")
        self.prolog.assertz("wumpus_final_location([-1,-1])")
        self.prolog.assertz("score(30)")
        self.prolog.assertz("timer(0)")
        self.prolog.assertz("has_gold(0)")
        self.prolog.assertz("wumpus_dead(0)")
        
        # Initialize percepts for starting position
        self.update_percepts(1, 1)
        
    def create_widgets(self):
        # Main container
        main_container = tk.Frame(self.root, bg=self.bg_color)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Left panel (game board)
        left_panel = tk.Frame(main_container, bg=self.bg_color)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Score and timer display (top right)
        score_frame = tk.Frame(left_panel, bg=self.bg_color)
        score_frame.pack(anchor=tk.NE, pady=10)
        
        self.score_label = tk.Label(score_frame, text="Score: 30", 
                                  font=('Poppins', 12, 'bold'), 
                                  bg=self.bg_color, fg=self.text_color)
        self.score_label.pack(side=tk.LEFT, padx=10)
        
        self.timer_label = tk.Label(score_frame, text="Moves: 0", 
                                  font=('Poppins', 12, 'bold'), 
                                  bg=self.bg_color, fg=self.text_color)
        self.timer_label.pack(side=tk.LEFT, padx=10)
        
        # Game board
        self.board_frame = tk.Frame(left_panel, bg=self.bg_color)
        self.board_frame.pack(pady=20)
        
        self.cells = {}
        for y in range(4, 0, -1):  # Rows from 4 to 1 (top to bottom)
            for x in range(1, 5):  # Columns from 1 to 4
                cell = tk.Button(self.board_frame, text="", width=8, height=4,
                               font=('Poppins', 10), relief=tk.RAISED, bd=2,
                               command=lambda x=x, y=y: self.make_move(x, y))
                cell.grid(row=4-y, column=x-1, padx=5, pady=5)
                self.cells[(x, y)] = cell
                self.style_cell_button(cell)
        
        # Information display
        self.info_frame = tk.Frame(left_panel, bg=self.bg_color)
        self.info_frame.pack(pady=10)
        
        self.percept_label = tk.Label(self.info_frame, text="Percepts: ", 
                                    font=('Poppins', 12), bg=self.bg_color, fg=self.text_color)
        self.percept_label.pack()
        
        self.wumpus_label = tk.Label(self.info_frame, text="Wumpus: Alive", 
                                   font=('Poppins', 12), bg=self.bg_color, fg=self.text_color)
        self.wumpus_label.pack()
        
        # Control buttons
        self.control_frame = tk.Frame(left_panel, bg=self.bg_color)
        self.control_frame.pack(pady=20)
        
        buttons = [
            ("Shoot Arrow", self.shoot_arrow),
            ("Grab Gold", self.grab_gold),
            ("Climb Out", self.climb_out),
            ("Display Rules", self.show_rules_popup),
            ("Restart", self.restart_game),
            ("Quit", self.quit_game)
        ]
        
        for text, command in buttons:
            btn = tk.Button(self.control_frame, text=text, command=command,
                          font=('Poppins', 10), bg="#3498db", fg="white",
                          relief=tk.FLAT, padx=15, pady=5)
            btn.pack(side=tk.LEFT, padx=5)
            self.create_button_hover_effect(btn, "#3498db", "#2980b9")
        
        # Right panel (action log)
        right_panel = tk.Frame(main_container, bg=self.log_bg, width=250)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10,0))
        
        log_title = tk.Label(right_panel, text="ACTION LOG", 
                           font=('Poppins', 12, 'bold'), 
                           bg=self.log_bg, fg=self.log_text)
        log_title.pack(pady=10)
        
        self.log_text = tk.Text(right_panel, height=30, width=30, 
                              font=('Poppins', 10), bg=self.log_bg, 
                              fg=self.log_text, bd=0, highlightthickness=0)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10)
        self.log_text.config(state=tk.DISABLED)
        
    def style_cell_button(self, button):
        button.config(
            bg=self.cell_bg,
            activebackground="#e0e0e0",
            relief=tk.RAISED,
            bd=2,
            highlightbackground="#bdbdbd",
            highlightcolor="#bdbdbd",
            highlightthickness=2
        )
        
    def create_button_hover_effect(self, button, color_from, color_to):
        button.bind("<Enter>", lambda e: button.config(bg=color_to))
        button.bind("<Leave>", lambda e: button.config(bg=color_from))
        
    def add_log_entry(self, message):
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.action_log.append(log_entry)
        if len(self.action_log) > 50:  # Limit log size
            self.action_log.pop(0)
            
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        
    def update_percepts(self, x, y):
        # Clear old percepts
        self.prolog.retractall(f"breeze([{x},{y}])")
        self.prolog.retractall(f"stench([{x},{y}])")
        self.prolog.retractall(f"glitter([{x},{y}])")
        
        # Check for adjacent pits (breeze)
        adjacent = list(self.prolog.query(f"adjacent([{x},{y}], [A,B]), pit_location([A,B])"))
        if adjacent:
            self.prolog.assertz(f"breeze([{x},{y}])")
            self.add_log_entry(f"Sensed: Breeze at ({x},{y})")
        
        # Check for adjacent wumpus (stench)
        if not list(self.prolog.query("wumpus_dead(1)")):  # Only if Wumpus is alive
            adjacent = list(self.prolog.query(f"adjacent([{x},{y}], [A,B]), wumpus_location([A,B])"))
            if adjacent:
                self.prolog.assertz(f"stench([{x},{y}])")
                self.add_log_entry(f"Sensed: Stench at ({x},{y})")
        
        # Check for gold (glitter)
        if list(self.prolog.query(f"gold_location([{x},{y}])")) and not list(self.prolog.query("has_gold(1)")):
            self.prolog.assertz(f"glitter([{x},{y}])")
            self.add_log_entry(f"Sensed: Glitter at ({x},{y})")
        
    def update_display(self):
        # Get current game state from Prolog
        try:
            agent_loc = list(self.prolog.query("agent_location([X,Y])"))[0]
            x, y = agent_loc["X"], agent_loc["Y"]
        except:
            return
        
        # Update percepts for current location
        self.update_percepts(x, y)
        
        # Get current percepts
        percepts = []
        percept_colors = []
        
        if list(self.prolog.query(f"breeze([{x},{y}])")):
            percepts.append("Breeze")
            percept_colors.append(self.danger_color)
        if list(self.prolog.query(f"stench([{x},{y}])")):
            percepts.append("Stench")
            percept_colors.append(self.danger_color)
        if list(self.prolog.query(f"glitter([{x},{y}])")):
            percepts.append("Glitter")
            percept_colors.append(self.gold_color)
        
        # Update percept display
        if percepts:
            percept_text = "Percepts: " + ", ".join(percepts)
            color = self.danger_color if self.danger_color in percept_colors else self.gold_color
        else:
            percept_text = "Percepts: Safe"
            color = self.safe_color
            
        self.percept_label.config(text=percept_text, fg=color)
        
        # Update Wumpus status
        wumpus_status = "Wumpus: " + ("Dead" if list(self.prolog.query("wumpus_dead(1)")) else "Alive")
        self.wumpus_label.config(text=wumpus_status)
        
        # Update score and timer
        score = list(self.prolog.query("score(S)"))[0]["S"]
        timer = list(self.prolog.query("timer(T)"))[0]["T"]
        self.score_label.config(text=f"Score: {score}")
        self.timer_label.config(text=f"Moves: {timer}")
        
        # Reset all cells
        for (cell_x, cell_y), button in self.cells.items():
            button.config(
                bg=self.cell_bg,
                text="",
                relief=tk.RAISED,
                highlightbackground="#bdbdbd",
                highlightcolor="#bdbdbd",
                highlightthickness=2
            )
            
            # Current agent position
            if cell_x == x and cell_y == y:
                button.config(
                    bg=self.agent_color,
                    text="Agent",
                    relief=tk.SUNKEN,
                    highlightbackground="#0288d1",
                    highlightcolor="#0288d1",
                    highlightthickness=3
                )
            # Gold in current cell
            elif cell_x == x and cell_y == y and list(self.prolog.query(f"gold_location([{x},{y}])")) and not list(self.prolog.query("has_gold(1)")):
                button.config(
                    bg=self.gold_color,
                    text="Gold",
                    highlightbackground="#ffc400",
                    highlightcolor="#ffc400",
                    highlightthickness=3
                )
        
        # Highlight adjacent cells
        adjacent = list(self.prolog.query(f"adjacent([{x},{y}], [A,B])"))
        for adj in adjacent:
            adj_x, adj_y = adj["A"], adj["B"]
            if (adj_x, adj_y) in self.cells:
                # Only highlight if it's not the current agent position
                if not (adj_x == x and adj_y == y):
                    self.cells[(adj_x, adj_y)].config(
                        bg=self.safe_color,
                        highlightbackground="#66bb6a",
                        highlightcolor="#66bb6a",
                        highlightthickness=2
                    )
    
    def make_move(self, x, y):
        # Get current agent location
        agent_loc = list(self.prolog.query("agent_location([X,Y])"))[0]
        ax, ay = agent_loc["X"], agent_loc["Y"]
        
        # Check if the clicked cell is adjacent to current position
        adjacent = list(self.prolog.query(f"adjacent([{ax},{ay}], [{x},{y}])"))
        if not adjacent:
            messagebox.showerror("Invalid Move", "You can only move to adjacent squares!")
            return
        
        # Execute the move
        self.prolog.retractall(f"agent_location([{ax},{ay}])")
        self.prolog.assertz(f"agent_location([{x},{y}])")
        self.add_log_entry(f"Moved to ({x},{y})")
        
        # Update timer and score
        timer = list(self.prolog.query("timer(T)"))[0]["T"]
        self.prolog.retractall("timer(_)")
        self.prolog.assertz(f"timer({timer + 1})")
        
        score = list(self.prolog.query("score(S)"))[0]["S"]
        self.prolog.retractall("score(_)")
        self.prolog.assertz(f"score({score - 1})")
        
        # Check for pit
        if list(self.prolog.query(f"pit_location([{x},{y}])")):
            self.cells[(x, y)].config(
                bg="black",
                fg="white",
                text="Pit",
                highlightbackground="#000000",
                highlightcolor="#000000"
            )
            self.add_log_entry("Fell into a pit! Game over.")
            messagebox.showinfo("Game Over", "You fell into a pit! Game over.")
            self.root.destroy()
            return
            
        # Check for wumpus
        if list(self.prolog.query(f"wumpus_location([{x},{y}])")) and not list(self.prolog.query("wumpus_dead(1)")):
            self.cells[(x, y)].config(
                bg="red",
                text="Wumpus",
                highlightbackground="#d32f2f",
                highlightcolor="#d32f2f"
            )
            self.add_log_entry("Eaten by Wumpus! Game over.")
            messagebox.showinfo("Game Over", "You were eaten by the Wumpus! Game over.")
            self.root.destroy()
            return
        
        self.update_display()
        
    def shoot_arrow(self):
        # Get current location
        agent_loc = list(self.prolog.query("agent_location([X,Y])"))[0]
        x, y = agent_loc["X"], agent_loc["Y"]
        
        # Get possible directions to shoot
        directions = []
        if x < 4: directions.append(("right", [x+1, y]))
        if x > 1: directions.append(("left", [x-1, y]))
        if y < 4: directions.append(("up", [x, y+1]))
        if y > 1: directions.append(("down", [x, y-1]))
        
        # Ask user for direction
        direction = simpledialog.askstring("Shoot Arrow", 
                                        f"Enter direction to shoot ({', '.join([d[0] for d in directions])}):")
        
        if direction and direction.lower() in [d[0] for d in directions]:
            target = [d[1] for d in directions if d[0] == direction.lower()][0]
            wumpus_loc = list(self.prolog.query("wumpus_location([X,Y])"))[0]
            
            if target == [wumpus_loc["X"], wumpus_loc["Y"]]:
                self.add_log_entry("Shot arrow and killed Wumpus!")
                messagebox.showinfo("Success!", "You killed the Wumpus!")
                self.prolog.retractall("wumpus_dead(_)")
                self.prolog.assertz("wumpus_dead(1)")
                self.update_display()
            else:
                self.add_log_entry("Shot arrow and missed!")
                messagebox.showinfo("Missed", "Your arrow missed the Wumpus!")
                # Deduct points for shooting
                score = list(self.prolog.query("score(S)"))[0]["S"]
                self.prolog.retractall("score(_)")
                self.prolog.assertz(f"score({score - 10})")
                self.update_display()
    
    def grab_gold(self):
        agent_loc = list(self.prolog.query("agent_location([X,Y])"))[0]
        x, y = agent_loc["X"], agent_loc["Y"]
        
        if list(self.prolog.query(f"gold_location([{x},{y}])")) and not list(self.prolog.query("has_gold(1)")):
            self.prolog.retractall("has_gold(_)")
            self.prolog.assertz("has_gold(1)")
            self.prolog.retractall(f"glitter([{x},{y}])")
            
            # Update score
            score = list(self.prolog.query("score(S)"))[0]["S"]
            self.prolog.retractall("score(_)")
            self.prolog.assertz(f"score({score + 500})")
            
            self.add_log_entry("Gold grabbed!")
            messagebox.showinfo("Success!", "You've grabbed the gold! Now return to (1,1) to climb out.")
            self.update_display()
        else:
            self.add_log_entry("Tried to grab gold but none here!")
            messagebox.showinfo("No Gold", "There's no gold here to grab!")
    
    def climb_out(self):
        agent_loc = list(self.prolog.query("agent_location([X,Y])"))[0]
        x, y = agent_loc["X"], agent_loc["Y"]
        
        if x == 1 and y == 1:
            if list(self.prolog.query("has_gold(1)")):
                score = list(self.prolog.query("score(S)"))[0]["S"]
                self.add_log_entry(f"Climbed out with gold! Final score: {score}")
                messagebox.showinfo("You Win!", f"You've successfully climbed out with the gold! Final score: {score}")
                self.root.destroy()
            else:
                self.add_log_entry("Tried to climb out without gold!")
                messagebox.showinfo("No Gold", "You need to have the gold to climb out!")
        else:
            self.add_log_entry("Tried to climb out from wrong location!")
            messagebox.showinfo("Wrong Location", "You can only climb out at the starting position (1,1)!")
        
    def restart_game(self):
        # Reinitialize the game
        self.prolog.retractall("breeze(_)")
        self.prolog.retractall("stench(_)")
        self.prolog.retractall("glitter(_)")
        self.prolog.retractall("agent_location(_)")
        self.prolog.retractall("timer(_)")
        self.prolog.retractall("score(_)")
        self.prolog.retractall("wumpus_final_location(_)")
        self.prolog.retractall("has_gold(_)")
        self.prolog.retractall("wumpus_dead(_)")
        
        self.prolog.assertz("agent_location([1,1])")
        self.prolog.assertz("wumpus_final_location([-1,-1])")
        self.prolog.assertz("score(30)")
        self.prolog.assertz("timer(0)")
        self.prolog.assertz("has_gold(0)")
        self.prolog.assertz("wumpus_dead(0)")
        
        self.action_log = []
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.add_log_entry("Game restarted")
        
        self.update_display()
    
    def show_rules_popup(self):
        rules_window = Toplevel(self.root)
        rules_window.title("Game Rules")
        rules_window.geometry("500x500")
        rules_window.configure(bg=self.bg_color)
        
        # Rules text
        rules_text = """🌍 Wumpus World Game Rules 🌍

1. The world is a 4x4 grid
2. You start at (1,1) facing right
3. Dangers:
   - Wumpus: Kills you if you enter its room (stench nearby)
   - Pits: Kill you if you fall in (breeze nearby)
4. Goal: Find the gold and return to (1,1) to win
5. Actions:
   - Move to adjacent squares
   - Shoot arrow (one direction, costs 10 points)
   - Grab gold when you find it
   - Climb out at (1,1) with gold to win

🕵️‍♀️ Percepts:
- Stench: Wumpus nearby
- Breeze: Pit nearby
- Glitter: Gold in current room
- Scream: Wumpus killed
"""
        rules_label = tk.Label(rules_window, text=rules_text, justify=tk.LEFT, 
                             font=('Poppins', 12), bg=self.bg_color, fg=self.text_color)
        rules_label.pack(pady=20, padx=20)
        
        # Close button
        close_btn = tk.Button(rules_window, text="Close", command=rules_window.destroy, 
                            font=('Poppins', 12), bg="#3498db", fg="white",
                            relief=tk.FLAT, padx=20, pady=5)
        close_btn.pack(pady=10)
        self.create_button_hover_effect(close_btn, "#3498db", "#2980b9")
        
    def quit_game(self):
        if messagebox.askyesno("Quit Game", "Are you sure you want to quit the game?"):
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    game = WumpusWorldGUI(root)
    root.mainloop()
