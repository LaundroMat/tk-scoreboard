import configparser
import operator
import datetime
from functools import partial
import logging
import sys

import tkinter as tk
from tkinter import messagebox
import tkinter.ttk as ttk

from contestant import Contestant

LARGE_FONT = ('Helvetica', '36')
REGULAR_FONT = ('Helvetica', '16')
SMALL_FONT = ('Helvetica', '12')

logging.basicConfig(format='%(asctime)s %(message)s',
                    filename='game-{dte}.log'.format(dte=str(datetime.datetime.now().strftime("%d%b%Y-%H%M%S"))),
                    level=logging.INFO)


class Rankings(ttk.LabelFrame):
    def __init__(self, master=None, contestants=None, *args, **kwargs):
        super(Rankings, self).__init__(master, *args, **kwargs)
        self.config(text="Ranking")
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
                line.pack(fill=tk.BOTH, expand=1)
                lbl_position = ttk.Label(line, text="{0}. ".format(str(player_position)), anchor=tk.NW)
                lbl_position.pack(fill=tk.X, side=tk.LEFT)
                lbl_name = ttk.Label(line, text=player.name, anchor=tk.W)
                lbl_name.pack(fill=tk.X, expand=1, side=tk.LEFT)
                lbl_score = ttk.Label(line, text=str(player.score), anchor=tk.NE, padding=[5, 0, 0, 0])
                lbl_score.pack(fill=tk.X, expand=1, side=tk.RIGHT)

                previous_score = player.score


class Upcoming(ttk.Labelframe):
    def __init__(self, master=None, contestants=[]):
        super(Upcoming, self).__init__(master)
        self.config(text="Upcoming contenders")
        self.player_selected = None
        self.rows = []
        self.update(contestants)

    def update(self, contestants=[]):
        for w in self.rows:
            w.destroy()

        self.rows = []

        for row, player in enumerate(contestants[2:]):
            w = ttk.Label(self, text=player.name, anchor=tk.NW)
            if row < 1:
                w.configure(font=LARGE_FONT)
            else:
                w.configure(font=REGULAR_FONT)
            w.bind('<Button-1>', partial(self.widget_selected, row))
            w.pack(fill=tk.X, expand=1)
            self.rows.append(w)

        if self.player_selected:
            self.rows[self.player_selected - 2].configure(style='Selected.TLabel')

    def widget_selected(self, row, event):
        # Clear selections
        for w in self.rows:
            w.configure(style='Unselected.TLabel')

        if self.player_selected == row + 2:  # Add 2 because we start from [2:]
            # Unselect player
            self.player_selected = None
        else:
            self.rows[row].configure(style='Selected.TLabel')
            self.player_selected = row + 2


