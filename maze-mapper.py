import tkinter as tk
from tkinter import ttk
import math
import numpy as np

class Cell():
    "Cell represents the state of a single square unit in the maze."
    EMPTY = 0
    EXPLORED = 1
    SPINNER = 2
    ENDFLAG = 3

class Boundary():
    """Boundary represents an edge of a single cell in a maze."""
    EMPTY = 0
    WALL = 1
    DOOR = 2
    ENDFLAG = 3


rotation = {
    0: np.array(((1, 0), (0, 1)), dtype=int),
    90: np.array(((0, 1), (-1, 0)), dtype=int),
    180: np.array(((-1, 0), (0, -1)), dtype=int),
    270: np.array(((0, -1), (1, 0)), dtype=int)}

class Model:
    """Model tracks the total state of a maze, including player and cursor position.

    Model advises the View about updated state.
    """
    def __init__(self, rows, cols):
        "Initialize mazeitems (walls and floors), player, and cursor."
        self.maze = np.zeros((rows * 2 + 1, cols * 2 + 1),
                             dtype="O")
        self.cursor_loc = np.array((0, 0), dtype=int)
        self.player_loc = np.array((0, 0), dtype=int)
        self.player_dir = np.array((-1, 0), dtype=int)
        self.player_bounds = (rows * 2, cols * 2)
        self.rows = rows
        self.cols = cols
        self.maze[1::2,1::2] = Cell.EMPTY
        self.maze[0::2,1::2] = Boundary.EMPTY
        self.maze[1::2,0::2] = Boundary.EMPTY
        self.view = None

    def rotate_player(self, rot):
        "Rotate the player.  rot is one of 0, 90, 180, or 270."
        self.player_dir = self.player_dir @ rotation[rot]
        self.view.adjust_player()

    def advance_player(self, steps):
        "Advance the player by a number of squares."
        self.player_loc = (self.player_loc + steps * self.player_dir) % self.player_bounds
        self.view.adjust_player()

    def move_cursor(self, vec):
        "Move the cursor by a vectored amount."
        self.cursor_loc = (self.cursor_loc + vec) % self.player_bounds
        self.view.adjust_cursor()

    def rotate_wall(self, vec):
        "Change the state of a wall.  vec specifies the wall as an offset from the cursor."
        wpos = tuple((self.cursor_loc + (1,1) + vec) % self.maze.shape)
        self.maze[wpos[1], wpos[0]] = (self.maze[wpos[1], wpos[0]] + 1) % Boundary.ENDFLAG
        self.view.adjust_mazeitem(wpos[1], wpos[0])
        #TODO remove
        self.view.adjust_all()

class Controller:
    """Controller accepts input from the user and passes it to the model."""
    def __init__(self, model, view):
        self.model = model
        self.view = view
        model.view = view
        view.link_model(model)
        view.adjust_all()
        view.bind("<j>", lambda event: model.rotate_player(270))
        view.bind("<l>", lambda event: model.rotate_player(90))
        view.bind("<k>", lambda event: model.advance_player(2))
        view.bind("<i>", lambda event: model.advance_player(2))
        view.bind("<m>", lambda event: model.advance_player(-2))
        view.bind("<Up>", lambda event: model.move_cursor((0, -2)))
        view.bind("<Down>", lambda event: model.move_cursor((0, +2)))
        view.bind("<Left>", lambda event: model.move_cursor((-2, 0)))
        view.bind("<Right>", lambda event: model.move_cursor((+2, 0)))
        view.bind("<Shift-Up>", lambda event: model.rotate_wall((0, -1)))
        view.bind("<Shift-Down>", lambda event: model.rotate_wall((0, +1)))
        view.bind("<Shift-Left>", lambda event: model.rotate_wall((-1, 0)))
        view.bind("<Shift-Right>", lambda event: model.rotate_wall((+1, 0)))
        view.bind("<q>", lambda event: root.quit())
        view.bind("<X>", lambda event: root.destroy())


class View2D(tk.Canvas):
    """View displays the state of the maze and player using widgets on a tk.Canvas."""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.model = None
        self.scale = 20.
        self.wallsize = self.scale / 10
        self.colors = {'floor': 'gray95',
                       'emptywall': 'gray90',
                       'wall': 'black',
                       'door': 'brown',
                       'cursor': 'red',
                       'player': 'blue'}

    def delete_all_items(self):
        self.delete(*self.find_all())

    def link_model(self, model):
        self.model = model
        self.mazeitems = np.zeros(model.maze.shape, dtype="O")
        rows, cols = model.maze.shape
        for i in range(cols):
            for j in range(rows):
                itemtype = i % 2 + j % 2
                if itemtype == 2:
                    self.mazeitems[i,j] = self.create_rectangle(0, 0, 0, 0, fill=self.colors['floor'], width=0)
                elif itemtype == 1:
                    self.mazeitems[i,j] = self.create_rectangle(0, 0, 0, 0, fill=self.colors['wall'], width=0)
        self.player_shape = self.create_polygon(0, 0, fill = self.colors['player'])
        self.cursor_shape = self.create_oval(0, 0, 0, 0, fill = self.colors['cursor'])

    def set_mazeitem_color(self, i, j, color):
        self.itemconfigure(self.mazeitems[i, j], fill=color)

    def adjust_all(self):
        self.adjust_cursor()
        self.adjust_player()
        rows, cols = self.mazeitems.shape
        for i in range(cols):
            for j in range(rows):
                self.adjust_mazeitem(i, j)

    def adjust_cursor(self):
        "Orient and place cursor widget."
        # TODO handle view rotation and recentering
        pos = (self.model.cursor_loc + (1., 1.)) * self.scale / 2
        c1 = pos + np.array((-.2, -.2)) * self.scale
        c2 = pos + np.array((+.2, +.2)) * self.scale
        self.coords(self.cursor_shape, *c1, *c2)

    def adjust_player(self):
        "Orient and place player widget."
        # TODO handle view rotation and recentering
        pos = (self.model.player_loc + (1., 1.)) * self.scale / 2
        d1 = self.model.player_dir
        d2 = self.model.player_dir @ rotation[90]
        c1 = pos + self.scale * 0.4 * d1
        c2 = pos + self.scale * (-0.4 * d1 + 0.2 * d2)
        c3 = pos + self.scale * (-0.4 * d1 - 0.2 * d2)
        self.coords(self.player_shape, *c1, *c2, *c3)

    def adjust_mazeitem(self, i, j):
        "Orient, place, and recolor mazeitem (wall or floor)."
        # TODO handle view rotation and recentering
        x1 = (j // 2) * self.scale + self.wallsize / 2
        x2 = x1 + self.scale - self.wallsize
        y1 = (i // 2) * self.scale + self.wallsize / 2
        y2 = y1 + self.scale - self.wallsize
        if i % 2 == 0:
            y1, y2 = y1 - self.wallsize, y1
        if j % 2 == 0:
            x1, x2 = x1 - self.wallsize, x1
        self.coords(self.mazeitems[i, j], x1, y1, x2, y2)
        status = model.maze[i, j]
        if status == Boundary.EMPTY:
            color = self.colors['emptywall']
        elif status == Boundary.WALL:
            color = self.colors['wall']
        elif status == Boundary.DOOR:
            color = self.colors['door']
        self.set_mazeitem_color(i, j, color)



root = tk.Tk()
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

view = View2D(root, width=500, height=500, bg='white')
view.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
view.pack()
view.focus_set()

model = Model(22, 22)
controller = Controller(model, view)


root.mainloop()
