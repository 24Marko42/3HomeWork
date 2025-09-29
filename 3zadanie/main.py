# main.py
import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PyQt5.QtGui import QPixmap, QImage, qRgb
from PyQt5.QtCore import Qt
from PyQt5.uic import loadUi


class ImageEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        ui_file = Path(__file__).parent / "image_edit.ui"
        if not ui_file.exists():
            raise FileNotFoundError(f"Не найден файл: {ui_file}")
        loadUi(str(ui_file), self)

        self.original_image = None  
        self.rotation_count = 0    

        self.radio_original.setChecked(True)

        self.radio_red.toggled.connect(self.update_display)
        self.radio_green.toggled.connect(self.update_display)
        self.radio_blue.toggled.connect(self.update_display)
        self.radio_original.toggled.connect(self.update_display)
        self.btn_rotate_left.clicked.connect(self.rotate_left)
        self.btn_rotate_right.clicked.connect(self.rotate_right)
        self.btn_save.clicked.connect(self.save_image)  

        self.load_image_on_start()

    def load_image_on_start(self):
        """Открывает диалог выбора изображения при запуске"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите квадратное изображение",
            "",
            "Изображения (*.png *.jpg *.jpeg *.bmp);;Все файлы (*)"
        )

        if not file_path:
            QMessageBox.critical(self, "Ошибка", "Изображение не выбрано.")
            self.close()
            return

        pixmap = QPixmap(file_path)
        if pixmap.isNull():
            QMessageBox.critical(self, "Ошибка", "Не удалось загрузить изображение.")
            self.close()
            return

        width, height = pixmap.width(), pixmap.height()
        if abs(width - height) > 10:
            QMessageBox.warning(self, "Предупреждение", "Изображение должно быть квадратным! Будет обрезано.")
            size = min(width, height)
            rect = (width - size) // 2, (height - size) // 2, size, size
            image = pixmap.toImage().copy(*rect)
            pixmap = QPixmap.fromImage(image)

        self.original_image = pixmap.toImage()
        self.rotation_count = 0
        self.update_display()
        self.status_label.setText("Изображение загружено")

    def update_display(self):
        """Применяет текущие эффекты и отображает изображение"""
        if self.original_image is None:
            return

        image = self.original_image.copy()

        if self.radio_red.isChecked():
            image = self.keep_channel(image, 'red')
        elif self.radio_green.isChecked():
            image = self.keep_channel(image, 'green')
        elif self.radio_blue.isChecked():
            image = self.keep_channel(image, 'blue')

        # Конвертирую в QPixmap
        pixmap = QPixmap.fromImage(image)

        if self.rotation_count != 0:
            from PyQt5.QtGui import QTransform
            transform = QTransform().rotate(90 * self.rotation_count)
            pixmap = pixmap.transformed(transform, Qt.SmoothTransformation)

        self.current_pixmap = pixmap  

        # Масштабируем 
        scaled = pixmap.scaled(
            self.image_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.image_label.setPixmap(scaled)

    def keep_channel(self, img: QImage, channel: str) -> QImage:
        """Оставляет только один цветовой канал"""
        result = img.copy()
        for x in range(img.width()):
            for y in range(img.height()):
                pixel = img.pixelColor(x, y)
                r, g, b, a = pixel.red(), pixel.green(), pixel.blue(), pixel.alpha()
                if channel == 'red':
                    new_color = qRgb(r, 0, 0)
                elif channel == 'green':
                    new_color = qRgb(0, g, 0)
                elif channel == 'blue':
                    new_color = qRgb(0, 0, b)
                else:
                    new_color = pixel.rgb()
                result.setPixel(x, y, new_color)
        return result

    def rotate_left(self):
        """Поворот на 90° против часовой стрелки"""
        self.rotation_count = (self.rotation_count - 1) % 4
        self.update_display()
        self.status_label.setText("Повернуто влево")

    def rotate_right(self):
        """Поворот на 90° по часовой стрелке"""
        self.rotation_count = (self.rotation_count + 1) % 4
        self.update_display()
        self.status_label.setText("Повернуто вправо")

    def save_image(self):
        """Сохраняет текущее изображение в файл"""
        if not hasattr(self, 'current_pixmap') or self.current_pixmap is None:
            QMessageBox.warning(self, "Предупреждение", "Нечего сохранять — изображение не загружено.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить изображение как",
            "",
            "Изображения (*.png *.jpg *.bmp);;PNG (*.png);;JPEG (*.jpg);;BMP (*.bmp)"
        )

        if not file_path:
            return  

        if self.current_pixmap.save(file_path):
            self.status_label.setText(f"Изображение сохранено: {Path(file_path).name}")
            QMessageBox.information(self, "Сохранение", "Изображение успешно сохранено.")
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось сохранить изображение.")

    def resizeEvent(self, event):
        """Перерисовка при изменении размера окна"""
        super().resizeEvent(event)
        if self.original_image is not None:
            self.update_display()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImageEditor()
    window.setWindowTitle("Редактор изображений")
    window.show()
    sys.exit(app.exec())