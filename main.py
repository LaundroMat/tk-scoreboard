import configparser
import operator
import datetime
from functools import partial

import tkinter as tk
from tkinter import messagebox
import tkinter.ttk as ttk

from contestant import Contestant

LARGE_FONT = ('Helvetica', '32')
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
        self.rows = []
        self.update(contestants)
        self.selected = None

    def update(self, contestants=[]):
        for w in self.rows:
            w.destroy()

        for index, player in enumerate(contestants[2:]):
            w = ttk.Label(self, text=player.name, anchor=tk.NW)
            if index < 3:
                w.configure(font=LARGE_FONT)
            else:
                w.configure(font=REGULAR_FONT)
            w.bind('<Button-1>', partial(self.widget_selected, index))
            w.pack(fill=tk.X, expand=1)
            self.rows.append(w)

    def widget_selected(self, index, event):
        print("Selectorized ", index)
        # Clear other selection
        for w in self.rows:
            w.configure(background="white") #TODO: find how to get bg color 
        self.rows[index].configure(background="grey")
        self.selected = index


class CurrentFight(ttk.LabelFrame):
    def __init__(self, master=None, *args, **kwargs):
        super(CurrentFight, self).__init__(master, *args, **kwargs)
        self.config(text="Now fighting", relief='raised')
        self.create_widgets()

    def create_widgets(self):
        # Use anchor=tl.CENTER and fill=tk.X to center vertically
        self.frame_king = ttk.Frame(master=self)
        self.frame_king.pack(fill=tk.BOTH, expand=1, side=tk.LEFT)

        self.lbl_king = ttk.Label(self.frame_king, anchor=tk.CENTER, font=LARGE_FONT, foreground='red')
        self.lbl_king.pack()

        king_button_frame = ttk.Frame(master=self.frame_king, style="Red.TFrame")
        king_button_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.button_king_add_point = ttk.Button(king_button_frame, text="+1")
        self.button_king_add_point.pack(side=tk.LEFT, expand=1, fill=tk.X)
        self.button_king_substract_point = ttk.Button(king_button_frame, text="-1")
        self.button_king_substract_point.pack(side=tk.LEFT, expand=1, fill=tk.X)
        self.button_king_move_to_queue = ttk.Button(king_button_frame, text="Move to queue")
        self.button_king_move_to_queue.pack(side=tk.LEFT, expand=1, fill=tk.X)

        vs = ttk.Label(self, text="versus", anchor=tk.CENTER)
        vs.pack(fill=tk.BOTH, side=tk.LEFT, expand=1)

        self.frame_challenger = ttk.Frame(master=self)
        self.frame_challenger.pack(fill=tk.BOTH, expand=1, side=tk.LEFT)

        self.lbl_challenger = ttk.Label(self.frame_challenger, font=LARGE_FONT, foreground='blue', anchor=tk.CENTER)
        self.lbl_challenger.pack()

        challenger_button_frame = ttk.Frame(master=self.frame_challenger)
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
    def __init__(self, master=None, time_left=0, *args, **kwargs):
        super(Timer, self).__init__(master, *args, **kwargs)
        self.time_left = datetime.timedelta(seconds=time_left)
        self.display_time = tk.StringVar()
        self.create_widgets()
        self.lbl_display.config(textvariable=self.display_time)
        self.display_time.set("{0}".format(self.time_left))

        self.is_paused = True
        self.tick_tock()
        self.blink()

    def create_widgets(self):
        self.frame = ttk.Frame(self)
        self.lbl_display = ttk.Label(self.frame, style="Timer.TLabel")
        self.lbl_display.pack()
        self.button_add_5_seconds = ttk.Button(self.frame, text="+5 seconds")
        self.button_add_5_seconds.pack(side=tk.LEFT)
        self.button_substract_5_seconds = ttk.Button(self.frame, text="-5 seconds")
        self.button_substract_5_seconds.pack()
        self.frame.pack()

    def tick_tock(self):
        if not self.is_paused:
            self.time_left -= datetime.timedelta(seconds=1)
            self.job_tick_tock = self.after(1000, self.tick_tock)
        self.display_time.set("{0}".format(self.time_left))

    def timer_action(self):
        if self.is_paused:
            self.is_paused = False
            if self.job_blink:
                self.after_cancel(self.job_blink)
            self.lbl_display.configure(style="Timer.TLabel")
            self.tick_tock()
        else:
            self.is_paused = True
            if self.job_tick_tock:
                self.after_cancel(self.job_tick_tock)
            self.blink()

    def blink(self):
        if self.lbl_display.configure().get('style')[-1] == 'Timer.TLabel':
            self.lbl_display.configure(style="ReverseTimer.TLabel")
        elif self.lbl_display.configure().get('style')[-1] == 'ReverseTimer.TLabel':
            self.lbl_display.configure(style="Timer.TLabel")

        self.job_blink = self.after(500, self.blink)

    def add_5_seconds(self, event):
        self.time_left += datetime.timedelta(seconds=5)
        self.display_time.set("{0}".format(self.time_left))

    def substract_5_seconds(self, event):
        self.time_left -= datetime.timedelta(seconds=5)
        self.display_time.set("{0}".format(self.time_left))


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

        time_left = int(parser.get('time', 'time_remaining'))

        self.grid()
        self.create_frames(time_left=time_left)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.attach_events()

        self.update()


    def create_frames(self, time_left=0):
        self.frame_right = ttk.Frame(master=self)

        self.frame_current_fight = CurrentFight(master=self.frame_right)
        self.frame_current_fight.pack(fill=tk.BOTH, expand=1)

        self.frame_upcoming = Upcoming(master=self.frame_right)
        self.frame_upcoming.pack(fill=tk.BOTH, expand=1)
        self.frame_current_fight.lbl_king.config(textvariable=self.king_name)
        self.frame_current_fight.lbl_challenger.config(textvariable=self.challenger_name)

        self.frame_timer = Timer(master=self.frame_right, time_left=time_left)
        self.frame_timer.pack(fill=tk.BOTH, expand=1)

        self.frame_rankings = Rankings(master=self)
        self.frame_rankings.grid(column=0, row=0, rowspan=3, sticky=tk.NW)

        self.frame_right.grid(column=1, row=0, sticky='news')

    def attach_events(self):
        self.frame_current_fight.button_king_add_point.bind("<Button-1>", self.add_point_to_king)
        self.frame_current_fight.button_king_substract_point.bind("<Button-1>", self.substract_point_for_king)
        self.frame_current_fight.button_king_move_to_queue.bind("<Button-1>", self.move_king_to_queue)

        self.frame_current_fight.button_challenger_add_point.bind("<Button-1>", self.add_point_for_challenger)
        self.frame_current_fight.button_challenger_substract_point.bind("<Button-1>", self.substract_point_for_challenger)
        self.frame_current_fight.button_challenger_back_to_queue.bind("<Button-1>", self.move_challenger_back_to_queue)
        self.frame_current_fight.button_challenger_make_king.bind("<Button-1>", self.make_challenger_king)

        self.frame_timer.button_add_5_seconds.bind("<Button-1>", self.frame_timer.add_5_seconds)
        self.frame_timer.button_substract_5_seconds.bind("<Button-1>", self.frame_timer.substract_5_seconds)


        self.bind_all("<Up>", self.move_row_up)
        self.bind_all("<Down>", self.move_row_down)

    def add_point_to_king(self, event):
        self.contestants[0].score += 1
        self.update(update_current_fight=False)

    def substract_point_for_king(self, event):
        self.contestants[0].score -= 1
        self.update(update_current_fight=False)

    def move_king_to_queue(self, event):
        self.contestants += [self.contestants.pop(0)]
        self.update()

    def add_point_for_challenger(self, event):
        self.contestants[1].score += 1
        self.update(update_current_fight=False)

    def substract_point_for_challenger(self, event):
        self.contestants[1].score -= 1
        self.update(update_current_fight=False)

    def make_challenger_king(self, event):
        self.move_king_to_queue(event)
        self.update()

    def move_challenger_back_to_queue(self, event):
        self.contestants += [self.contestants.pop(1)]
        self.update()

    def move_row_up(self, key):
        print("Moving up ", self.frame_upcoming.selected)
        self.contestants[self.frame_upcoming.selected], self.contestants[self.frame_upcoming.selected-1] = self.contestants[self.frame_upcoming.selected-1], self.contestants[self.frame_upcoming.selected]
        self.update(update_rankings=False, update_upcoming=True, update_current_fight=False)

    def move_row_down(self, key):
        print("Moving down ", self.frame_upcoming.selected)

    def update(self, update_rankings=True, update_upcoming=True, update_current_fight=True):
        if update_rankings:
            self.frame_rankings.update_ranking(self.contestants)
        if update_upcoming:
            self.frame_upcoming.update(self.contestants)
        if update_current_fight:
            self.king_name.set(self.contestants[0].name)
            self.challenger_name.set(self.contestants[1].name)

    def catch_keypress(self, key):
        print(key.keycode)
        if key.keycode == 27:
            # ESC pressed
            if messagebox.askyesno("Quit", "Really quit?"):
                self.destroy()
        if key.keycode == 32:
            # Space pressed
            self.frame_timer.timer_action()

    def open_admin(self):
        new_window = tk.Toplevel(self)
        tree = ttk.Treeview(master=new_window)
        tree["columns"]=("contestant", "score", "is_king", 'is_contender')
        tree.column("contestant", width=100)
        tree.column("score", width=100)
        tree.heading("contestant", text="Contestant")
        tree.heading("score", text="Score")
        tree.heading("is_king", text="Is king?")
        tree.heading("is_contender", text="Is contender?")

        tree.insert("" , 0,    text="Line 1", values=("1A","1b"))

        tree.grid()
        tree.focus_force()


app = Scoreboard()
width, height = app.winfo_screenwidth(), app.winfo_screenheight()
print(width, height)
app.geometry('%dx%d+0+0' % (width,height))
style = ttk.Style(master=app)
style.configure('.', font=REGULAR_FONT, foreground='black')
style.configure('TLabel', font=REGULAR_FONT)
style.configure('Timer.TLabel', font=LARGE_FONT, foreground='red')
style.configure('ReverseTimer.TLabel', font=LARGE_FONT, foreground='grey')
style.configure('Red.TFrame', background='red')
style.configure('Red.TLabel', background='red')
style.configure('TLabelframe', padding=12)
style.configure('TLabelframe.Label', foreground='black')


app.attributes("-fullscreen", True)
app.open_admin()
app.bind_all("<Key>", app.catch_keypress)

app.mainloop()
