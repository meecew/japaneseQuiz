import pygame
import sys
import math
import numpy as np
import cv2
import random
import time

####
#### TO DO: POSSBILY SHUFFLING?!
####

# Config
WINDOW_W, WINDOW_H = 1920, 1080
FPS = 60
TITLE = "QUUIIZZ"
 
# Audios
SOUND_CORRECT = "sound_success.mp3"
SOUND_WRONG = ["sound_failed.mp3", "boom.mp3"]
SOUND_WIN = ["win.mp3", "win2.mp3"]

SAMPLE_RATE = 44100
JUMPSCARE_IMAGES_SUCCESS = [
    "successPic.jpg",  
    "successPic.jpg",   
    "successPic.jpg",   
]
JUMPSCARE_IMAGES_FAILED = [
    "failedPic.jpg",  
    "failedPic.jpg",   
    "failedPic.jpg",   
]
JUMPSCARE_IMAGES_WIN = [
    "win.jpg",
    "win2.jpg"
]

JUMPSCARE_DURATION = 1.8   
JUMPSCARE_HOLD     = 0.18  

QUESTIONS = [
    {
        "video": None,                          
        "video_label": "Clip 1",
        "question": "test 1",
        "choices": ["0", "1", "2", "3"],
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
        "question": "Wow, they're eating food and it looks great!!! (yum)\nAs they're eating the school lunch noodles, one of them commented…\n絶妙にコシがないし (zetsumyo no koshi ga naishi)\nAccording to him, how are the noodles?",
        "choices": ["They're really spicy.", "They're perfectly al dente with a firm chew", "They're oddly lacking in bite—soft and a bit soggy.", "They're sweet and buttery"],
        "correct": 2,
    },
]
 
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
C_CTRL_BG     = ( 30,  30,  30)   
C_CTRL_HOVER  = ( 55,  55,  55)   

# ^
#/|\
# |
# |
# |
# DOESNT THAT LOOK SO CLEAN?!?!



# from here (#0)

