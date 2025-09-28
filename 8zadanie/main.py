# main.py
import sys
import math
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QMessageBox,
    QVBoxLayout, QLabel, QSlider, QHBoxLayout, QWidget
)
from PyQt5.QtGui import QPainter, QPen, QColor, QPixmap
from PyQt5.QtCore import Qt
from PyQt5.uic import loadUi


class LSystemApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Загружаем UI
        ui_file = Path(__file__).parent / "l_system.ui"
        if not ui_file.exists():
            raise FileNotFoundError(f"Не найден файл: {ui_file}")
        loadUi(str(ui_file), self)

        # Данные L-системы
        self.axiom = ""
        self.rules = {}
        self.angle_divisions = 5
        self.system_name = ""
        self.current_sequence = ""
        self.max_steps = 5

        # Текущий шаг
        self.step = 0

        # Настройка слайдера
        self.evolution_slider.setMinimum(0)
        self.evolution_slider.setMaximum(self.max_steps)
        self.evolution_slider.setValue(0)
        self.evolution_slider.setEnabled(False)
        self.evolution_slider.valueChanged.connect(self.update_step)

        # Метки
        self.step_label.setText("0")
        self.system_name_label.setText("L-система не загружена")

        # Загрузка при старте
        self.load_lsystem_file()

    def load_lsystem_file(self):
        """Открывает диалог выбора файла L-системы"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Открыть файл L-системы",
            "",
            "Текстовые файлы (*.txt);;Все файлы (*)"
        )

        if not file_path:
            QMessageBox.critical(self, "Ошибка", "Файл не выбран.")
            self.close()
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]

            if len(lines) < 3:
                raise ValueError("Файл должен содержать минимум 3 строки.")

            self.system_name = lines[0]
            self.angle_divisions = int(lines[1])
            self.axiom = lines[2]

            # Парсим правила
            self.rules = {}
            for line in lines[3:]:
                parts = line.split(maxsplit=1)
                if len(parts) == 2:
                    key, value = parts
                    self.rules[key] = value.replace(' ', '')  # убираем пробелы

            # Инициализация
            self.system_name_label.setText(f"<b>{self.system_name}</b>")
            self.evolution_slider.setEnabled(True)
            self.update_step(0)
            self.statusBar().showMessage(f"Загружено: {Path(file_path).name}")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить L-систему:\n{str(e)}")
            self.close()

    def update_step(self, step):
        """Обновляет последовательность и перерисовывает"""
        self.step = step
        sequence = self.axiom
        for _ in range(step):
            next_seq = ""
            for char in sequence:
                next_seq += self.rules.get(char, char)
            sequence = next_seq
        self.current_sequence = sequence
        self.step_label.setText(str(step))
        self.draw_fractal()

    def draw_fractal(self):
        """Рисует фрактал с помощью QPainter"""
        size = self.canvas.size()
        w, h = size.width(), size.height()

        if w < 10 or h < 10:
            w = h = 600

        pixmap = QPixmap(w, h)
        pixmap.fill(Qt.white)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(w // 2, h // 2)

        length = 5 if self.step < 4 else 2
        angle_deg = 360 / self.angle_divisions
        direction = 0  # угол в градусах
        stack = []
        x, y = 0, 0

        for cmd in self.current_sequence:
            if cmd in 'FAB':  # линия вперёд
                dx = length * math.cos(math.radians(direction))
                dy = length * math.sin(math.radians(direction))
                painter.setPen(QPen(Qt.black, 1))
                # ✅ Приводим к int
                painter.drawLine(int(x), int(y), int(x + dx), int(y + dy))
                x += dx
                y += dy
            elif cmd == 'f':  # движение без рисования
                dx = length * math.cos(math.radians(direction))
                dy = length * math.sin(math.radians(direction))
                x += dx
                y += dy
            elif cmd == '+':
                direction += angle_deg
            elif cmd == '-':
                direction -= angle_deg
            elif cmd == '[':
                stack.append((x, y, direction))
            elif cmd == ']':
                if stack:
                    x, y, direction = stack.pop()

        painter.end()

        scaled_pixmap = pixmap.scaled(
            self.canvas.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.canvas.setPixmap(scaled_pixmap)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.evolution_slider.isEnabled():
            self.draw_fractal()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LSystemApp()
    window.show()
    sys.exit(app.exec_())