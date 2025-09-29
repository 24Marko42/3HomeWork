# main.py
import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PyQt5.uic import loadUi


class NumberAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()

        ui_file = Path(__file__).parent / "numbers_analysis.ui"
        if not ui_file.exists():
            raise FileNotFoundError(f"Не найден файл: {ui_file}")
        loadUi(str(ui_file), self)

        self.current_directory = str(Path.cwd())

        self.loadButton.clicked.connect(self.load_file)   
        self.saveButton_2.clicked.connect(self.save_results)  

        self.numbers = []
        self.clear_results()

    def clear_results(self):
        self.maxLabel.setText("-")
        self.minLabel.setText("-")
        self.avgLabel.setText("-")
        self.numbers_text.setPlainText("Числа не загружены.")

    def show_status(self, message):
        self.statusBar().showMessage(message)

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Открыть текстовый файл",
            self.current_directory,
            "Text Files (*.txt);;All Files (*)"
        )
        if not file_path:
            return

        self.current_directory = str(Path(file_path).parent)

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tokens = content.split()
            numbers = []
            for token in tokens:
                try:
                    num = int(token)
                    numbers.append(num)
                except ValueError:
                    raise ValueError(f"Неверный формат: '{token}'")

            if not numbers:
                raise ValueError("Файл пуст.")

            self.numbers = numbers
            self.max_value = max(numbers)
            self.min_value = min(numbers)
            self.avg_value = sum(numbers) / len(numbers)

            # Выводим числа
            self.numbers_text.setPlainText(' '.join(map(str, numbers)))
            self.maxLabel.setText(str(self.max_value))
            self.minLabel.setText(str(self.min_value))
            self.avgLabel.setText(f"{self.avg_value:.2f}")
            self.show_status(f"Загружено {len(numbers)} чисел")

        except Exception as e:
            self.clear_results()
            self.numbers_text.setPlainText("")
            self.show_status("Ошибка")
            QMessageBox.critical(self, "Ошибка", f"Не удалось прочитать файл:\n{str(e)}")

    def save_results(self):
        if not self.numbers:
            QMessageBox.warning(self, "Предупреждение", "Сначала загрузите данные.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить результаты",
            self.current_directory,
            "Text Files (*.txt);;All Files (*)"
        )
        if not file_path:
            return

        self.current_directory = str(Path(file_path).parent)

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"Максимальное значение: {self.max_value}\n")
                f.write(f"Минимальное значение: {self.min_value}\n")
                f.write(f"Среднее значение: {self.avg_value:.2f}\n")
                f.write(f"Всего чисел: {len(self.numbers)}\n")

            self.show_status("Результаты сохранены")
            QMessageBox.information(self, "Сохранение", "Результаты успешно сохранены.")

        except Exception as e:
            self.show_status("Ошибка сохранения")
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл:\n{str(e)}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = NumberAnalyzer()
    window.show()
    sys.exit(app.exec())