def load_cjk_font(size, bold=False):
    candidates = [
        "msgothic", "msgothic.ttc",
        "yugothic", "yugothic.ttc",
        #"meiryo", "meiryo.ttc", KIKI FUNG CAN NOT SEE THIS TINY AHH FONT I JUST KNOW
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
    print("[WARNING] No CJK-capable font found.")
    return pygame.font.SysFont(None, size, bold=bold)

# to here (#0)
# ripped out of the internet again

def draw_rounded_rect(surface, color, rect, radius=10, border=0, border_color=None):
    x, y, w, h = rect
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border and border_color:
        pygame.draw.rect(surface, border_color, rect, border, border_radius=radius)


def draw_text(surface, text, font, color, rect, align="left", valign="top", wrap=True):
    x, y, w, h = rect
    if wrap:
        paragraphs = text.split("\n")
        lines = []
        for para in paragraphs:
            words = para.split()
            if not words:
                lines.append("")
                continue
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
        lines = text.split("\n")

    total_h = len(lines) * font.get_linesize()
    start_y = y + (h - total_h) // 2 if valign == "center" else y

    for line in lines:
        surf = font.render(line, True, color)
        lw = surf.get_width()
        lx = x + (w - lw) // 2 if align == "center" else (x + w - lw if align == "right" else x)
        surface.blit(surf, (lx, start_y))
        start_y += font.get_linesize()


def measure_text_height(text, font, width):
    paragraphs = text.split("\n")
    lines = []
    for para in paragraphs:
        words = para.split()
        if not words:
            lines.append("")
            continue
        current = []
        for word in words:
            test = " ".join(current + [word])
            if font.size(test)[0] <= width:
                current.append(word)
            else:
                if current:
                    lines.append(" ".join(current))
                current = [word]
        if current:
            lines.append(" ".join(current))
    return len(lines) * font.get_linesize()


# Video player
# I rip this part off the internet

CTRL_H      = 44   # height of the controls bar
CTRL_BTN_W  = 56   
CTRL_RADIUS = 6

class VideoPlayer:
    def __init__(self, rect):
        self.rect = rect           
        self.cap = None
        self.frame_surf = None
        self.playing = False
        self.loaded = False
        self.finished = False      
        self.fps = 30
        self._frame_timer = 0
        self._total_frames = 0
        self._current_frame = 0

        rx, ry, rw, rh = rect
        self.video_area = (rx, ry, rw, rh - CTRL_H)
        self._build_ctrl_rects()

    def _build_ctrl_rects(self):
        rx, ry, rw, rh = self.rect
        bar_y = ry + rh - CTRL_H
        self.btn_play_rect  = pygame.Rect(rx + 8, bar_y + (CTRL_H - 36) // 2, 36, 36)
        self.btn_replay_rect_inside = pygame.Rect(rx + 14 + 36 + 8, bar_y + (CTRL_H - 36) // 2 + 6, 24, 24)
        self.btn_replay_rect = pygame.Rect(rx + 8 + 36 + 8, bar_y + (CTRL_H - 36) // 2, 36, 36)
        pb_x = rx + 8 + 36 + 8 + 36 + 12
        pb_w = rw - (pb_x - rx) - 12
        self.progressbar_rect = pygame.Rect(pb_x, bar_y + CTRL_H // 2 - 3, pb_w, 6)

    def load(self, path):
        self.loaded = False
        self.finished = False
        self.frame_surf = None
        self.playing = False
        self._current_frame = 0
        if path is None:
            return False
        try:
            self.cap = cv2.VideoCapture(path)
            if not self.cap.isOpened():
                self.cap = None
                return False
            self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30
            self._total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.loaded = True
            return True
        except Exception:
            return False

    def play(self):
        if self.cap:
            self.playing = True
            self.finished = False
            self._frame_timer = 0

    def pause(self):
        self.playing = False

    def toggle_play_pause(self):
        if not self.loaded:
            return
        if self.finished:
            self.replay()
            return
        if self.playing:
            self.pause()
        else:
            self.play()

    def replay(self):
        if self.cap:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self._current_frame = 0
            self.finished = False
            self.playing = True
            self._frame_timer = 0

    def stop(self):
        self.playing = False
        self.finished = False
        self._current_frame = 0
        if self.cap:
            self.cap.release()
            self.cap = None
        self.frame_surf = None
        self.loaded = False

    def update(self, dt):
        if not self.playing or not self.cap:
            return
        self._frame_timer += dt
        frame_interval = 1.0 / self.fps
        while self._frame_timer >= frame_interval:
            self._frame_timer -= frame_interval
            ret, frame = self.cap.read()
            if not ret:
                self.playing = False
                self.finished = True
                return
            self._current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            vx, vy, vw, vh = self.video_area
            frame = cv2.resize(frame, (vw, vh))
            self.frame_surf = pygame.surfarray.make_surface(frame.swapaxes(0, 1))

    def handle_click(self, pos):
        """Call from the main event loop. Returns True if consumed."""
        if self.btn_play_rect.collidepoint(pos):
            self.toggle_play_pause()
            return True
        if self.btn_replay_rect.collidepoint(pos):
            self.replay()
            return True
        if self.progressbar_rect.collidepoint(pos) and self.loaded and self._total_frames > 0:
            ratio = (pos[0] - self.progressbar_rect.x) / self.progressbar_rect.width
            ratio = max(0.0, min(1.0, ratio))
            target = int(ratio * self._total_frames)
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, target)
            self._current_frame = target
            self.finished = False
            return True
        return False

    # Render

    def draw(self, surface, font_small, label, mouse_pos):
        rx, ry, rw, rh = self.rect
        vx, vy, vw, vh = self.video_area
        bar_y = ry + rh - CTRL_H

        # Video frame area
        pygame.draw.rect(surface, C_VIDEO_BG, (vx, vy, vw, vh), border_radius=0)
        if self.frame_surf:
            surface.blit(self.frame_surf, (vx, vy))
        else:
            cx, cy = vx + vw // 2, vy + vh // 2
            lw = font_small.size(label)[0]
            lx = vx + (vw - lw) // 2
            ls = font_small.render(label, True, (160, 160, 155))
            surface.blit(ls, (lx, vy + vh - 28))
            if not self.loaded:
                nv = font_small.render("No video :(", True, (100, 100, 95))
                surface.blit(nv, (cx - nv.get_width() // 2, cy - nv.get_height() // 2))

        if self.finished and self.frame_surf:
            overlay = pygame.Surface((vw, vh), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 110))
            surface.blit(overlay, (vx, vy))
            fin_font = font_small
            ft = fin_font.render("Video ended  —  press ↺ to replay", True, (200, 200, 195))
            surface.blit(ft, (vx + vw // 2 - ft.get_width() // 2, vy + vh // 2 - ft.get_height() // 2))

        pygame.draw.rect(surface, C_CTRL_BG, (rx, bar_y, rw, CTRL_H))
        ph = self.btn_play_rect.collidepoint(mouse_pos)
        pbg = C_CTRL_HOVER if ph else C_CTRL_BG
        pygame.draw.rect(surface, pbg, self.btn_play_rect, border_radius=CTRL_RADIUS)
        bx, by, bw, bh = self.btn_play_rect
        cx, cy = bx + bw // 2, by + bh // 2
        if self.playing:
            pygame.draw.rect(surface, C_WHITE, (cx - 7, cy - 8, 5, 16))
            pygame.draw.rect(surface, C_WHITE, (cx + 2, cy - 8, 5, 16))
        else:
            pts = [(cx - 7, cy - 10), (cx + 11, cy), (cx - 7, cy + 10)]
            pygame.draw.polygon(surface, C_WHITE, pts)

        rh2 = self.btn_replay_rect.collidepoint(mouse_pos)
        rbg = C_CTRL_HOVER if rh2 else C_CTRL_BG
        pygame.draw.rect(surface, rbg, self.btn_replay_rect, border_radius=CTRL_RADIUS)
        pygame.draw.rect(surface, C_WHITE, self.btn_replay_rect_inside, border_radius=CTRL_RADIUS)


        pr = self.progressbar_rect

        pygame.draw.rect(surface, (70, 70, 70), pr, border_radius=3)

        if self.loaded and self._total_frames > 0:
            ratio = self._current_frame / self._total_frames
            fill_w = int(pr.width * ratio)
            if fill_w > 0:
                pygame.draw.rect(surface, C_ACCENT, (pr.x, pr.y, fill_w, pr.height), border_radius=3)

            dot_x = pr.x + fill_w
            pygame.draw.circle(surface, C_WHITE, (dot_x, pr.y + pr.height // 2), 6)


        pygame.draw.rect(surface, (50, 50, 50), self.rect, 1, border_radius=12)


# Choice buttons

class ChoiceButton:
    ANIM_DURATION = 0.35

    def __init__(self, rect, text, index):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.index = index
        self.state = "idle"
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
        self.state = "hover" if self.rect.collidepoint(mouse_pos) else "idle"

    def trigger(self, result):
        self.state = result
        self.anim_t = 0.0

    def draw(self, surface, font):
        r = self.rect
        progress = min(self.anim_t / self.ANIM_DURATION, 1.0)

        if self.state == "correct":
            bg, bdr, tc = C_CORRECT_BG, C_CORRECT_BDR, C_CORRECT_TXT
        elif self.state == "wrong":
            self._offset_x = int(6 * math.sin(progress * math.pi * 4) * (1 - progress)) if progress < 1.0 else 0
            bg, bdr, tc = C_WRONG_BG, C_WRONG_BDR, C_WRONG_TXT
        elif self.state == "reveal":
            bg, bdr, tc = C_CORRECT_BG, C_CORRECT_BDR, C_CORRECT_TXT
        elif self.state == "hover":
            bg, bdr, tc = (238, 237, 254), C_ACCENT, C_TEXT
        else:
            bg, bdr, tc = C_SURFACE, C_BORDER, C_TEXT

        dx = getattr(self, "_offset_x", 0)
        draw_r = (r.x + dx, r.y, r.width, r.height)
        draw_rounded_rect(surface, bg, draw_r, radius=10, border=1, border_color=bdr)
        pad = 14
        draw_text(surface, self.text, font, tc,
                  (r.x + dx + pad, r.y, r.width - pad * 2, r.height),
                  align="left", valign="center", wrap=True)

# So called jump scare, maybe not that scary
class JumpScare:
    """Loads a jpg, slams it fullscreen, holds briefly, then fades out."""

    def __init__(self):
        self._surf   = None   # scaled surface
        self._alpha  = 0.0    # 0.0 – 255.0
        self._timer  = 0.0
        self.active  = False

    def trigger(self, image_path):
        try:
            raw = pygame.image.load(image_path).convert()
            self._surf = pygame.transform.scale(raw, (WINDOW_W, WINDOW_H))
        except Exception as e:
            print(f"[JumpScare] Could not load {image_path}: {e}")
            self._surf = None
            return
        self._alpha = 255.0
        self._timer = 0.0
        self.active = True

    def update(self, dt):
        if not self.active:
            return
        self._timer += dt
        if self._timer < JUMPSCARE_HOLD:
            self._alpha = 255.0
        else:
            # fade from 255 → 0 over the remaining duration
            fade_elapsed = self._timer - JUMPSCARE_HOLD
            fade_total   = JUMPSCARE_DURATION - JUMPSCARE_HOLD
            progress     = fade_elapsed / fade_total
            self._alpha  = max(0.0, 255.0 * (1.0 - progress))
            if self._alpha <= 0:
                self.active = False

    def draw(self, surface):
        if not self.active or self._surf is None:
            return
        self._surf.set_alpha(int(self._alpha))
        surface.blit(self._surf, (0, 0))

# Main game

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

        self.font_lg   = load_cjk_font(24)
        self.font_md   = load_cjk_font(20, bold=True)
        self.font_sm   = load_cjk_font(13)
        self.font_bold = load_cjk_font(28)
        self.font_xl   = load_cjk_font(48)

        self.snd_correct = pygame.mixer.Sound(SOUND_CORRECT)
        self.snd_wrong   = pygame.mixer.Sound(SOUND_WRONG[random.randint(0, 1)])
        

        self.current = 0
        self.score   = 0
        self.timesFailed = 0
        self.state   = self.STATE_QUESTION
        self.canAdv = True
        self.jumpscare = JumpScare()

        PAD = 24

        VIDEO_W, VIDEO_H = 720, 480 + CTRL_H
        self.video_rect = (
            (WINDOW_W - VIDEO_W) // 2,
            12,
            VIDEO_W,
            VIDEO_H,
        )
        self.video_player = VideoPlayer(self.video_rect)
        self._load_question()

    # layout organize

    def _layout(self):
        """Recompute all Y positions based on current question text height."""
        PAD = 24
        _, vy, _, vh = self.video_rect
        VIDEO_BOTTOM = vy + vh          

        BAR_Y   = VIDEO_BOTTOM + 14
        BAR_H   = 5
        LABEL_Y = BAR_Y + BAR_H + 6
        LABEL_H = self.font_sm.get_linesize()
        Q_TOP   = LABEL_Y + LABEL_H + 10

        q = QUESTIONS[self.current]
        q_h = measure_text_height(q["question"], self.font_bold, WINDOW_W - PAD * 2)
        q_h = max(q_h, self.font_bold.get_linesize())

        btn_top = Q_TOP + q_h + 14

        self._bar_y   = BAR_Y
        self._bar_h   = BAR_H
        self._label_y = LABEL_Y
        self._q_top   = Q_TOP
        self._q_h     = q_h
        self._btn_top = btn_top

    def _load_question(self):
        self.state = self.STATE_QUESTION
        self.video_player.stop()
        q = QUESTIONS[self.current]
        self.video_player.load(q["video"])

        self._layout()

        PAD = 24
        btn_top = self._btn_top
        cols   = 2
        rows   = math.ceil(len(q["choices"]) / cols)
        btn_w  = (WINDOW_W - PAD * 2 - 10) // cols
        btn_h  = 58

        self.buttons = []
        for i, text in enumerate(q["choices"]):
            col = i % cols
            row = i // cols
            self.buttons.append(ChoiceButton(
                (PAD + col * (btn_w + 10), btn_top + row * (btn_h + 10), btn_w, btn_h),
                text, i
            ))

        nb_y = btn_top + rows * (btn_h + 10) + 10
        self.next_btn_rect = pygame.Rect(PAD, nb_y, WINDOW_W - PAD * 2, 44)
        self.show_next     = False
        self.feedback_text = ""
        self.feedback_color = C_MUTED

        self.restart_btn_rect = pygame.Rect(WINDOW_W // 2 - 100, 500, 200, 44)

    # events

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mp = event.pos

            if self.state == self.STATE_END:
                if self.restart_btn_rect.collidepoint(mp):
                    self.current = 0
                    self.score   = 0
                    self._load_question()
                return True

            if self.video_player.handle_click(mp):
                return True

            if self.state == self.STATE_QUESTION:
                for btn in self.buttons:
                    if btn.rect.collidepoint(mp):
                        self._answer(btn.index)
                        break

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
                btn.trigger("correct" if idx == correct else "wrong")
            elif btn.index == correct and idx != correct:
                btn.trigger("reveal")

        if idx == correct:
            self.score += 1
            self.snd_correct.play()
            self.feedback_text  = "Correct!"
            self.feedback_color = C_CORRECT_TXT
            self.canAdv = True
            if self.current < len(JUMPSCARE_IMAGES_SUCCESS) and JUMPSCARE_IMAGES_SUCCESS[self.current]:
                self.jumpscare.trigger(JUMPSCARE_IMAGES_SUCCESS[self.current])
        else:
            self.snd_wrong   = pygame.mixer.Sound(SOUND_WRONG[0])
            for j in range(self.timesFailed + 1):
                self.snd_wrong.play()
                self.snd_wrong   = pygame.mixer.Sound(SOUND_WRONG[1])
                
            self.feedback_text  = f"GO BACK!!!!!!"
            self.feedback_color = C_MUTED
            self.canAdv = False
            if self.current < len(JUMPSCARE_IMAGES_FAILED) and JUMPSCARE_IMAGES_FAILED[self.current]:
                self.jumpscare.trigger(JUMPSCARE_IMAGES_FAILED[self.current])


        self._next_label = "See results" if self.current == len(QUESTIONS) - 1 else "Next question  →"
        self.show_next = True

    def _advance(self):
        if self.canAdv == True:
            self.current += 1
        else:
            self.current = 0
            self.score = 0
            self.timesFailed += 1
        if self.current >= len(QUESTIONS):
            self.state = self.STATE_END
            self.timesFailed = 0
            self.snd_win = pygame.mixer.Sound(SOUND_WIN[0])
            self.snd_win.play()
            #self.jumpscare.trigger(JUMPSCARE_IMAGES_WIN[0])

            self.snd_win = pygame.mixer.Sound(SOUND_WIN[1])
            self.snd_win.play()

            
            
            self.jumpscare.trigger(JUMPSCARE_IMAGES_WIN[1])
        else:
            self._load_question()

    # Update, draw

    def update(self, dt):
        mp = pygame.mouse.get_pos()
        answered = self.state != self.STATE_QUESTION
        for btn in self.buttons:
            btn.update(dt, mp, answered)
        self.video_player.update(dt)

        self.jumpscare.update(dt) 

    def draw(self):
        self.screen.fill(C_BG)
        if self.state == self.STATE_END:
            self._draw_end()
        else:
            self._draw_question()
        self.jumpscare.draw(self.screen)  
        pygame.display.flip()

    def _draw_question(self):
        PAD = 24
        q   = QUESTIONS[self.current]
        mp  = pygame.mouse.get_pos()

        self.video_player.draw(self.screen, self.font_sm, q["video_label"], mp)

        # Progress bar
        total  = len(QUESTIONS)
        fill_w = int(((self.current + 1) / total) * (WINDOW_W - PAD * 2))
        pygame.draw.rect(self.screen, C_BORDER, (PAD, self._bar_y, WINDOW_W - PAD * 2, self._bar_h), border_radius=3)
        pygame.draw.rect(self.screen, C_ACCENT, (PAD, self._bar_y, fill_w, self._bar_h), border_radius=3)

        ql = self.font_sm.render(f"Question {self.current + 1} of {total}", True, C_MUTED)
        self.screen.blit(ql, (PAD, self._label_y))
        sc = self.font_sm.render(f"{self.score} / {total}", True, C_TEXT)
        self.screen.blit(sc, (WINDOW_W - PAD - sc.get_width(), self._label_y))

        draw_text(self.screen, q["question"], self.font_bold, C_TEXT,
                  (PAD, self._q_top, WINDOW_W - PAD * 2, self._q_h + 8),
                  align="left", valign="top", wrap=True)

        for btn in self.buttons:
            btn.draw(self.screen, self.font_md)

        if self.feedback_text:
            fb = self.font_sm.render(self.feedback_text, True, self.feedback_color)
            self.screen.blit(fb, (WINDOW_W // 2 - fb.get_width() // 2, self.next_btn_rect.y - 7))

        if self.show_next:
            hovered = self.next_btn_rect.collidepoint(mp)
            nbg = C_ACCENT_DARK if hovered else C_ACCENT
            draw_rounded_rect(self.screen, nbg,
                               (self.next_btn_rect.x, self.next_btn_rect.y + 15,
                                self.next_btn_rect.width, self.next_btn_rect.height),
                               radius=10)
            nl = self.font_bold.render(self._next_label, True, C_WHITE)
            self.screen.blit(nl, (
                self.next_btn_rect.x + (self.next_btn_rect.width  - nl.get_width())  // 2,
                self.next_btn_rect.y + (self.next_btn_rect.height - nl.get_height()) // 2 + 15,
            ))

    def _draw_end(self):
        
        total  = len(QUESTIONS)
        sc_txt = self.font_xl.render(f"{self.score}/{total}", True, C_ACCENT)
        self.screen.blit(sc_txt, (WINDOW_W // 2 - sc_txt.get_width() // 2, 380))

        msgs = ["how..?", "how....?", "how....?", "YAAATTAAA!!!!!"]
        ms   = self.font_lg.render(msgs[min(self.score, len(msgs) - 1)], True, C_MUTED)
        self.screen.blit(ms, (WINDOW_W // 2 - ms.get_width() // 2, 460))

        mp     = pygame.mouse.get_pos()
        hovered = self.restart_btn_rect.collidepoint(mp)
        draw_rounded_rect(self.screen,
                           (230, 230, 225) if hovered else C_SURFACE,
                           (self.restart_btn_rect.x, self.restart_btn_rect.y,
                            self.restart_btn_rect.width, self.restart_btn_rect.height),
                           radius=10, border=1, border_color=C_BORDER)
        rl = self.font_bold.render("Try again", True, C_TEXT)
        self.screen.blit(rl, (
            self.restart_btn_rect.x + (self.restart_btn_rect.width  - rl.get_width())  // 2,
            self.restart_btn_rect.y + (self.restart_btn_rect.height - rl.get_height()) // 2,
        ))

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