class CurrentFight(ttk.LabelFrame):
    def __init__(self, master=None, *args, **kwargs):
        super(CurrentFight, self).__init__(master, *args, **kwargs)
        self.config(text="Now fighting", relief='raised')
        self.create_widgets()

    def create_widgets(self):
        # Use anchor=tl.CENTER and fill=tk.X to center vertically
        self.frame_king = ttk.Frame(master=self)
        self.frame_king.pack(fill=tk.BOTH, expand=1, side=tk.LEFT)

        self.frame_king_label = ttk.Label(self.frame_king, font=SMALL_FONT, anchor=tk.CENTER, text="King".upper())
        self.frame_king_label.pack()
        self.lbl_king = ttk.Label(self.frame_king, anchor=tk.CENTER, font=LARGE_FONT)
        self.lbl_king.pack(pady=32)

        king_button_frame = ttk.Frame(master=self.frame_king)
        king_button_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.button_king_add_point = ttk.Button(king_button_frame, text="+1", style='MyButton.TButton')
        self.button_king_add_point.pack(side=tk.LEFT, expand=1, fill=tk.X)
        self.button_king_substract_point = ttk.Button(king_button_frame, text="-1")
        self.button_king_substract_point.pack(side=tk.LEFT, expand=1, fill=tk.X)
        self.button_king_move_to_queue = ttk.Button(king_button_frame, text="Move to queue")
        self.button_king_move_to_queue.pack(side=tk.LEFT, expand=1, fill=tk.X)

        vs = ttk.Label(self, text="versus", anchor=tk.CENTER)
        vs.pack(fill=tk.BOTH, side=tk.LEFT, expand=1)

        self.frame_challenger = ttk.Frame(master=self)
        self.frame_challenger.pack(fill=tk.BOTH, expand=1, side=tk.LEFT)

        self.frame_challenger_label = ttk.Label(self.frame_challenger, font=SMALL_FONT, anchor=tk.CENTER,
                                                text="Challenger".upper())
        self.frame_challenger_label.pack()
        self.lbl_challenger = ttk.Label(self.frame_challenger, font=LARGE_FONT, anchor=tk.CENTER)
        self.lbl_challenger.pack(pady=32)

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
        self.parser = configparser.ConfigParser()
        self.parser.read('initial_values.ini')

        self.contestants = [Contestant(name=name) for name in self.parser.get("contestants", "names").split("\n")]

        self.king_name = tk.StringVar()
        self.king_name.set(self.contestants[0].name)
        self.challenger_name = tk.StringVar()
        self.challenger_name.set(self.contestants[1].name)

    def draw(self):
        self.grid()
        self.create_frames(time_left=int(self.parser.get('time', 'time_remaining')))
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.attach_events()

        self.update()

    def create_frames(self, time_left=0):
        self.frame_rankings = Rankings(master=self)
        self.frame_rankings.grid(column=0, row=0, sticky=tk.N, ipadx=32)
        self.grid_columnconfigure(0, weight=1)

        self.frame_timer = Timer(master=self, time_left=time_left)
        self.frame_timer.grid(column=0, row=1)

        self.frame_right = ttk.Frame(master=self)
        self.frame_right.grid(column=1, row=0, sticky='news', rowspan=2)

        self.frame_current_fight = CurrentFight(master=self.frame_right)
        self.frame_current_fight.pack(fill=tk.BOTH, expand=1)
        self.frame_current_fight.frame_king_label.config(style='King.TLabel')
        self.frame_current_fight.lbl_king.config(textvariable=self.king_name, style='King.TLabel')
        self.frame_current_fight.frame_challenger_label.config(style='Challenger.TLabel')
        self.frame_current_fight.lbl_challenger.config(textvariable=self.challenger_name, style='Challenger.TLabel')

        self.frame_upcoming = Upcoming(master=self.frame_right)
        self.frame_upcoming.pack(fill=tk.BOTH, expand=1)

    def attach_events(self):
        self.frame_current_fight.button_king_add_point.bind("<Button-1>", self.add_point_to_king)
        self.frame_current_fight.button_king_substract_point.bind("<Button-1>", self.substract_point_for_king)
        self.frame_current_fight.button_king_move_to_queue.bind("<Button-1>", self.move_king_to_queue)

        self.frame_current_fight.button_challenger_add_point.bind("<Button-1>", self.add_point_for_challenger)
        self.frame_current_fight.button_challenger_substract_point.bind("<Button-1>",
                                                                        self.substract_point_for_challenger)
        self.frame_current_fight.button_challenger_back_to_queue.bind("<Button-1>", self.move_challenger_back_to_queue)
        self.frame_current_fight.button_challenger_make_king.bind("<Button-1>", self.make_challenger_king)

        self.frame_timer.button_add_5_seconds.bind("<Button-1>", self.frame_timer.add_5_seconds)
        self.frame_timer.button_substract_5_seconds.bind("<Button-1>", self.frame_timer.substract_5_seconds)

    def add_point_to_king(self, event):
        self.contestants[0].score += 1

        try:
            logging.info("{name} (currently king) scores a point and has {score} point(s) now.".format(
                name=self.contestants[0].name, score=self.contestants[0].score))
        except:
            print(sys.exc_info()[0])

        self.update(update_current_fight=False)

    def substract_point_for_king(self, event):
        self.contestants[0].score -= 1

        try:
            logging.info("{name} (currently king) lost a point and has {score} point(s) now.".format(
                name=self.contestants[0].name, score=self.contestants[0].score))
        except e:
            print(e)

        self.update(update_current_fight=False)

    def move_king_to_queue(self, event):
        self.contestants += [self.contestants.pop(0)]

        try:
            logging.info("{name} is no longer king! {new} is the new king.".format(
                name=self.contestants[-1].name, new=self.contestants[0].name))
        except e:
            print(e)

        self.update()

    def add_point_for_challenger(self, event):
        self.contestants[1].score += 1

        try:
            logging.info(
                "{name} (the current challenger) has scored a point against king {king} and now has {score} point(s).".format(
                    name=self.contestants[1].name, king=self.contestants[0].name, score=self.contestants[1].score))
        except e:
            print(e)

        self.update(update_current_fight=False)

    def substract_point_for_challenger(self, event):
        self.contestants[1].score -= 1

        try:
            logging.info(
                "{name} (the current challenger) has lost a point against king {king} and now has {score} point(s).".format(
                    name=self.contestants[1].name, king=self.contestants[0].name, score=self.contestants[1].score))
        except e:
            print(e)

        self.update(update_current_fight=False)

    def make_challenger_king(self, event):
        self.move_king_to_queue(event)
        self.update()

    def move_challenger_back_to_queue(self, event):
        self.contestants += [self.contestants.pop(1)]

        try:
            logging.info("{name} lost the battle against the king and has returned to the queue!.".format(
                name=self.contestants[-1].name))
        except e:
            print(e)

        self.update()

    def update(self, update_rankings=True, update_upcoming=True, update_current_fight=True):
        if update_rankings:
            self.frame_rankings.update_ranking(self.contestants)
        if update_upcoming:
            self.frame_upcoming.update(self.contestants)
        if update_current_fight:
            self.king_name.set(self.contestants[0].name)
            self.challenger_name.set(self.contestants[1].name)

    def catch_keypress(self, key):
        # print(key.keycode)
        if key.keycode == 27:
            # ESC pressed
            if messagebox.askyesno("Quit", "Really quit?"):
                logging.info("=== FINAL RESULTS ===")
                ranking = sorted(self.contestants.copy(), key=operator.attrgetter('score'), reverse=True)
                player_position = 1
                previous_score = ranking[0].score
                for player in ranking:
                    if player.score < previous_score:
                        player_position += 1
                    logging.info(
                        "{pos}.\t{name}\t{score}".format(pos=player_position, name=player.name, score=player.score))

                self.destroy()
        if key.keycode == 32:
            # Space pressed
            self.frame_timer.timer_action()

        if key.keycode == 38 and self.frame_upcoming.player_selected:
            # Arrow up
            # Don't do anything if this is at the start of the list
            if not self.frame_upcoming.player_selected < 3:
                self.contestants[self.frame_upcoming.player_selected], self.contestants[
                    self.frame_upcoming.player_selected - 1] = self.contestants[
                                                                   self.frame_upcoming.player_selected - 1], \
                                                               self.contestants[self.frame_upcoming.player_selected]
                self.frame_upcoming.player_selected = self.frame_upcoming.player_selected - 1
                self.frame_upcoming.rows[self.frame_upcoming.player_selected - 2].configure(background="grey")
                self.update()

        if key.keycode == 40 and self.frame_upcoming.player_selected:
            # Arrow down
            try:
                self.contestants[self.frame_upcoming.player_selected], self.contestants[
                    self.frame_upcoming.player_selected + 1] = self.contestants[
                                                                   self.frame_upcoming.player_selected + 1], \
                                                               self.contestants[self.frame_upcoming.player_selected]
                self.frame_upcoming.player_selected = self.frame_upcoming.player_selected + 1
                self.update()
            except IndexError:
                # Reached end of list
                pass


