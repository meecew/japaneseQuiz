import pygame
import sys
import math
import numpy as np
import cv2

# Config
WINDOW_W, WINDOW_H = 1920, 1080
FPS = 60
TITLE = "QUUIIZZ"
 
# Audios
SOUND_CORRECT = "sound_success.mp3"
SOUND_WRONG = "sound_failed.mp3"
SAMPLE_RATE = 44100
 
# ── Questions ────────────────────────────────────────────────────────────────
 
QUESTIONS = [
    {
        "video": None,                          
        "video_label": "Clip 1",
        "question": "test 1",
        "choices": [
            "0",
            "1",
            "2",
            "3",
        ],
        "correct": 0,
    },
    {
        "video": "checkpoint2.mp4",
        "video_label": "Clip 2",
        "question": "Check point 2\nYou stumble across this one phrase that you never saw before - 水戸まで行かなき (mito made ikanaki)\nafter searching the meaning up, Google tells you it's on of the following. Based on the conversation, which of the following meaning is most likely?",
        "choices": [
            "水戸まで行かない (Mito made ikanai) (We are NOT going to Mito.)", 
            "水戸まで行かなければならない (Mito made ikanakereba narai) (We have to go to Mito.)"
        ],
        "correct": 1,
    },
    {
        "video": "checkpoint3.mp4",
        "video_label": "Clip 3",
        "question": "test 3",
        "choices": [
            "0", "1", "2", "3"
        ],
        "correct": 3,
    },
]
 
# element colors
C_BG          = (248, 248, 245)
C_SURFACE     = (255, 255, 255)
C_BORDER      = (210, 210, 200)
C_TEXT        = ( 30,  30,  28)
C_MUTED       = (120, 120, 115)
C_ACCENT      = (127, 119, 221)   
C_ACCENT_DARK = ( 83,  74, 183)
C_CORRECT_BG  = (234, 243, 222)
C_CORRECT_BDR = ( 99, 153,  34)
C_CORRECT_TXT = ( 39,  80,  10)
C_WRONG_BG    = (252, 235, 235)
C_WRONG_BDR   = (226,  75,  74)
C_WRONG_TXT   = ( 80,  19,  19)
C_VIDEO_BG    = ( 17,  17,  17)
C_WHITE       = (255, 255, 255)
# ^
#/|\
# |
# |
# |
# DOESNT THAT LOOK SO CLEAN?!?!

# Renders

# AI wrote ts, idk whats going on
# from here (#0)
def load_cjk_font(size, bold=False):
    candidates = [
        "msgothic", "msgothic.ttc",
        "yugothic", "yugothic.ttc",
        #"meiryo", "meiryo.ttc", KIKI FUNG CAN NOT SEE THIS FONT I JUST KNOW
        "YuGothic",
    ]
    for name in candidates:
        try:
            if name.startswith("/") or name.endswith((".ttf", ".ttc", ".otf")):
                font = pygame.font.Font(name, size)
            else:
                font = pygame.font.SysFont(name, size, bold=bold)
            return font
        except Exception:
            continue
 
    print("[WARNING] No CJK-capable font found. Japanese text may appear as boxes.")
    return pygame.font.SysFont(None, size, bold=bold)
# to here (#0)

def draw_rounded_rect(surface, color, rect, radius=10, border=0, border_color=None):
    x, y, w, h = rect
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border and border_color:
        pygame.draw.rect(surface, border_color, rect, border, border_radius=radius)
 
def draw_text(surface, text, font, color, rect, align="left", valign="top", wrap=True):
    """Draw text inside a rect, with optional word-wrap."""
    x, y, w, h = rect
    if wrap:
        words = text.split()
        lines = []
        current = []
        for word in words:
            test = " ".join(current + [word])
            if font.size(test)[0] <= w:
                current.append(word)
            else:
                if current:
                    lines.append(" ".join(current))
                current = [word]
        if current:
            lines.append(" ".join(current))
    else:
        lines = [text]
 
    total_h = len(lines) * font.get_linesize()
    if valign == "center":
        start_y = y + (h - total_h) // 2
    else:
        start_y = y
 
    for line in lines:
        surf = font.render(line, True, color)
        lw = surf.get_width()
        if align == "center":
            lx = x + (w - lw) // 2
        elif align == "right":
            lx = x + w - lw
        else:
            lx = x
        surface.blit(surf, (lx, start_y))
        start_y += font.get_linesize()
 
# Video (***IMPORTANT, NEED MORE RESEARCH)
 
