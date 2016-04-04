from tkinter import font
import tkinter as tk
import tkinter.ttk as ttk
import sys

players = range(20)
LARGE_FONT = ('Helvetica', '36')
REGULAR_FONT = ('Helvetica', '16')


class Rankings(ttk.Labelframe):
    def __init__(self, master=None, *args, **kwargs):
        super(Rankings, self).__init__(master, *args, **kwargs)
        self.config(text="Ranking")
        self.create_widgets()

    def create_widgets(self):
        for player in players:
            line = ttk.Frame(self, style='Red.TFrame')
            pos = ttk.Label(line, text=str(player), anchor=tk.NW)
            name = ttk.Label(line, text='Aster Van Broekhoven El Morador Di Akk', anchor=tk.NW)
            points = ttk.Label(line, text=str(player), anchor=tk.NW)
            pos.pack(fill=tk.X, expand=1, side=tk.LEFT)
            name.pack(fill=tk.X, expand=1, side=tk.LEFT)
            points.pack(fill=tk.X, expand=1, side=tk.RIGHT)
            line.pack(fill=tk.BOTH, expand=1)


class Upcoming(ttk.Labelframe):
    def __init__(self, master=None):
        super(Upcoming, self).__init__(master)
        self.config(text="Upcoming contenders")
        self.create_widgets()

    def create_widgets(self):
        for index, player in enumerate(players):
            w = ttk.Label(self, text=str(player), anchor=tk.NW)
            if index < 3:
                w.configure(font=LARGE_FONT)
            else:
                w.configure(font=REGULAR_FONT)
            w.pack(fill=tk.X, expand=1)


class CurrentFight(ttk.LabelFrame):
    def __init__(self, master=None, *args, **kwargs):
        super(CurrentFight, self).__init__(master, *args, **kwargs)
        self.config(text="Now fighting", relief='raised')
        self.create_widgets()

    def create_widgets(self):
        # Use anchor=tl.CENTER and fill=tk.X to center vertically
        king = ttk.Label(self, text="Krist Martens", anchor=tk.CENTER, font=LARGE_FONT, foreground='red')
        king.pack(fill=tk.BOTH, expand=1, side=tk.LEFT)

        king_button_frame = ttk.Frame(master=king, style="Red.TFrame")
        king_button_frame.pack(side=tk.BOTTOM, fill=tk.X)
        button_king_add_point = ttk.Button(king_button_frame, text="+1")
        button_king_add_point.pack(side=tk.LEFT, expand=1, fill=tk.X)
        button_king_substract_point = ttk.Button(king_button_frame, text="-1")
        button_king_substract_point.pack(side=tk.LEFT, expand=1, fill=tk.X)
        button_king_move_to_queue = ttk.Button(king_button_frame, text="Move to queue")
        button_king_move_to_queue.pack(side=tk.LEFT, expand=1, fill=tk.X)

        vs = ttk.Label(self, text="Versus", anchor=tk.CENTER)
        vs.pack(fill=tk.BOTH, side=tk.LEFT, expand=1)

        contender = ttk.Label(self, text="Aster Berkhof", font=LARGE_FONT, foreground='blue', anchor=tk.CENTER)
        contender.pack(fill=tk.BOTH, expand=1, side=tk.LEFT)

        contender_button_frame = ttk.Frame(master=contender)
        contender_button_frame.pack(side=tk.BOTTOM, fill=tk.X)
        button_contender_add_point = ttk.Button(contender_button_frame, text="+1")
        button_contender_add_point.pack(side=tk.LEFT, expand=1, fill=tk.X)
        button_contender_substract_point = ttk.Button(contender_button_frame, text="-1")
        button_contender_substract_point.pack(side=tk.LEFT, expand=1, fill=tk.X)
        button_contender_back_to_queue = ttk.Button(contender_button_frame, text="Back to queue")
        button_contender_back_to_queue.pack(side=tk.LEFT, expand=1, fill=tk.X)
        button_contender_make_king = ttk.Button(contender_button_frame, text="Make king")
        button_contender_make_king.pack(side=tk.LEFT, expand=1, fill=tk.X)



class Timer(ttk.Frame):
    def __init__(self, master=None, *args, **kwargs):
        super(Timer, self).__init__(master, *args, **kwargs)
        self.create_widgets()

    def create_widgets(self):
        self.display = ttk.Label(self)
        self.display.pack()


class Scoreboard(tk.Tk):
    def __init__(self, master=None):
        super(Scoreboard, self).__init__(master)

        self.clock = 6000
        self.clock_display = tk.StringVar()

        self.grid()
        self.create_frames()
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

    def create_frames(self):
        self.right = ttk.Frame(master=self)

        self.current_fight = CurrentFight(master=self.right)
        self.current_fight.pack(fill=tk.BOTH, expand=1)

        self.upcoming = Upcoming(master=self.right)
        self.upcoming.pack(fill=tk.BOTH, expand=1)

        self.timer = Timer(master=self.right)
        self.timer.pack()
        self.timer.display.config(textvariable=self.clock_display)

        self.rankings = Rankings(master=self)
        self.rankings.grid(column=0, row=0, rowspan=3, sticky=tk.NW)

        self.right.grid(column=1, row=0, sticky='news')

        self.tick_tock()

    def catch_keypress(self, key):
        print(key.keycode)
        if key.keycode == 27:
            # ESC pressed
            self.destroy()

    def tick_tock(self):
        self.clock -= 1
        self.clock_display.set(str(self.clock))
        self.after(1000, self.tick_tock)


app = Scoreboard()

style = ttk.Style(master=app)
style.configure('.', font=REGULAR_FONT, foreground='black')
style.configure('TLabel', font=REGULAR_FONT)
style.configure('Red.TFrame', background='red')
style.configure('Red.TLabel', background='red')
style.configure('TLabelframe', padding=12)
style.configure('TLabelframe.Label', foreground='black')

app.attributes("-fullscreen", True)
app.configure(bg='yellow')

app.bind_all("<Key>", app.catch_keypress)

app.mainloop()