app = Scoreboard()
app.configure(background='black')

# >>> s = ttk.Style()
# >>> s.theme_names()
# ('winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative')

style = ttk.Style(master=app)
# style.theme_use("xpnative")
style.configure('.', font=REGULAR_FONT, foreground='white', background='black')
style.configure('TLabel', font=REGULAR_FONT)
style.configure('TButton', foreground="grey")
# bg =style.lookup('TLabel', 'background')
# print(bg)
# print(app.winfo_rgb(bg))
style.configure('Timer.TLabel', font=("Courier New", 40), foreground=app.parser.get('colours', 'timer_on'))
style.configure('ReverseTimer.TLabel', font=("Courier New", 40), foreground=app.parser.get('colours', 'timer_off'))
style.configure('Selected.TLabel', background='white', foreground="black")
style.configure('Unselected.TLabel', background='black')
style.configure('TLabelFrame.Label', padding=12, background='black')
style.configure('TLabelframe.Label', foreground='grey')
style.configure('King.TLabel', foreground=app.parser.get('colours', 'king'))
style.configure('Challenger.TLabel', foreground=app.parser.get('colours', 'challenger'))

app.draw()

app.attributes("-fullscreen", True)
app.bind_all("<Key>", app.catch_keypress)

app.mainloop()