class VideoPlayer:
    def __init__(self, rect):
        self.rect = rect
        self.cap = None
        self.frame_surf = None
        self.playing = False
        self.fps = 30
        self._frame_timer = 0
 
    def load(self, path):
        try:
            self.cap = cv2.VideoCapture(path)
            if not self.cap.isOpened():
                self.cap = None
                return False
            self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30
            return True
        except Exception:
            return False
 
    def play(self):
        if self.cap:
            self.playing = True
            self._frame_timer = 0
 
    def stop(self):
        self.playing = False
        if self.cap:
            self.cap.release()
            self.cap = None
        self.frame_surf = None
 
    def update(self, dt):
        if not self.playing or not self.cap:
            return
        self._frame_timer += dt
        frame_interval = 1.0 / self.fps
        while self._frame_timer >= frame_interval:
            self._frame_timer -= frame_interval
            ret, frame = self.cap.read()
            if not ret:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                self.playing = False
                return
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rx, ry, rw, rh = self.rect
            frame = cv2.resize(frame, (rw, rh))
            self.frame_surf = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
 
    def draw(self, surface, font_small, label):
        rx, ry, rw, rh = self.rect
        pygame.draw.rect(surface, C_VIDEO_BG, self.rect, border_radius=12)
        if self.frame_surf:
            surface.blit(self.frame_surf, (rx, ry))
            pygame.draw.rect(surface, C_BORDER, self.rect, 1, border_radius=12)
        else:
            # Placeholder
            cx, cy = rx + rw // 2, ry + rh // 2
            # Play button circle
            pygame.draw.circle(surface, (60, 60, 60), (cx, cy), 32)
            # Triangle
            pts = [(cx - 10, cy - 14), (cx + 18, cy), (cx - 10, cy + 14)]
            pygame.draw.polygon(surface, C_WHITE, pts)
            # Label
            lw = font_small.size(label)[0]
            lx = rx + (rw - lw) // 2
            ls = font_small.render(label, True, (160, 160, 155))
            surface.blit(ls, (lx, ry + rh - 28))
            pygame.draw.rect(surface, (50, 50, 50), self.rect, 1, border_radius=12)
 
    def get_play_btn_rect(self):
        rx, ry, rw, rh = self.rect
        cx, cy = rx + rw // 2, ry + rh // 2
        return pygame.Rect(cx - 32, cy - 32, 64, 64)
 
# Buttons
 
class ChoiceButton:
    ANIM_DURATION = 0.35
 
    def __init__(self, rect, text, index):
        self.rect = pygame.Rect(rect)
        self.text = text 
        self.index = index
        self.state = "idle"   # idle, hover, correct, wrong, reveal
        self.anim_t = 0.0
        self._offset_x = 0
 
    def update(self, dt, mouse_pos, answered):
        if self.state in ("correct", "wrong", "reveal"):
            if self.anim_t < self.ANIM_DURATION:
                self.anim_t += dt
            return
 
        if answered:
            self.state = "idle"
            return
 
        if self.rect.collidepoint(mouse_pos):
            self.state = "hover"
        else:
            self.state = "idle"
 
    def trigger(self, result):
        self.state = result
        self.anim_t = 0.0
 
    def draw(self, surface, font):
        r = self.rect
        progress = min(self.anim_t / self.ANIM_DURATION, 1.0)
 
        if self.state == "correct":
            # Pop-in scale
            scale = 1.0 + 0.04 * math.sin(progress * math.pi)
            bg, bdr, tc = C_CORRECT_BG, C_CORRECT_BDR, C_CORRECT_TXT
        elif self.state == "wrong":
            # Shake offset
            if progress < 1.0:
                self._offset_x = int(6 * math.sin(progress * math.pi * 4) * (1 - progress))
            else:
                self._offset_x = 0
            scale = 1.0
            bg, bdr, tc = C_WRONG_BG, C_WRONG_BDR, C_WRONG_TXT
        elif self.state == "reveal":
            scale = 1.0
            bg, bdr, tc = C_CORRECT_BG, C_CORRECT_BDR, C_CORRECT_TXT
        elif self.state == "hover":
            scale = 1.0
            bg, bdr, tc = (238, 237, 254), C_ACCENT, C_TEXT
        else:
            scale = 1.0
            bg, bdr, tc = C_SURFACE, C_BORDER, C_TEXT
 
        dx = getattr(self, "_offset_x", 0)
        draw_r = (r.x + dx, r.y, r.width, r.height)
        draw_rounded_rect(surface, bg, draw_r, radius=10, border=1, border_color=bdr)
 
        pad = 14
        text_rect = (r.x + dx + pad, r.y, r.width - pad * 2, r.height)
        draw_text(surface, self.text, font, tc, text_rect, align="left", valign="center", wrap=True)
 
