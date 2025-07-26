import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy, 
    QMessageBox, QPushButton, QLineEdit, QFrame
)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, pyqtProperty
from PyQt5.QtGui import QColor, QPainter, QFont, QIcon  # Добавил QIcon


class AnimatedButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self._color = QColor("#222222")
        self._hover_color = QColor("#00cc44")
        self._current_color = self._color

        self.anim = QPropertyAnimation(self, b"color")
        self.anim.setDuration(300)

        self.setFont(QFont("Segoe UI Black", 14, QFont.Bold))
        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(50)

    def getColor(self):
        return self._current_color

    def setColor(self, color):
        self._current_color = color
        self.update()

    color = pyqtProperty(QColor, fget=getColor, fset=setColor)

    def enterEvent(self, event):
        self.anim.stop()
        self.anim.setStartValue(self._current_color)
        self.anim.setEndValue(self._hover_color)
        self.anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.anim.stop()
        self.anim.setStartValue(self._current_color)
        self.anim.setEndValue(self._color)
        self.anim.start()
        super().leaveEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(self._current_color)
        painter.setPen(Qt.NoPen)
        rect = self.rect()
        radius = 35
        painter.drawRoundedRect(rect, radius, radius)
        painter.setPen(Qt.white)
        painter.setFont(self.font())
        painter.drawText(rect, Qt.AlignCenter, self.text())


class ShutdownApp(QWidget):
    def __init__(self):
        super().__init__()
        
        # Инициализация иконки (работает и в EXE, и в Python)
        self.init_icon()
        
        # Основные настройки окна
        self.setWindowTitle("Shutdown Timer")
        self.setFixedSize(350, 500)
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
            }
            QMessageBox {
                background-color: #252525;
                color: white;
            }
        """)
        
        # Инициализация таймера
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_countdown)
        self.remaining_seconds = 0
        self.shutdown_scheduled = False
        
        # Шрифты
        self.main_font = QFont("Segoe UI", 12, QFont.Bold)
        self.title_font = QFont("Segoe UI Black", 14, QFont.Bold)
        
        # Основные элементы интерфейса
        self.init_ui()
        
        # Для правильного отображения иконки в Windows
        if sys.platform == "win32":
            self.set_win32_app_id()

    def init_icon(self):
        """Инициализация иконки приложения"""
        if getattr(sys, 'frozen', False):
            # Для собранного EXE
            base_path = sys._MEIPASS
        else:
            # Для запуска из Python
            base_path = os.path.dirname(os.path.abspath(__file__))
            
        icon_path = os.path.join(base_path, "icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            self.setWindowIcon(QIcon.fromTheme("system-shutdown"))

    def set_win32_app_id(self):
        """Установка AppID для Windows (для правильного отображения иконки)"""
        try:
            from ctypes import windll
            windll.shell32.SetCurrentProcessExplicitAppUserModelID("ShutdownTimer.1.0")
        except Exception as e:
            print(f"Не удалось установить AppID: {e}")

    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок
        self.label = QLabel("Выберите время до выключения")
        self.label.setFont(self.title_font)
        self.label.setStyleSheet("color: #E0E0E0;")
        self.label.setAlignment(Qt.AlignCenter)
        
        # Таймер
        self.countdown_label = QLabel()
        self.countdown_label.setFont(QFont("Segoe UI", 28, QFont.Bold))
        self.countdown_label.setStyleSheet("color: #00CC44;")
        self.countdown_label.setAlignment(Qt.AlignCenter)
        
        # Кнопки выбора времени
        time_buttons = self.create_time_buttons()
        
        # Поле ввода времени
        input_panel = self.create_input_panel()
        
        # Кнопка отмены
        cancel_btn = self.create_cancel_button()
        
        # Сборка интерфейса
        main_layout.addWidget(self.label)
        main_layout.addWidget(self.countdown_label)
        main_layout.addLayout(time_buttons)
        main_layout.addWidget(input_panel)
        main_layout.addWidget(cancel_btn)
        
        self.setLayout(main_layout)

    def create_time_buttons(self):
        """Создает кнопки для быстрого выбора времени"""
        buttons_layout = QHBoxLayout()
        left_column = QVBoxLayout()
        right_column = QVBoxLayout()
        
        times = [5, 15, 45, 10, 30, 60]
        
        for i, minutes in enumerate(times):
            btn = AnimatedButton(f"{minutes} мин")
            btn.clicked.connect(lambda checked, sec=minutes*60: self.start_timer(sec))
            if i < 3:
                left_column.addWidget(btn)
            else:
                right_column.addWidget(btn)
        
        buttons_layout.addLayout(left_column)
        buttons_layout.addLayout(right_column)
        return buttons_layout

    def create_input_panel(self):
        """Создает панель с полем ввода"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 25px;
                padding: 5px;
            }
        """)
        
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(10, 5, 5, 5)
        layout.setSpacing(10)
        
        self.custom_input = QLineEdit()
        self.custom_input.setPlaceholderText("Минуты")
        self.custom_input.setFont(self.main_font)
        self.custom_input.setStyleSheet("""
            QLineEdit {
                background-color: transparent;
                border: none;
                color: #000000;
                padding: 5px;
            }
        """)
        
        ok_btn = QPushButton("OK")
        ok_btn.setFixedSize(70, 35)
        ok_btn.setFont(self.main_font)
        ok_btn.setCursor(Qt.PointingHandCursor)
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #222222;
                color: white;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #00CC44;
            }
        """)
        ok_btn.clicked.connect(self.custom_time_entered)
        
        layout.addWidget(self.custom_input)
        layout.addWidget(ok_btn)
        
        return frame

    def create_cancel_button(self):
        """Создает кнопку отмены"""
        btn = QPushButton("❌ Отменить выключение")
        btn.setFont(self.main_font)
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn.setFixedHeight(50)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #D32F2F;
                color: white;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #B71C1C;
            }
        """)
        btn.clicked.connect(self.cancel_shutdown)
        return btn

    def start_timer(self, seconds):
        """Запускает таймер выключения"""
        self.remaining_seconds = seconds
        self.shutdown_scheduled = True
        self.timer.start(1000)
        self.update_countdown()
        os.system(f"shutdown /s /t {seconds}")

    def custom_time_entered(self):
        """Обработка ввода пользовательского времени"""
        try:
            minutes = int(self.custom_input.text())
            if minutes <= 0:
                raise ValueError
            self.start_timer(minutes * 60)
            self.custom_input.clear()
        except ValueError:
            QMessageBox.warning(
                self, 
                "Ошибка", 
                "Введите положительное целое число минут.",
                QMessageBox.Ok
            )

    def update_countdown(self):
        """Обновление отображения таймера"""
        if self.remaining_seconds > 0:
            if self.remaining_seconds == 60:
                QMessageBox.information(
                    self, 
                    "Внимание", 
                    "Осталась 1 минута до выключения!",
                    QMessageBox.Ok
                )
            mins, secs = divmod(self.remaining_seconds, 60)
            self.countdown_label.setText(f"{mins:02d}:{secs:02d}")
            self.remaining_seconds -= 1
        else:
            self.timer.stop()
            self.countdown_label.setText("💤 Выключение...")

    def cancel_shutdown(self):
        """Отмена запланированного выключения"""
        if self.shutdown_scheduled:
            os.system("shutdown /a")
            self.shutdown_scheduled = False
            self.timer.stop()
            self.countdown_label.setText("🕒 Отменено")
            QMessageBox.information(
                self, 
                "Отмена", 
                "Выключение отменено!",
                QMessageBox.Ok
            )