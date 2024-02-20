import threading
import tkinter as tk

from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
from rembg import remove


class FonIsGoneBackgroundRemoverApp:
    def __init__(self, master):
        self.master = master
        master.title("Удалить фон с картинки. Fon is gone.")    # Заголовок главного окна.
        # Размеры и положение окна (ширина x высота + горизонтальное положение + вертикальное положение)
        master.geometry("500x500+700+200")
        master.resizable(width=True, height=True)    # Может ли окно изменять свои размеры?

        # Поля ввода начального и финального изображения
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()

        # Создадим основной Frame
        control_frame = tk.Frame(master)
        control_frame.pack(side=tk.TOP, fill=tk.X)

        # Надпись и поле ввода для пути к изображению
        tk.Label(control_frame, text="Выбрать изображение:").grid(row=0, column=0, sticky="w")
        tk.Entry(control_frame, textvariable=self.input_path, width=40,
                 state="readonly").grid(row=0, column=1, sticky="we")
        tk.Button(control_frame, text="Открыть файл", bg="light gray", command=self.browse_input).grid(row=0, column=2)

        # Надпись и поле ввода для пути к результату
        tk.Label(control_frame, text="Сохранить результат:").grid(row=1, column=0, sticky="w")
        tk.Entry(control_frame, textvariable=self.output_path, width=40,
                 state="readonly").grid(row=1, column=1, sticky="we")
        tk.Button(control_frame, text="Сохранить как", command=self.browse_output).grid(row=1, column=2)

        # Кнопка для запуска удаления фона
        tk.Button(control_frame, text="Удалить фон", bg="white",
                  command=self.remove_background).grid(row=2, column=0, columnspan=3, sticky="we")

        # Конфигурация столбцов grid для адаптации ширины виджетов
        control_frame.grid_columnconfigure(1, weight=1)

        # Место для отображения изображений
        image_frame = tk.Frame(self.master)
        image_frame.pack(fill=tk.BOTH, expand=True)

        # Изображение исходного изображения с заголовком
        self.label_original_img = tk.Label(image_frame)
        self.label_original_img.grid(row=1, column=0, padx=10, pady=10)
        self.label_original_title = tk.Label(image_frame, text="Исходное изображение")
        self.label_original_title.grid(row=0, column=0, padx=10, pady=10)

        # Изображение результата с заголовком
        self.label_result_img = tk.Label(image_frame)
        self.label_result_img.grid(row=1, column=1, padx=10, pady=10)
        self.label_result_title = tk.Label(image_frame, text="Изображение без фона")
        self.label_result_title.grid(row=0, column=1, padx=10, pady=10)

        # Обеспечение растяжения контента вместе с окном
        image_frame.grid_rowconfigure(0, weight=1)
        image_frame.grid_columnconfigure(0, weight=1)
        image_frame.grid_columnconfigure(1, weight=1)

        # Progress bar в режиме determinate, чтобы без начала и конца
        self.progress_bar = ttk.Progressbar(control_frame, mode='determinate')
        self.progress_bar.grid(row=3, column=0, columnspan=3, sticky='we')

        # Добавляем фиксированную картинку ниже выходных картинок
        fixed_image = Image.open("fixed_image.jpg")
        fixed_image = fixed_image.resize((480, 80))
        tk_fixed_image = ImageTk.PhotoImage(fixed_image)
        self.label_fixed_img = tk.Label(self.master, image=tk_fixed_image)
        self.label_fixed_img.image = tk_fixed_image
        self.label_fixed_img.pack()  # Отображаем фиксированную картинку под выходными картинками

    def browse_input(self):
        """
        Открывает диалоговое окно для выбора файла изображения и отображает его.
        Запрашивает у пользователя выбор файла изображения с помощью
        filedialog.askopenfilename. Затем устанавливает путь в переменную StringVar
        и пытается открыть файл как изображение. Если файл не является
        изображением, выводит сообщение об ошибке и обнуляет путь.
        """
        file_path = filedialog.askopenfilename(filetypes=[("Изображения", "*.png;*.jpg;*.jpeg;*.gif;*.bmp;*.webp")])
        self.input_path.set(file_path)
        # Используем PIL, чтобы попробовать открыть файл как изображение, и обработать исключение, если это не удается
        if file_path:
            try:
                self.open_image(file_path)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Выбранный файл не является изображением. {str(e)}. Файл уничтожен.")
                self.input_path.set("")  # Обнулить путь, так как это не изображение. Угрожать пользователю.

    def open_image(self, file_path):
        """
        Открывает изображение по указанному пути, уменьшает его до максимального размера
        для удобного просмотра, и отображает его на месте Label.
        :param file_path: Путь к изображению, которое нужно открыть.
        """
        max_size = (250, 250)    # Максимальный размер под предпросмотр
        original_image = Image.open(file_path)
        # Уменьшаем изображение, сохраняя пропорции
        original_image.thumbnail(max_size, Image.Resampling.LANCZOS)
        tk_original_image = ImageTk.PhotoImage(original_image)
        self.label_original_img.config(image=tk_original_image)
        self.label_original_img.image = tk_original_image  # Сохранить ссылку на изображение

    def browse_output(self):
        """
        Открывает диалог сохранения файла, предварительно устанавливая расширение .png и
        тип файла PNG. Если пользователь не указал расширение, добавляет его автоматически.
        Устанавливает полученный путь в переменную self.output_path.
        """
        file_path = filedialog.asksaveasfilename(initialfile="without_fon", defaultextension=".png",
                                                 filetypes=[("PNG файл", "*.png")])
        if not file_path.endswith(".png"):
            file_path += "without_fon.png"    # Принудительный png
        self.output_path.set(file_path)

    def remove_background(self):
        """
        Запускает процесс удаления фона в отдельном потоке, чтобы не блокировать GUI.
        """
        threading.Thread(target=self.remove_background_thread).start()

    def remove_background_thread(self):
        """
        Выполняет обработку изображения в отдельном потоке.
        Обработка включает в себя удаление фона из выбранного изображения и сохранение
        результата по указанному пути. После завершения обработки обновляет отображение
        и останавливает индикатор выполнения.
        """
        self.progress_bar.start()  # Активируем индикатор выполнения

        input_path = self.input_path.get()
        output_path = self.output_path.get()

        if input_path and output_path:
            input_image = Image.open(input_path)
            output_image = remove(input_image)
            output_image.save(output_path)
            # После завершения обработки обновляем изображение и останавливаем индикатор выполнения
            self.update_progressbar(output_image)
        else:
            messagebox.showwarning("Ошибка", "Необходимо указать путь к изображению и путь для сохранения результата.")
            self.progress_bar.stop()  # Останавливаем индикатор выполнения в случае ошибки

    def update_progressbar(self, output_image):
        """
        Обновляет изображение в главном потоке GUI и останавливает индикатор выполнения.
        :param output_image: Обработанное изображение для отображения.
        """
        if self.master and hasattr(self.master, 'after'):
            self.master.after(0, self.show_output_image, output_image)
            self.progress_bar.stop()  # Останавливаем индикатор выполнения после обработки

    def show_output_image(self, output_image):
        """
            Обновляет отображение результата удаления фона на главном окне.
            Выводит информационное окно с сообщением об успешном удалении фона.
            :param output_image: Изображение без фона (PIL Image).
         """
        # Этот код теперь в отдельном методе, чтобы его было удобнее вызывать из update_progressbar
        max_width, max_height = (250, 250)
        ratio = min(max_width / output_image.width, max_height / output_image.height)
        new_size = (int(output_image.width * ratio), int(output_image.height * ratio))
        output_image = output_image.resize(new_size, Image.Resampling.LANCZOS)

        tk_result_image = ImageTk.PhotoImage(output_image)
        self.label_result_img.config(image=tk_result_image)
        self.label_result_img.image = tk_result_image  # Сохраняем ссылку на изображение
        messagebox.showinfo("Фон удален", "Фон был успешно удален!")


if __name__ == "__main__":
    root = tk.Tk()
    app = FonIsGoneBackgroundRemoverApp(root)
    root.mainloop()
