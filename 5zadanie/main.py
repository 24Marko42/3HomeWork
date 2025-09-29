# main.py
import sys
import random
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel,
    QPushButton, QInputDialog, QMessageBox
)
from PyQt5.QtGui import QPixmap, QPainter, QColor
from PyQt5.QtCore import Qt
from PyQt5.uic import loadUi


class FlagGenerator(QMainWindow):
    def __init__(self):
        super().__init__()

        # Загружаем UI
        ui_file = Path(__file__).parent / "generator_flaga.ui"
        if not ui_file.exists():
            raise FileNotFoundError(f"Не найден файл: {ui_file}")
        loadUi(str(ui_file), self)

        # Привязка кнопки
        self.btn_generate.clicked.connect(self.generate_flag)

        # Инициализация
        self.flag_pixmap = None
        self.status_label.setText("Нажмите 'Сгенерировать'")

    def generate_flag(self):
        """Запрашивает количество полос и рисует флаг"""
        num_stripes, ok = QInputDialog.getInt(
            self,
            "Количество полос",
            "Введите количество цветных полос:",
            min=2,
            max=20,
            value=5
        )

        if not ok:
            return  # пользователь нажал Cancel

        # Получаем размер холста
        width = self.flag_label.width()
        height = self.flag_label.height()

        if width < 10 or height < 10:
            width = 400
            height = 300

        # Создаём пустое изображение
        self.flag_pixmap = QPixmap(width, height)
        self.flag_pixmap.fill(Qt.white)
        painter = QPainter(self.flag_pixmap)

        # Высота одной полосы
        stripe_height = height / num_stripes

        # Рисуем полосы
        for i in range(num_stripes):
            color = QColor(
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255)
            )
            y = int(i * stripe_height)
            h = int(stripe_height)
            painter.fillRect(0, y, width, h, color)

        painter.end()

        # Обновляем отображение
        self.update_display()
        self.status_label.setText(f"Флаг с {num_stripes} полосами сгенерирован.")

    def update_display(self):
        """Масштабирует и устанавливает pixmap"""
        if self.flag_pixmap is None:
            self.flag_label.setText("Флаг не сгенерирован")
            return

        scaled = self.flag_pixmap.scaled(
            self.flag_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.flag_label.setPixmap(scaled)

    def resizeEvent(self, event):
        """Перерисовывает при изменении размера окна"""
        super().resizeEvent(event)
        if self.flag_pixmap is not None:
            self.update_display()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FlagGenerator()
    window.setWindowTitle("Генератор полосатого флага")
    window.show()
    sys.exit(app.exec_())