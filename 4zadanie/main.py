# main.py
import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from PyQt5.uic import loadUi


class TransparencyEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        ui_file = Path(__file__).parent / "transparency.ui"
        if not ui_file.exists():
            raise FileNotFoundError(f"Не найден файл: {ui_file}")
        loadUi(str(ui_file), self)

        self.original_pixmap = None
        self.current_opacity = 1.0  # от 0.0 до 1.0

        self.transparency_slider.setMinimum(0)
        self.transparency_slider.setMaximum(100)
        self.transparency_slider.setValue(100)
        self.percent_label.setText("100%")
        self.transparency_slider.setEnabled(False)  

        self.btn_load.clicked.connect(self.load_image)
        self.transparency_slider.valueChanged.connect(self.update_transparency)
        
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setText("Изображение не загружено")

    def load_image(self):
        """Открывает диалог выбора изображения"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Открыть изображение",
            "",
            "Изображения (*.png *.jpg *.jpeg *.bmp);;Все файлы (*)"
        )

        if not file_path:
            return

        pixmap = QPixmap(file_path)
        if pixmap.isNull():
            QMessageBox.critical(self, "Ошибка", "Не удалось загрузить изображение.")
            return

        # Сохраняю оригинал
        self.original_pixmap = pixmap.copy()
        self.current_opacity = 1.0

        self.transparency_slider.setEnabled(True)
        self.transparency_slider.setValue(100)
        self.percent_label.setText("100%")

        self.apply_transparency()
        self.status_label.setText(f"Изображение загружено: {Path(file_path).name}")

    def update_transparency(self, value):
        """Вызывается при изменении слайдера"""
        self.current_opacity = value / 100.0
        self.percent_label.setText(f"{value}%")
        self.apply_transparency()
        self.status_label.setText(f"Прозрачность: {value}%")

    def apply_transparency(self):
        """Накладывает alpha-канал и обновляет изображение"""
        if self.original_pixmap is None:
            return

        # Конвертируем для манипуляций
        image = self.original_pixmap.toImage()
        width = image.width()
        height = image.height()

        result_image = QImage(width, height, QImage.Format_ARGB32)

        for y in range(height):
            for x in range(width):
                pixel = image.pixelColor(x, y)
                alpha = int(255 * self.current_opacity)
                pixel.setAlpha(alpha)
                result_image.setPixelColor(x, y, pixel)

        result_pixmap = QPixmap.fromImage(result_image)

        scaled_pixmap = result_pixmap.scaled(
            self.image_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)

    def resizeEvent(self, event):
        """Перерисовывает при изменении размера окна"""
        super().resizeEvent(event)
        if self.original_pixmap is not None:
            self.apply_transparency()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TransparencyEditor()
    window.setWindowTitle("Регулятор прозрачности изображения")
    window.show()
    sys.exit(app.exec())