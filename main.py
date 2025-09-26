# -*- coding: utf-8 -*-
"""
Jirka Kára – Mini Hry (Kivy/Android verze)
Hra 1: Stránskej v Holešovicích (náhodné bludiště na čas)
Ovládání: šipky na obrazovce + swipe gesta
Start: náhodný obrázek (squat/špinavá postel/cela), zvuk na startu
Cíl: svatba Jirky Káry (obrázek)
Penalizace: při nárazu do zdi je 40% šance na hlášku a -5s z času
"""
import random
import time
import os

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window

APP_TITLE = "Jirka Kára – Mini Hry (Android)"
VERSION = "1.0-android"

HLASKY = [
    "Hele, Stránskej, kudy na Stross?",
    "Neblbni a drž směr!",
    "Tady to znám, ale dneska je to nějak jiný…",
    "Zatni zuby a jdi rovně!",
    "Kam zas uhýbáš, ty vole?",
    "Dýchej a soustřeď se.",
    "Dneska to dáš!",
    "Nespěchej na špatným místě.",
    "Holešovice nejsou pro slabý povahy.",
    "Cíl je svatba Jirky Káry, makej!",
]

# Asset filenames (place next to main.py or in app dir)
ASSET_START_IMAGES = [
    "start_squat.png",
    "start_bed.png",
    "start_jail.png",
]
ASSET_PLAYER = "stranskej.png"
ASSET_GOAL = "goal_cil.png"
ASSET_START_SOUND = "WhatsApp Audio 2025-09-26 at 15.13.18.mpeg"
ASSET_FAIL_SOUNDS = ["fail1.mpeg", "fail2.mpeg", "fail3.mpeg"]

def resource_path(fname):
    # Kivy/Buildozer will package files found relative to main.py
    return os.path.join(os.path.dirname(__file__), fname)

