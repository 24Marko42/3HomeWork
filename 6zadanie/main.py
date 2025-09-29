# main.py
import sys
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton,
    QSlider, QLabel, QColorDialog, QMessageBox
)
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QPixmap
from PyQt5.QtCore import Qt
from PyQt5.uic import loadUi


class SmileyApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Загружаем UI
        ui_file = Path(__file__).parent / "smilik.ui"
        if not ui_file.exists():
            raise FileNotFoundError(f"Не найден файл: {ui_file}")
        loadUi(str(ui_file), self)

        # Настройки
        self.smiley_color = QColor(255, 220, 0)  # Жёлтый по умолчанию
        self.scale_factor = 1.0  # 100%

        # Настройка слайдера
        self.scale_slider.setMinimum(10)
        self.scale_slider.setMaximum(200)
        self.scale_slider.setValue(100)
        self.scale_slider.valueChanged.connect(self.update_scale)

        # Текст масштаба
        self.scale_label.setText("100%")

        # Привязка кнопки
        self.btn_color.clicked.connect(self.choose_color)

        # Инициализация холста
        self.canvas.setAlignment(Qt.AlignCenter)
        self.canvas.setMinimumSize(300, 300)

        # Первичная отрисовка
        self.draw_smiley()

    def choose_color(self):
        """Открывает диалог выбора цвета"""
        color = QColorDialog.getColor(self.smiley_color, self, "Выберите цвет смайлика")
        if color.isValid():
            self.smiley_color = color
            self.draw_smiley()
            self.statusBar().showMessage("Цвет изменён")

    def update_scale(self, value):
        """Обновляет масштаб"""
        self.scale_factor = value / 100.0
        self.scale_label.setText(f"{value}%")
        self.draw_smiley()
        self.statusBar().showMessage(f"Масштаб: {value}%")

    def draw_smiley(self):
        """Рисует смайлик с текущим цветом и масштабом"""
        size = self.canvas.size()
        w, h = size.width(), size.height()

        if w < 10 or h < 10:
            w = h = 500

        pixmap = QPixmap(w, h)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Центр и базовый радиус
        center_x = w // 2
        center_y = h // 2
        base_radius = min(w, h) * 0.4 * self.scale_factor

        # Лицо
        painter.setPen(QPen(Qt.black, 2))
        painter.setBrush(QBrush(self.smiley_color))
        painter.drawEllipse(
            int(center_x - base_radius),
            int(center_y - base_radius),
            int(2 * base_radius),
            int(2 * base_radius)
        )

        # Глаза
        eye_r = base_radius * 0.15
        # Левый глаз
        painter.setBrush(QBrush(Qt.black))
        painter.drawEllipse(
            int(center_x - base_radius * 0.4 - eye_r),
            int(center_y - base_radius * 0.4 - eye_r),
            int(2 * eye_r),
            int(2 * eye_r)
        )
        # Правый глаз
        painter.drawEllipse(
            int(center_x + base_radius * 0.4 - eye_r),
            int(center_y - base_radius * 0.4 - eye_r),
            int(2 * eye_r),
            int(2 * eye_r)
        )

        # Улыбка
        smile_r = base_radius * 0.7
        rect = (
            int(center_x - smile_r),
            int(center_y - smile_r * 0.5),
            int(2 * smile_r),
            int(2 * smile_r)
        )
        painter.setPen(QPen(Qt.black, 3))
        painter.setBrush(Qt.NoBrush)
        painter.drawArc(*rect, 0 * 16, 180 * 16)  # нижняя дуга

        painter.end()

        # Масштабируем под размер label
        scaled = pixmap.scaled(
            self.canvas.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.canvas.setPixmap(scaled)

    def resizeEvent(self, event):
        """Перерисовка при изменении размера окна"""
        super().resizeEvent(event)
        self.draw_smiley()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SmileyApp()
    window.setWindowTitle("Смайлик")
    window.show()
    sys.exit(app.exec_())