# Main
 
class QuizGame:
    STATE_QUESTION = "question"
    STATE_ANSWERED = "answered"
    STATE_END      = "end"
 
    def __init__(self):
        pygame.init()
        pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=2, buffer=512)
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        # Fonts
        self.font_lg = load_cjk_font(20)
        self.font_md = load_cjk_font(16)
        self.font_sm = load_cjk_font(13)
        self.font_bold = load_cjk_font(17, bold=True)
        self.font_xl = load_cjk_font(48)
        # Sounds
        self.snd_correct = pygame.mixer.Sound(SOUND_CORRECT)
        self.snd_wrong = pygame.mixer.Sound(SOUND_WRONG)
        # Misc
        self.current = 0
        self.score = 0
        self.state = self.STATE_QUESTION
        # Layout constants
        PAD = 24
        self.video_rect = ((WINDOW_W / 2) - (1080 / 2), 12, 1080, 720) #1080, 720
        self.video_player = VideoPlayer(self.video_rect)
 
        self._load_question()
 
    def _load_question(self):
        self.state = self.STATE_QUESTION
        self.video_player.stop()
        q = QUESTIONS[self.current]
        self.video_player.load(q["video"])
 
        # Build choice buttons
        PAD = 24
        btn_top = 386 + 460 # video + progress + question
        cols = 2
        rows = math.ceil(len(q["choices"]) / cols)
        btn_w = (WINDOW_W - PAD * 2 - 10) // cols
        btn_h = 58
 
        self.buttons = []
        for i, text in enumerate(q["choices"]):
            col = i % cols
            row = i // cols
            bx = PAD + col * (btn_w + 10)
            by = btn_top + row * (btn_h + 10)
            self.buttons.append(ChoiceButton((bx, by, btn_w, btn_h), text, i))
 
        # Next button
        nb_y = btn_top + rows * (btn_h + 10) + 10
        self.next_btn_rect = pygame.Rect(PAD, nb_y, WINDOW_W - PAD * 2, 44)
        self.show_next = False
        self.feedback_text = ""
        self.feedback_color = C_MUTED
 
        # Restart button (end screen)
        self.restart_btn_rect = pygame.Rect(WINDOW_W // 2 - 100, 420, 200, 44)
 
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return False
 
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mp = event.pos
 
            if self.state == self.STATE_END:
                if self.restart_btn_rect.collidepoint(mp):
                    self.current = 0
                    self.score = 0
                    self._load_question()
                return True
 
            # Video play button
            if not self.video_player.playing:
                if self.video_player.get_play_btn_rect().collidepoint(mp):
                    self.video_player.play()
 
            # Choice buttons
            if self.state == self.STATE_QUESTION:
                for btn in self.buttons:
                    if btn.rect.collidepoint(mp):
                        self._answer(btn.index)
                        break
 
            # Next button
            if self.state == self.STATE_ANSWERED and self.show_next:
                if self.next_btn_rect.collidepoint(mp):
                    self._advance()
        return True
 
    def _answer(self, idx):
        self.state = self.STATE_ANSWERED
        q = QUESTIONS[self.current]
        correct = q["correct"]
        for btn in self.buttons:
            if btn.index == idx:
                if idx == correct:
                    btn.trigger("correct")
                else:
                    btn.trigger("wrong")
            elif btn.index == correct and idx != correct:
                btn.trigger("reveal")
 
        if idx == correct:
            self.score += 1
            self.snd_correct.play()
            self.feedback_text = "Correct!"
            self.feedback_color = C_CORRECT_TXT
        else:
            self.snd_wrong.play()
            self.feedback_text = f"Not quite — answer: {q['choices'][correct]}"
            self.feedback_color = C_MUTED
 
        is_last = self.current == len(QUESTIONS) - 1
        self._next_label = "See results" if is_last else "Next question  →"
        self.show_next = True
 
    def _advance(self):
        self.current += 1
        if self.current >= len(QUESTIONS):
            self.state = self.STATE_END
        else:
            self._load_question()
 
    def update(self, dt):
        mp = pygame.mouse.get_pos()
        answered = self.state != self.STATE_QUESTION
        for btn in self.buttons:
            btn.update(dt, mp, answered)
        self.video_player.update(dt)
 
    def draw(self):
        self.screen.fill(C_BG)
 
        if self.state == self.STATE_END:
            self._draw_end()
        else:
            self._draw_question()
 
        pygame.display.flip()
 
    def _draw_question(self):
        ##
        ## + 490 FOR ALL Y-AXIS CONSTANT
        ##
        PAD = 24
        q = QUESTIONS[self.current]
 
        # Video
        self.video_player.draw(self.screen, self.font_sm, q["video_label"])
 
        # Progress bar
        bar_y = 24 + 220 + 14 + 490
        bar_h = 5
        total = len(QUESTIONS)
        fill_w = int(((self.current + 1) / total) * (WINDOW_W - PAD * 2))
        pygame.draw.rect(self.screen, C_BORDER, (PAD, bar_y, WINDOW_W - PAD * 2, bar_h), border_radius=3)
        pygame.draw.rect(self.screen, C_ACCENT, (PAD, bar_y, fill_w, bar_h), border_radius=3)
 
        # Quesetion label and score
        ql = self.font_sm.render(f"Question {self.current + 1} of {total}", True, C_MUTED)
        self.screen.blit(ql, (PAD, bar_y + bar_h + 6))
        sc = self.font_sm.render(f"{self.score} / {total}", True, C_TEXT)
        self.screen.blit(sc, (WINDOW_W - PAD - sc.get_width(), bar_y + bar_h + 6))
 
        # Question text
        q_top = bar_y + bar_h + 6 + 20
        draw_text(self.screen, q["question"], self.font_bold, C_TEXT,
                  (PAD, q_top, WINDOW_W - PAD * 2, 60), align="left", valign="top", wrap=True)
 
        # Choice buttons
        for btn in self.buttons:
            btn.draw(self.screen, self.font_md)
 
        # Feedback
        if self.feedback_text:
            fb = self.font_sm.render(self.feedback_text, True, self.feedback_color)
            self.screen.blit(fb, (WINDOW_W // 2 - fb.get_width() // 2,
                                   self.next_btn_rect.y - 7))
 
        # Next button
        if self.show_next:
            mp = pygame.mouse.get_pos()
            hovered = self.next_btn_rect.collidepoint(mp)
            nbg = C_ACCENT_DARK if hovered else C_ACCENT
            draw_rounded_rect(self.screen, nbg,
                               (self.next_btn_rect.x, self.next_btn_rect.y + 15,
                                self.next_btn_rect.width, self.next_btn_rect.height),
                               radius=10)
            nl = self.font_bold.render(self._next_label, True, C_WHITE)
            nx = self.next_btn_rect.x + (self.next_btn_rect.width - nl.get_width()) // 2
            ny = self.next_btn_rect.y + (self.next_btn_rect.height - nl.get_height()) // 2 + 15
            self.screen.blit(nl, (nx, ny))
 
    def _draw_end(self):
        total = len(QUESTIONS)
 
        # Score
        sc_txt = self.font_xl.render(f"{self.score}/{total}", True, C_ACCENT)
        self.screen.blit(sc_txt, (WINDOW_W // 2 - sc_txt.get_width() // 2, 180))
 
        # Message
        msgs = ["Nice try — have another go!", "Good effort! One more round?", "Well done!", "Perfect score!"]
        msg = msgs[min(self.score, len(msgs) - 1)]
        ms = self.font_lg.render(msg, True, C_MUTED)
        self.screen.blit(ms, (WINDOW_W // 2 - ms.get_width() // 2, 260))
 
        # Restart button
        mp = pygame.mouse.get_pos()
        hovered = self.restart_btn_rect.collidepoint(mp)
        rbg = (230, 230, 225) if hovered else C_SURFACE
        draw_rounded_rect(self.screen, rbg,
                           (self.restart_btn_rect.x, self.restart_btn_rect.y,
                            self.restart_btn_rect.width, self.restart_btn_rect.height),
                           radius=10, border=1, border_color=C_BORDER)
        rl = self.font_bold.render("Try again", True, C_TEXT)
        rx = self.restart_btn_rect.x + (self.restart_btn_rect.width - rl.get_width()) // 2
        ry = self.restart_btn_rect.y + (self.restart_btn_rect.height - rl.get_height()) // 2
        self.screen.blit(rl, (rx, ry))
 
    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if not self.handle_event(event):
                    pygame.quit()
                    sys.exit()
            self.update(dt)
            self.draw()
 
 
if __name__ == "__main__":
    QuizGame().run()
