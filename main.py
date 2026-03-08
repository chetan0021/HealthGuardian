import sys
import os
import urllib.request
import winsound
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QSystemTrayIcon,
                             QMenu, QStyle, QGraphicsDropShadowEffect, QDialog, QCheckBox, 
                             QGraphicsOpacityEffect)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRectF, pyqtSignal, QPointF, QPoint
from PyQt6.QtGui import QIcon, QFont, QColor, QPainter, QPen, QAction, QFontDatabase, QPolygonF

# Download the Digital-7 font if it doesn't exist
FONT_PATH = "DSEG7Classic-Bold.ttf"
FONT_NAME = "DSEG7 Classic"
if not os.path.exists(FONT_PATH):
    print("Downloading 7-segment font for Jarvis theme...")
    try:
        url = "https://raw.githubusercontent.com/keshikan/DSEG/master/fonts/DSEG7-Classic/DSEG7Classic-Bold.ttf"
        urllib.request.urlretrieve(url, FONT_PATH)
    except Exception as e:
        print(f"Failed to download font: {e}")

APP_SETTINGS = {
    'enable_popups': True,
    'play_sound': True,
    'run_in_background': True
}

# Configuration Data
TIMERS_CONF = {
    '20': {'duration': 20 * 60, 'break_duration': 20, 'title': '20-20-20 Rule', 'message': 'LOOK 20 FEET AWAY', 'color': '#00f2fe'},
    '60': {'duration': 60 * 60, 'break_duration': 60, 'title': 'Hydration Time', 'message': 'DRINK WATER', 'color': '#0078FF'},
    '120': {'duration': 120 * 60, 'break_duration': 15 * 60, 'title': 'Long Break', 'message': 'STEP AWAY FROM PC', 'color': '#f093fb'}
}

class CyberPanel(QWidget):
    def __init__(self, color_str, bg_alpha=240, border_width=2, parent=None):
        super().__init__(parent)
        self.color = QColor(color_str)
        self.bg_alpha = bg_alpha
        self.border_width = border_width
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        corner = 30.0
        w = float(self.width())
        h = float(self.height())
        poly = QPolygonF([
            QPointF(corner, 1),
            QPointF(w - corner, 1),
            QPointF(w - 1, corner),
            QPointF(w - 1, h - corner),
            QPointF(w - corner, h - 1),
            QPointF(corner, h - 1),
            QPointF(1, h - corner),
            QPointF(1, corner)
        ])
        
        painter.setBrush(QColor(5, 5, 10, self.bg_alpha))
        pen = QPen(self.color, self.border_width)
        painter.setPen(pen)
        painter.drawPolygon(poly)

class CircularProgress(QWidget):
    timer_finished = pyqtSignal(str)

    def __init__(self, timer_id, parent=None):
        super().__init__(parent)
        self.timer_id = timer_id
        self.conf = TIMERS_CONF[timer_id]
        self.max_time = self.conf['duration']
        self.time_left = self.max_time
        
        self.setFixedSize(180, 210)
        self.color = QColor(self.conf['color'])
        
        # Internal Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.is_running = True

    def update_timer(self):
        if not self.is_running: return
        self.time_left -= 1
        if self.time_left <= 0:
            self.time_left = self.max_time
            # Emit custom signal to main window, and KEEP TICKING independently
            self.timer_finished.emit(self.timer_id)
        self.update()

    def play_pause(self):
        self.is_running = not self.is_running
        self.update()

    def reset(self):
        self.time_left = self.max_time
        self.is_running = True
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = QRectF(15, 15, self.width()-30, self.width()-30)
        
        fraction = self.time_left / self.max_time
        span_angle = int(-fraction * 360 * 16)
        
        # Draw Glow (Thicker, semi-transparent arc beneath)
        c_glow = QColor(self.color)
        c_glow.setAlpha(80)
        pen_glow = QPen(c_glow)
        pen_glow.setWidth(20)
        pen_glow.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_glow)
        painter.drawArc(rect, 90 * 16, span_angle)
        
        # Background Circle
        c_bg = QColor(self.color)
        c_bg.setAlpha(20)
        pen_bg = QPen(c_bg)
        pen_bg.setWidth(6)
        painter.setPen(pen_bg)
        painter.drawEllipse(rect)
        
        # Foreground Arc (Neon)
        pen_fg = QPen(self.color)
        pen_fg.setWidth(8)
        pen_fg.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_fg)
        painter.drawArc(rect, 90 * 16, span_angle)
        
        # Text
        minutes = self.time_left // 60
        seconds = self.time_left % 60
        time_str = f"{minutes:02d}:{seconds:02d}"
        
        painter.setPen(self.color)
        font = QFont(FONT_NAME, 26, QFont.Weight.Bold)
        if FONT_NAME not in QFontDatabase.families(): font = QFont("Consolas", 26, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, time_str)
        
        # Status Text placed distinctly below the circle
        painter.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
        status_rect = QRectF(0, 185, 180, 25)
        painter.drawText(status_rect, Qt.AlignmentFlag.AlignCenter, "ACTIVE" if self.is_running else "PAUSED")
        
        painter.end()


