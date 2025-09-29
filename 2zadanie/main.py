# main.py
import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PyQt5.uic import loadUi


class TextEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        ui_file = Path(__file__).parent / "editor.ui"
        if not ui_file.exists():
            raise FileNotFoundError(f"Не найден файл: {ui_file}")
        loadUi(str(ui_file), self)

        self.current_file = None
        self.is_modified = False  

        self.action_new.clicked.connect(self.new_file)    
        self.action_open.clicked.connect(self.open_file)
        self.action_save.clicked.connect(self.save_file)

        self.text_edit.textChanged.connect(self.on_text_changed)

        self.setup_window_title()

    def setup_window_title(self):
        """Обновляет заголовок окна"""
        title = "Текстовый редактор"
        if self.current_file:
            title += f" - {Path(self.current_file).name}"
        if self.is_modified:
            title += " *"
        self.setWindowTitle(title)

    def on_text_changed(self):
        """Помечает документ как изменённый"""
        if not self.is_modified:
            self.is_modified = True
            self.setup_window_title()

    def confirm_save(self):
        """Спрашивает, сохранить ли изменения"""
        if not self.is_modified:
            return True

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Подтверждение")
        msg_box.setText("Документ был изменён.")
        msg_box.setInformativeText("Сохранить изменения?")
        msg_box.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
        result = msg_box.exec_()
        if result == QMessageBox.Save:
            return self.save_file()
        elif result == QMessageBox.Discard:
            return True
        else:
            return False

    def new_file(self):
        """Создать новый файл"""
        if not self.confirm_save():
            return
        self.text_edit.clear()
        self.current_file = None
        self.is_modified = False
        self.setup_window_title()
        self.statusBar().showMessage("Создан новый файл", 2000)

    def open_file(self):
        """Открыть файл"""
        if not self.confirm_save():
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Открыть файл",
            "",
            "Текстовые файлы (*.txt);;Все файлы (*)"
        )

        if not file_path:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.text_edit.setText(content)
            self.current_file = file_path
            self.is_modified = False
            self.setup_window_title()
            self.status_bar.showMessage(f"Файл открыт: {Path(file_path).name}", 2000)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть файл:\n{str(e)}")

    def save_file(self):
        """Сохранить файл"""
        if self.current_file:
            return self.save_to_file(self.current_file)
        else:
            return self.save_as()

    def save_as(self):
        """Сохранить как..."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить файл как",
            "",
            "Текстовые файлы (*.txt);;Все файлы (*)"
        )
        if not file_path:
            return False
        return self.save_to_file(file_path)

    def save_to_file(self, file_path):
        """Сохраняет содержимое в файл"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.text_edit.toPlainText())
            self.current_file = file_path
            self.is_modified = False
            self.setup_window_title()
            self.statusBar().showMessage(f"Файл сохранён: {Path(file_path).name}", 2000)
            return True
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл:\n{str(e)}")
            return False

    def closeEvent(self, event):
        """Обработка закрытия окна"""
        if self.confirm_save():
            event.accept()
        else:
            event.ignore()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TextEditor()
    window.show()
    sys.exit(app.exec())