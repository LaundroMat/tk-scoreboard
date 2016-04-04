import configparser
import operator
from tkinter import font
import tkinter as tk
import tkinter.ttk as ttk
import sys

from contestant import Contestant

LARGE_FONT = ('Helvetica', '36')
REGULAR_FONT = ('Helvetica', '16')

class Rankings(ttk.Labelframe):
    def __init__(self, master=None, contestants=None, *args, **kwargs):
        super(Rankings, self).__init__(master, *args, **kwargs)
        self.config(text="Ranking")
        # self.create_widgets()
        self.update_ranking(contestants)

    def update_ranking(self, contestants):
        if contestants:
            # Drop children and rebuild
            for w in self.winfo_children():
                w.destroy()

            ranking = sorted(contestants.copy(), key=operator.attrgetter('score'), reverse=True)
            player_position = 1
            previous_score = ranking[0].score
            for player in ranking:
                if player.score < previous_score:
                    player_position += 1

                line = ttk.Frame(self)
                lbl_position = ttk.Label(line, text="{0}. ".format(str(player_position)), anchor=tk.NW)
                lbl_position.pack(fill=tk.X, side=tk.LEFT)
                lbl_name = ttk.Label(line, text=player.name, anchor=tk.W)
                lbl_name.pack(fill=tk.X, expand=1, side=tk.LEFT)
                lbl_score = ttk.Label(line, text=str(player.score), anchor=tk.NE, padding=[5, 0, 0, 0])
                lbl_score.pack(fill=tk.X, expand=1, side=tk.RIGHT)
                line.pack(fill=tk.BOTH, expand=1)

                previous_score = player.score


class Upcoming(ttk.Labelframe):
    def __init__(self, master=None, contestants=[]):
        super(Upcoming, self).__init__(master)
        self.config(text="Upcoming contenders")
        self.update(contestants)

    def update(self, contestants=[]):
        for w in self.winfo_children():
            w.destroy()

        for index, player in enumerate(contestants[2:]):
            w = ttk.Label(self, text=player.name, anchor=tk.NW)
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
        self.lbl_king = ttk.Label(self, anchor=tk.CENTER, font=LARGE_FONT, foreground='red')
        self.lbl_king.pack(fill=tk.BOTH, expand=1, side=tk.LEFT)

        king_button_frame = ttk.Frame(master=self.lbl_king, style="Red.TFrame")
        king_button_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.button_king_add_point = ttk.Button(king_button_frame, text="+1")
        self.button_king_add_point.pack(side=tk.LEFT, expand=1, fill=tk.X)
        self.button_king_substract_point = ttk.Button(king_button_frame, text="-1")
        self.button_king_substract_point.pack(side=tk.LEFT, expand=1, fill=tk.X)
        self.button_king_move_to_queue = ttk.Button(king_button_frame, text="Move to queue")
        self.button_king_move_to_queue.pack(side=tk.LEFT, expand=1, fill=tk.X)

        vs = ttk.Label(self, text="versus", anchor=tk.CENTER)
        vs.pack(fill=tk.BOTH, side=tk.LEFT, expand=1)

        self.lbl_challenger = ttk.Label(self, font=LARGE_FONT, foreground='blue', anchor=tk.CENTER)
        self.lbl_challenger.pack(fill=tk.BOTH, expand=1, side=tk.LEFT)

        challenger_button_frame = ttk.Frame(master=self.lbl_challenger)
        challenger_button_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.button_challenger_add_point = ttk.Button(challenger_button_frame, text="+1")
        self.button_challenger_add_point.pack(side=tk.LEFT, expand=1, fill=tk.X)
        self.button_challenger_substract_point = ttk.Button(challenger_button_frame, text="-1")
        self.button_challenger_substract_point.pack(side=tk.LEFT, expand=1, fill=tk.X)
        self.button_challenger_back_to_queue = ttk.Button(challenger_button_frame, text="Back to queue")
        self.button_challenger_back_to_queue.pack(side=tk.LEFT, expand=1, fill=tk.X)
        self.button_challenger_make_king = ttk.Button(challenger_button_frame, text="Make king")
        self.button_challenger_make_king.pack(side=tk.LEFT, expand=1, fill=tk.X)


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


        parser = configparser.ConfigParser()
        parser.read('initial_values.ini')
        self.contestants = [Contestant(name=name) for name in parser.get("contestants", "names").split("\n")]

        self.king_name = tk.StringVar()
        self.king_name.set(self.contestants[0].name)
        self.challenger_name = tk.StringVar()
        self.challenger_name.set(self.contestants[1].name)

        self.clock = int(parser.get('time', 'time_remaining'))
        self.clock_display = tk.StringVar()

        self.grid()
        self.create_frames()
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.attach_events()

        self.update()

    def create_frames(self):
        self.frame_right = ttk.Frame(master=self)

        self.frame_current_fight = CurrentFight(master=self.frame_right)
        self.frame_current_fight.pack(fill=tk.BOTH, expand=1)


        self.frame_upcoming = Upcoming(master=self.frame_right)
        self.frame_upcoming.pack(fill=tk.BOTH, expand=1)
        self.frame_current_fight.lbl_king.config(textvariable=self.king_name)
        self.frame_current_fight.lbl_challenger.config(textvariable=self.challenger_name)


        self.frame_timer = Timer(master=self.frame_right)
        self.frame_timer.pack()
        self.frame_timer.display.config(textvariable=self.clock_display)

        self.frame_rankings = Rankings(master=self)
        self.frame_rankings.grid(column=0, row=0, rowspan=3, sticky=tk.NW)

        self.frame_right.grid(column=1, row=0, sticky='news')

        self.tick_tock()

    def attach_events(self):
        self.frame_current_fight.button_king_add_point.bind("<Button-1>", self.add_point_to_king)
        self.frame_current_fight.button_king_substract_point.bind("<Button-1>", self.substract_point_for_king)
        self.frame_current_fight.button_king_move_to_queue.bind("<Button-1>", self.move_king_to_queue)

        self.frame_current_fight.button_challenger_add_point.bind("<Button-1>", self.add_point_for_challenger)
        self.frame_current_fight.button_challenger_substract_point.bind("<Button-1>", self.substract_point_for_challenger)
        self.frame_current_fight.button_challenger_back_to_queue.bind("<Button-1>", self.move_challenger_back_to_queue)
        self.frame_current_fight.button_challenger_make_king.bind("<Button-1>", self.make_challenger_king)

    def add_point_to_king(self, event):
        self.contestants[0].score += 1
        self.update()

    def substract_point_for_king(self, event):
        self.contestants[0].score -= 1
        self.update()

    def move_king_to_queue(self, event):
        self.contestants += [self.contestants.pop(0)]
        self.update()

    def add_point_for_challenger(self, event):
        self.contestants[1].score += 1
        self.update()

    def substract_point_for_challenger(self, event):
        self.contestants[1].score -= 1
        self.update()

    def make_challenger_king(self, event):
        self.move_king_to_queue(event)
        self.update()

    def move_challenger_back_to_queue(self, event):
        self.contestants += [self.contestants.pop(1)]
        self.update()

    def update(self):
        self.frame_rankings.update_ranking(self.contestants)
        self.frame_upcoming.update(self.contestants)
        self.king_name.set(self.contestants[0].name)
        self.challenger_name.set(self.contestants[1].name)

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

app.bind_all("<Key>", app.catch_keypress)

app.mainloop()