class AlertOverlay(QWidget):
    def __init__(self, conf):
        super().__init__()
        self.conf = conf
        self.color = conf['color']
        self.break_duration = conf['break_duration']
        self.time_left = self.break_duration
        
        self.setWindowFlags(
            Qt.WindowType.Window | 
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        
        # Native window fade in animation
        self.setWindowOpacity(0.0)
        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(500)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.panel = CyberPanel(self.color, 240, 2, self)
        self.panel.setFixedSize(700, 450)
        self.panel.setStyleSheet(f"""
            QLabel#title {{
                color: {self.color};
                font-family: 'Consolas';
                font-size: 32px;
                font-weight: bold;
                border: none;
                background: transparent;
            }}
            QLabel#timer {{
                color: {self.color};
                font-size: 80px;
                border: none;
                background: transparent;
            }}
            QLabel#msg {{
                color: #ffffff;
                font-family: 'Consolas';
                font-size: 20px;
                border: none;
                background: transparent;
                margin-top: 5px;
            }}
            QPushButton {{
                background-color: transparent;
                color: {self.color};
                font-size: 20px;
                font-family: 'Consolas';
                font-weight: bold;
                border-radius: 8px;
                padding: 10px 30px;
                border: 2px solid {self.color};
            }}
            QPushButton:hover {{
                background-color: {self.color};
                color: #05050A;
            }}
        """)
        
        panel_layout = QVBoxLayout(self.panel)
        panel_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        panel_layout.setSpacing(15)
        
        self.title_lbl = QLabel(f"SYSTEM ALERT: [ {conf['title'].upper()} ]")
        self.title_lbl.setObjectName("title")
        self.title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.msg_lbl = QLabel(conf['message'].upper())
        self.msg_lbl.setObjectName("msg")
        self.msg_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.timer_lbl = QLabel()
        self.timer_lbl.setObjectName("timer")
        self.timer_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont(FONT_NAME, 80, QFont.Weight.Bold)
        if FONT_NAME not in QFontDatabase.families(): font = QFont("Consolas", 80, QFont.Weight.Bold)
        self.timer_lbl.setFont(font)
        
        self.btn = QPushButton("I'VE DONE IT")
        self.btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn.clicked.connect(self.close_and_stop)
        
        panel_layout.addSpacing(20)
        panel_layout.addWidget(self.title_lbl)
        panel_layout.addWidget(self.timer_lbl)
        panel_layout.addSpacing(15)
        panel_layout.addWidget(self.msg_lbl)
        panel_layout.addWidget(self.btn, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter)
        panel_layout.addSpacing(20)
        
        layout.addWidget(self.panel)

        self.update_timer_label()
        
        self.break_timer = QTimer(self)
        self.break_timer.timeout.connect(self.tick)
        
        self.beep_timer = QTimer(self)
        self.beep_timer.timeout.connect(self.play_beep)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(5, 5, 10, 220))

    def show_alert(self):
        self.showFullScreen()
        self.raise_()
        self.activateWindow()
        self.anim.start()
        self.break_timer.start(1000)
        
    def close_and_stop(self):
        self.beep_timer.stop()
        self.break_timer.stop()
        try:
            # Force-kill any lingering async sounds from winsound
            winsound.PlaySound(None, winsound.SND_PURGE)
        except:
            pass
        self.hide()
        self.deleteLater()

    def update_timer_label(self):
        m = self.time_left // 60
        s = self.time_left % 60
        self.timer_lbl.setText(f"{m:02d}:{s:02d}")

    def tick(self):
        if self.time_left > 0:
            self.time_left -= 1
            self.update_timer_label()
            if self.time_left == 0:
                self.msg_lbl.setText("BREAK COMPLETE. RESUME OPERATIONS.")
                self.msg_lbl.setStyleSheet(f"color: {self.color}; font-weight: bold;")
                self.timer_lbl.setStyleSheet("color: white;")
                if APP_SETTINGS['play_sound']:
                    self.play_beep() # play immediately
                    self.beep_timer.start(2000) # then beep every 2 seconds until closed
        
    def play_beep(self):
        try:
            # Async so it doesn't freeze the GUI
            winsound.PlaySound("SystemHand", winsound.SND_ALIAS | winsound.SND_ASYNC)
        except:
            pass

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setFixedSize(380, 220)
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.bg = CyberPanel("#00f2fe", 255, 2, self)
        self.bg.setGeometry(0, 0, 380, 220)
        
        self.setStyleSheet("""
            QCheckBox { color: #00f2fe; font-family: 'Consolas'; font-size: 14px; margin: 10px; font-weight: bold; }
            QCheckBox::indicator { width: 20px; height: 20px; border: 1px solid #00f2fe; background: transparent; }
            QCheckBox::indicator:checked { background: #00f2fe; }
            QPushButton {
                background-color: transparent; color: #00f2fe;
                border-radius: 8px; padding: 10px 20px; font-weight: bold;
                font-family: 'Consolas'; border: 2px solid #00f2fe;
            }
            QPushButton:hover { background-color: rgba(0, 242, 254, 0.2); }
        """)
        
        layout = QVBoxLayout(self)
        
        self.cb_popups = QCheckBox("Enable Fullscreen Popups")
        self.cb_popups.setChecked(APP_SETTINGS['enable_popups'])
        
        self.cb_sound = QCheckBox("Play Alert Beeps")
        self.cb_sound.setChecked(APP_SETTINGS['play_sound'])
        
        self.cb_bg = QCheckBox("Run in Background (Minimize to Tray)")
        self.cb_bg.setChecked(APP_SETTINGS['run_in_background'])
        
        layout.addWidget(self.cb_popups)
        layout.addWidget(self.cb_sound)
        layout.addWidget(self.cb_bg)
        
        save_btn = QPushButton("SAVE SETTINGS")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self.save_and_close)
        layout.addWidget(save_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
    def save_and_close(self):
        APP_SETTINGS['enable_popups'] = self.cb_popups.isChecked()
        APP_SETTINGS['play_sound'] = self.cb_sound.isChecked()
        APP_SETTINGS['run_in_background'] = self.cb_bg.isChecked()
        self.accept()

class HealthGuardianDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Health Guardian - System UI")
        self.setFixedSize(900, 600)
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._drag_pos = None
        
        self.setStyleSheet("""
            QLabel { color: #00f2fe; font-family: 'Consolas'; }
            QPushButton {
                background-color: transparent;
                color: #00f2fe;
                border: 1px solid #00f2fe;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
                font-family: 'Consolas';
            }
            QPushButton:hover { background-color: rgba(0, 242, 254, 0.2); }
            QPushButton#testBtn { background-color: rgba(0, 242, 254, 0.1); border: 2px solid #00f2fe; font-size: 16px; }
            QPushButton#testBtn:hover { background-color: rgba(0, 242, 254, 0.3); }
            QPushButton#closeBtn { background-color: transparent; border: none; font-size: 20px; color: #a0a5b8; }
            QPushButton#closeBtn:hover { color: #f5576c; }
        """)

        central_widget = CyberPanel("#00f2fe", 255, 2)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        close_btn = QPushButton("X", central_widget)
        close_btn.setObjectName("closeBtn")
        close_btn.setGeometry(850, 20, 30, 30)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.close)
        
        header = QLabel("SYSTEM UI: HEALTH GUARDIAN")
        header.setStyleSheet("font-size: 30px; font-weight: bold; letter-spacing: 2px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub = QLabel("HUMAN HEALTH PROTECTION // ALWAYS ACTIVE")
        sub.setStyleSheet("font-size: 14px; color: #a0a5b8;")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        main_layout.addWidget(header)
        main_layout.addWidget(sub)
        main_layout.addSpacing(30)
        
        grid = QHBoxLayout()
        self.circles = {}
        for timer_id in ['20', '60', '120']:
            card = QWidget()
            card_layout = QVBoxLayout(card)
            card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            t_lbl = QLabel(f"[{TIMERS_CONF[timer_id]['title'].upper()}]")
            t_lbl.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {TIMERS_CONF[timer_id]['color']};")
            t_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            circle = CircularProgress(timer_id, card)
            circle.timer_finished.connect(self.trigger_alert)
            self.circles[timer_id] = circle
            
            btn = QPushButton("PAUSE")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda ch, c=circle, b=btn: self.toggle_timer(c, b))
            
            card_layout.addWidget(t_lbl)
            card_layout.addWidget(circle, 0, Qt.AlignmentFlag.AlignCenter)
            card_layout.addWidget(btn)
            
            grid.addWidget(card)
            
        main_layout.addLayout(grid)
        main_layout.addSpacing(20)
        
        ctrl_layout = QHBoxLayout()
        ctrl_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        test_btn = QPushButton("TEST OVERLAY FORCE POPUP")
        test_btn.setObjectName("testBtn")
        test_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        test_btn.clicked.connect(self.test_popup)
        
        reset_btn = QPushButton("RESET TIMERS")
        reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reset_btn.clicked.connect(self.reset_all)
        
        settings_btn = QPushButton("⚙ SYSTEM SETTINGS")
        settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        settings_btn.clicked.connect(self.open_settings)
        
        ctrl_layout.addWidget(test_btn)
        ctrl_layout.addWidget(reset_btn)
        ctrl_layout.addWidget(settings_btn)
        main_layout.addLayout(ctrl_layout)

        self.setup_tray()
        
        self.master_timer = QTimer(self)
        self.master_timer.timeout.connect(self.tick_all)
        self.master_timer.start(1000)
        
        self.active_overlays = []

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def toggle_timer(self, circle, btn):
        circle.play_pause()
        btn.setText("PAUSE" if circle.is_running else "RESUME")

    def reset_all(self):
        for c in self.circles.values():
            c.reset()

    def tick_all(self):
        for c in self.circles.values():
            c.update_timer()

    def trigger_alert(self, timer_id):
        if not APP_SETTINGS['enable_popups']:
            return
            
        conf = TIMERS_CONF[timer_id]
        overlay = AlertOverlay(conf)
        self.active_overlays.append(overlay)
        overlay.show_alert()

    def test_popup(self):
        self.trigger_alert('20')

    def open_settings(self):
        dlg = SettingsDialog(self)
        dlg.exec()

    def setup_tray(self):
        icon = QApplication.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        self.tray_icon = QSystemTrayIcon(icon, self)
        
        menu = QMenu()
        show_action = QAction("SHOW UI", self)
        show_action.triggered.connect(self.showNormal)
        
        quit_action = QAction("DEACTIVATE GUARDIAN", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        
        menu.addAction(show_action)
        menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()
        
    def closeEvent(self, event):
        if APP_SETTINGS['run_in_background']:
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "Health Guardian",
                "UI Minimized. System remains active in background.",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
        else:
            event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Crucial to prevent app quitting or firing main window closeEvents when the popup closes
    app.setQuitOnLastWindowClosed(False)
    
    # Load Font
    if os.path.exists(FONT_PATH):
        font_id = QFontDatabase.addApplicationFont(FONT_PATH)
        if font_id != -1:
            FONT_NAME = QFontDatabase.applicationFontFamilies(font_id)[0]
            
    app.setWindowIcon(app.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
    window = HealthGuardianDashboard()
    window.show()
    sys.exit(app.exec())