class Maze:
    def __init__(self, rows, cols):
        self.rows = rows if rows % 2 == 1 else rows + 1
        self.cols = cols if cols % 2 == 1 else cols + 1
        self.grid = [[1 for _ in range(self.cols)] for _ in range(self.rows)]
        self.start = (1,1)
        self.goal = (self.rows-2, self.cols-2)

    def carve(self):
        r, c = 1, 1
        self.grid[r][c] = 0
        stack = [(r, c)]
        dirs = [(-2, 0), (2, 0), (0, -2), (0, 2)]
        while stack:
            r, c = stack[-1]
            neighbors = []
            for dr, dc in dirs:
                nr, nc = r + dr, c + dc
                if 1 <= nr < self.rows - 1 and 1 <= nc < self.cols - 1 and self.grid[nr][nc] == 1:
                    neighbors.append((nr, nc, r + dr // 2, c + dc // 2))
            if neighbors:
                nr, nc, wr, wc = random.choice(neighbors)
                self.grid[wr][wc] = 0
                self.grid[nr][nc] = 0
                stack.append((nr, nc))
            else:
                stack.pop()

class MazeWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.maze = None
        self.cell_size = 16
        self.xoff = 0
        self.yoff = 0
        self.player = [1,1]
        self.steps = 0
        self.player_tex = None
        self.goal_tex = None
        self.start_tex = None
        self.start_bg_path = None

    def set_assets(self, player_tex, goal_tex):
        self.player_tex = player_tex
        self.goal_tex = goal_tex

    def set_start_tex(self, start_tex):
        self.start_tex = start_tex

    def compute_geometry(self):
        if not self.maze:
            return
        rows, cols = self.maze.rows, self.maze.cols
        self.cell_size = max(10, min(int(self.width // cols), int(self.height // rows)))
        self.xoff = int((self.width - self.cell_size * cols) // 2)
        self.yoff = int((self.height - self.cell_size * rows) // 2)

    def on_size(self, *args):
        self.compute_geometry()
        self.redraw()

    def redraw(self):
        self.canvas.clear()
        if not self.maze: return
        rows, cols = self.maze.rows, self.maze.cols

        with self.canvas:
            # background
            Color(0.07, 0.08, 0.11, 1)  # dark
            Rectangle(pos=self.pos, size=self.size)

            # draw cells
            for r in range(rows):
                for c in range(cols):
                    x0 = self.xoff + c * self.cell_size
                    y0 = self.yoff + r * self.cell_size
                    if self.maze.grid[r][c] == 1:
                        Color(0.12, 0.16, 0.22, 1)  # wall
                    else:
                        Color(0.03, 0.07, 0.12, 1)  # path
                    Rectangle(pos=(x0, y0), size=(self.cell_size, self.cell_size))

            # start cell overlay
            sr, sc = self.maze.start
            sx = self.xoff + sc * self.cell_size + 1
            sy = self.yoff + sr * self.cell_size + 1
            if self.start_tex:
                Color(1,1,1,1)
                Rectangle(texture=self.start_tex, pos=(sx, sy), size=(self.cell_size-2, self.cell_size-2))

            # goal image
            gr, gc = self.maze.goal
            gx = self.xoff + gc * self.cell_size + 1
            gy = self.yoff + gr * self.cell_size + 1
            if self.goal_tex:
                Color(1,1,1,1)
                Rectangle(texture=self.goal_tex, pos=(gx, gy), size=(self.cell_size-2, self.cell_size-2))

            # player
            pr, pc = self.player
            px = self.xoff + pc * self.cell_size + 2
            py = self.yoff + pr * self.cell_size + 2
            if self.player_tex:
                Color(1,1,1,1)
                Rectangle(texture=self.player_tex, pos=(px, py), size=(self.cell_size-4, self.cell_size-4))
            else:
                Color(0.58, 0.77, 0.99, 1)
                Rectangle(pos=(px, py), size=(self.cell_size-4, self.cell_size-4))

class GameScreen(BoxLayout):
    def __init__(self, difficulty="Střední", **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.difficulty = difficulty
        self.time_limit = 120 if difficulty == "Střední" else (90 if difficulty == "Lehká" else 150)
        self.remaining = self.time_limit
        self.penalty_seconds = 0
        self.start_time = None
        self.running = False

        # Sounds
        self.start_sound = None
        self.fail_sounds = []

        # Header
        top = BoxLayout(orientation="horizontal", size_hint_y=None, height="48dp")
        self.lbl_title = Label(text=f"[b]Stránskej v Holešovicích – {self.difficulty}[/b]",
                               markup=True, color=(0.89,0.91,0.94,1))
        self.lbl_timer = Label(text="Čas: --", color=(0.65,0.95,0.82,1), size_hint_x=None, width="120dp")
        top.add_widget(self.lbl_title)
        top.add_widget(self.lbl_timer)
        self.add_widget(top)

        # Subheader
        sub = BoxLayout(orientation="horizontal", size_hint_y=None, height="36dp", padding=(8,0))
        self.lbl_quote = Label(text=random.choice(HLASKY), color=(0.58,0.77,0.99,1))
        sub.add_widget(self.lbl_quote)
        self.add_widget(sub)

        # Maze area
        self.maze_widget = MazeWidget()
        self.add_widget(self.maze_widget)

        # Controls (on-screen arrows)
        controls = BoxLayout(orientation="horizontal", size_hint_y=None, height="80dp", padding=6, spacing=6)
        def mkbtn(txt, cb):
            b = Button(text=txt)
            b.bind(on_press=lambda *_: cb())
            return b
        left = mkbtn("◀", lambda: self.move(0,-1))
        up = mkbtn("▲", lambda: self.move(-1,0))
        down = mkbtn("▼", lambda: self.move(1,0))
        right = mkbtn("▶", lambda: self.move(0,1))
        controls.add_widget(left); controls.add_widget(up); controls.add_widget(down); controls.add_widget(right)
        self.add_widget(controls)

        # Swipe gestures
        self.touch_start = None
        self.bind(on_touch_down=self._on_down, on_touch_up=self._on_up)

        # Init assets & maze
        self._load_assets()
        self._new_maze()

        # Timer loop
        Clock.schedule_interval(self._tick, 0.2)

    def _on_down(self, instance, touch):
        self.touch_start = (touch.x, touch.y)

    def _on_up(self, instance, touch):
        if not self.touch_start: return
        dx = touch.x - self.touch_start[0]
        dy = touch.y - self.touch_start[1]
        if abs(dx) > abs(dy):
            if dx > 20: self.move(0,1)
            elif dx < -20: self.move(0,-1)
        else:
            if dy > 20: self.move(1,0)
            elif dy < -20: self.move(-1,0)
        self.touch_start = None

    def _load_assets(self):
        # images
        from kivy.core.image import Image as CoreImage
        # player
        ppath = resource_path(ASSET_PLAYER)
        self.player_tex = None
        if os.path.exists(ppath):
            self.player_tex = CoreImage(ppath).texture
        # goal
        gpath = resource_path(ASSET_GOAL)
        self.goal_tex = None
        if os.path.exists(gpath):
            self.goal_tex = CoreImage(gpath).texture
        # start images
        self.start_paths = []
        for s in ASSET_START_IMAGES:
            sp = resource_path(s)
            if os.path.exists(sp):
                self.start_paths.append(sp)
        # sounds
        ssp = resource_path(ASSET_START_SOUND)
        self.start_sound = SoundLoader.load(ssp) if os.path.exists(ssp) else None
        for fs in ASSET_FAIL_SOUNDS:
            fsp = resource_path(fs)
            snd = SoundLoader.load(fsp) if os.path.exists(fsp) else None
            if snd: self.fail_sounds.append(snd)

    def _new_maze(self):
        size = 31 if self.difficulty == "Střední" else (21 if self.difficulty == "Lehká" else 41)
        m = Maze(size, size)
        m.carve()
        self.maze_widget.maze = m
        self.maze_widget.player = list(m.start)
        self.maze_widget.steps = 0
        # select start image
        self.start_tex = None
        if self.start_paths:
            from kivy.core.image import Image as CoreImage
            self.start_tex = CoreImage(random.choice(self.start_paths)).texture
        self.maze_widget.set_assets(self.player_tex, self.goal_tex)
        self.maze_widget.set_start_tex(self.start_tex)
        self.start_time = time.time()
        self.remaining = self.time_limit
        self.penalty_seconds = 0
        self.running = True
        if self.start_sound:
            self.start_sound.stop()
            self.start_sound.play()
        self.maze_widget.compute_geometry()
        self.maze_widget.redraw()

    def _tick(self, dt):
        if not self.running: return
        elapsed = int(time.time() - self.start_time)
        remain = max(0, self.time_limit - elapsed - self.penalty_seconds)
        self.remaining = remain
        self.lbl_timer.text = f"Čas: {remain}s"
        if remain <= 0:
            self._game_over()
            return

    def _maybe_penalty(self):
        # 40% chance: show quote and deduct 5s
        if random.random() < 0.4:
            self.lbl_quote.text = random.choice(HLASKY)
            self.penalty_seconds += 5

    def move(self, dr, dc):
        if not self.running: return
        r, c = self.maze_widget.player
        nr, nc = r + dr, c + dc
        m = self.maze_widget.maze
        if 0 <= nr < m.rows and 0 <= nc < m.cols and m.grid[nr][nc] == 0:
            self.maze_widget.player = [nr, nc]
            self.maze_widget.steps += 1
            if self.maze_widget.steps % 10 == 0:
                self.lbl_quote.text = random.choice(HLASKY)
            self.maze_widget.redraw()
            if (nr, nc) == m.goal:
                self._win()
        else:
            self._maybe_penalty()

    def _win(self):
        self.running = False
        msg = f"Dal jsi to! Kroky: {self.maze_widget.steps}, zbývající čas: {self.remaining}s"
        Popup(title="Vítězství!", content=Label(text=msg), size_hint=(0.8,0.4)).open()
        # new maze after short delay
        Clock.schedule_once(lambda *_: self._new_maze(), 1.2)

    def _game_over(self):
        self.running = False
        # play fail
        if self.fail_sounds:
            try:
                random.choice(self.fail_sounds).play()
            except Exception:
                pass
        Popup(title="GAME OVER", content=Label(text="Došel čas! Cíl je svatba Jirky Káry – zkus to znovu."),
              size_hint=(0.8,0.4)).open()
        Clock.schedule_once(lambda *_: self._new_maze(), 1.2)

class MenuScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=8, spacing=8, **kwargs)
        self.add_widget(Label(text=f"[b]{APP_TITLE}[/b]\\nVerze {VERSION}", markup=True, size_hint_y=None, height="96dp"))
        self.diff = "Střední"

        row = BoxLayout(size_hint_y=None, height="48dp", spacing=6)
        self.btn_e = Button(text="Lehká", on_press=lambda *_: self.set_diff("Lehká"))
        self.btn_m = Button(text="Střední", on_press=lambda *_: self.set_diff("Střední"))
        self.btn_h = Button(text="Těžká", on_press=lambda *_: self.set_diff("Těžká"))
        row.add_widget(self.btn_e); row.add_widget(self.btn_m); row.add_widget(self.btn_h)
        self.add_widget(row)

        self.start_btn = Button(text="Spustit hru", size_hint_y=None, height="56dp")
        self.start_btn.bind(on_press=self.start_game)
        self.add_widget(self.start_btn)

        self.status = Label(text="Start: náhodný obrázek, Cíl: svatba. Ovládání: šipky / swipe.", size_hint_y=None, height="48dp")
        self.add_widget(self.status)
        self.update_diff_buttons()

    def set_diff(self, d):
        self.diff = d
        self.update_diff_buttons()

    def update_diff_buttons(self):
        for b, name in [(self.btn_e,"Lehká"),(self.btn_m,"Střední"),(self.btn_h,"Těžká")]:
            b.disabled = (self.diff == name)

    def start_game(self, *args):
        self.parent.show_game(self.diff)

class Root(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.menu = MenuScreen(size_hint=(1,1))
        self.add_widget(self.menu)

    def show_menu(self, *args):
        self.clear_widgets()
        self.menu = MenuScreen(size_hint=(1,1))
        self.add_widget(self.menu)

    def show_game(self, difficulty):
        self.clear_widgets()
        gs = GameScreen(difficulty=difficulty, size_hint=(1,1))
        # back button overlay
        back = Button(text="« Menu", size_hint=(None,None), width="120dp", height="44dp",
                      pos=(10, Window.height-54))
        back.bind(on_press=lambda *_: self.show_menu())
        self.add_widget(gs)
        self.add_widget(back)

class JirkaKaraApp(App):
    def build(self):
        self.title = APP_TITLE
        root = Root()
        return root

if __name__ == "__main__":
    JirkaKaraApp().run()
