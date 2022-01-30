from enum import Flag
import tkinter as tk
from tkinter import ttk
import math

class Boundary(Flag):
    """Boundary represents an edge of a single cell in a maze."""
    BLANK = 0
    WALL = 1
    DOOR = 2
    
class Cell:
    """Cell is one square unit in the maze grid."""
    def __init__(self):
        # walls[0,1,2,3] are N, E, S, W walls respectively.
        self.borders = [Boundary.BLANK for _ in range(4)]
        pass
    def __repr__(self):
        return "Cell()"
    
class Maze:
    """Maze is a grid of cells with walls, doors, etc."""
    def __init__(self, xdim: int, ydim: int):
        self.xdim = xdim
        self.ydim = ydim
        self.cells = [Cell() for __ in range(xdim * ydim)]

    def get_cell(x: int, y: int):
        "Returns the cell at location x, y."
        if x < 0 or y < 0 or x >= self.xdim or y >= self.ydim:
            raise IndexError
        return self.cells[y * self.xdim + x]


def flatten_list(lst):
    """Flattens a list of lists, returning results as a list.

    Not recursive -- it flattens the top level only.
    """
    return [elt for sublst in lst for elt in sublst]

class MazeView2D(tk.Canvas):
    def __init__(self, parent, **kwargs):
        self.player_angle = 0
        self.player_x = 10
        self.player_y = 10
        self.dot_x = 10
        self.dot_y = 10
        self.maze = Maze(10,10)
        super().__init__(parent, **kwargs)
        self.bind("<j>", lambda event: self.rotate_player(-90))
        self.bind("<l>", lambda event: self.rotate_player(+90))
        self.bind("<k>", lambda event: self.advance_player(20))
        self.bind("<i>", lambda event: self.advance_player(20))
        self.bind("<Up>", lambda event: self.move_dot(0, -20))
        self.bind("<Down>", lambda event: self.move_dot(0, +20))
        self.bind("<Left>", lambda event: self.move_dot(-20, 0))
        self.bind("<Right>", lambda event: self.move_dot(+20, 0))
        self.bind("<q>", lambda event: root.quit)
        self.bind("<X>", lambda event: root.destroy)
        
        self.maze_squares = [self.create_rectangle(x*20, y*20, (x+1)*20, (y+1)*20, fill='white', outline='gray')
                             for x in range(self.maze.xdim) for y in range(self.maze.ydim)]
        self.player_shape = self.create_polygon(1, 1, fill='gray', outline='blue')
        self.change_player_coords()
        self.dot_shape = self.create_oval(1, 1, 2, 2, fill='gray', outline='red')
        self.change_dot_coords()
    
    def change_player_coords(self):
        player_pts = ((9., 0.), (-9., 5.), (-9., -5.))
        px, py, pa = self.player_x, self.player_y, self.player_angle
        grid_pts = ((px + (x * math.cos(pa) - y * math.sin(pa)),
                     py + (x * math.sin(pa) + y * math.cos(pa)))
                    for (x, y) in player_pts)
        self.coords(self.player_shape, *flatten_list(grid_pts))

    def change_dot_coords(self):
        dot_pts = ((-4., -4.), (+4., +4.))
        dx, dy = self.dot_x, self.dot_y
        grid_pts = ((dx, dy) for (x, y) in dot_pts)
        self.coords(self.dot_shape, *flatten_list(grid_pts))
        
    def rotate_player(self, angle):
        "Rotates player by angle (specified by degrees)."
        self.player_angle = (self.player_angle + angle * math.pi / 180) % (2 * math.pi)        
        self.change_player_coords()

    def move_player(self, x, y):
        "Moves player coordinates by an amount (x, y)."
        self.player_x += x
        self.player_y += y
        self.change_player_coords()

    def move_dot(self, x, y):
        "Moves dot coordinates by an amount (x, y)."
        self.dot_x += x
        self.dot_y += y
        self.change_dot_coords()
        
    def advance_player(self, amt):
        "Advances the player in its current direction by amt."
        self.move_player(amt * math.cos(self.player_angle),
                         amt * math.sin(self.player_angle))

root = tk.Tk()
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

mazeview = MazeView2D(root)
mazeview.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
mazeview.pack()
mazeview.focus_set()

root.mainloop()
