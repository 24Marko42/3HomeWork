# main.py
import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QMessageBox
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl
from PyQt5.uic import loadUi


class PianoApp(QMainWindow):
    def __init__(self):
        super().__init__()

        ui_file = Path(__file__).parent / "piano.ui"
        if not ui_file.exists():
            raise FileNotFoundError(f"Не найден файл интерфейса: {ui_file.resolve()}")
        loadUi(str(ui_file), self)

        self.sound_dir = Path(__file__).parent / "sounds"

        if not self.sound_dir.exists():
            QMessageBox.warning(self, "Предупреждение", f"Папка 'sounds' не найдена. Фортепиано будет работать без звука.")

        self.notes = {
            'A3#': 'A3#.mp3',
            'A5': 'A5.mp3',
            'B3': 'B3.mp3',
            'B3#': 'B3#.mp3',
            'C4': 'C4.mp3',
            'C4#': 'C4#.mp3',
            'D4': 'D4.mp3',
            'D6': 'D6.mp3',
            'E3': 'E3.mp3',
            'F6': 'F6.mp3',
            'G4': 'G4.mp3',
            'G5': 'G5.mp3'
        }

        # Белые клавиши (objectName из Qt Designer)
        self.white_keys = {
            'C': self.btn_C,
            'D': self.btn_D,
            'E': self.btn_E,
            'F': self.btn_F,
            'G': self.btn_G,
            'A': self.btn_A,
            'B': self.btn_B
        }

        # Чёрные клавиши (создаются программно)
        self.black_keys = {}
        self.create_black_keys()

        # Медиаплеер
        self.player = QMediaPlayer()

        self.setup_key_connections()

        self.status_label.setText("Фортепиано готово")

    def create_black_keys(self):
        """Создаёт чёрные клавиши поверх белых"""
        positions = [
            ('C#', self.btn_C, 0.7),
            ('D#', self.btn_D, 0.7),
            ('F#', self.btn_F, 0.7),
            ('G#', self.btn_G, 0.7),
            ('A#', self.btn_A, 0.7),
        ]

        for note, parent_btn, offset in positions:
            btn = QPushButton(note, self)
            btn.setStyleSheet("background-color: black; color: white;")
            btn.setFixedSize(40, 120)
            btn.setParent(self)  
            self.black_keys[note] = btn

    def resizeEvent(self, event):
        """Переопределено: при изменении размера окна перерисовываем позиции чёрных клавиш"""
        super().resizeEvent(event)
        self.reposition_black_keys()

    def reposition_black_keys(self):
        """Располагает чёрные клавиши над белыми"""
        x_pos = 0
        for key_name, button in self.white_keys.items():
            width = button.width()
            height = button.height()
            geom = button.geometry()

            if key_name == 'C' and 'C#' in self.black_keys:
                btn = self.black_keys['C#']
                btn.move(geom.x() + int(width * 0.7), 50)

            elif key_name == 'D' and 'D#' in self.black_keys:
                btn = self.black_keys['D#']
                btn.move(geom.x() + int(width * 0.7), 50)

            elif key_name == 'F' and 'F#' in self.black_keys:
                btn = self.black_keys['F#']
                btn.move(geom.x() + int(width * 0.7), 50)

            elif key_name == 'G' and 'G#' in self.black_keys:
                btn = self.black_keys['G#']
                btn.move(geom.x() + int(width * 0.7), 50)

            elif key_name == 'A' and 'A#' in self.black_keys:
                btn = self.black_keys['A#']
                btn.move(geom.x() + int(width * 0.7), 50)

            x_pos += width

    def setup_key_connections(self):
        """Назначает обработчики нажатий для всех клавиш"""
        # Белые клавиши
        for note, button in self.white_keys.items():
            button.clicked.connect(lambda _, n=note: self.play_note(n))

        # Чёрные клавиши
        for note, button in self.black_keys.items():
            button.clicked.connect(lambda _, n=note: self.play_note(n))

    def play_note(self, note):
        """Проигрывает звук ноты"""
        filename = self.notes.get(note)
        if not filename:
            return

        file_path = self.sound_dir / filename
        if file_path.exists():
            url = QUrl.fromLocalFile(str(file_path))
            self.player.setMedia(QMediaContent(url))
            self.player.play()
            self.status_label.setText(f"Играет: {note}")
        else:
            self.status_label.setText(f"Звук не найден: {filename}")
            print(f"Файл не найден: {file_path}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PianoApp()
    window.setWindowTitle("Виртуальное фортепиано")
    window.show()
    sys.exit(app.exec())