import sys
from datetime import datetime

from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtCore import Qt

# Импорт дизайна приложения
from euler_ui import Ui_euler_window


# Задание стиля элементам окна
STYLESHEET = """
#euler_window{
    background:#FFF;
    color: #000;
}

#func_line_edit{
    border-radius: 10px;
    border: 2px solid;
    font-family: "Webdings";
}

#x0_line_edit{
    border-radius: 8px;
    border: 2px solid;
    font-family: "Webdings";
}

#y0_line_edit{
    border-radius: 8px;
    border: 2px solid;
    font-family: "Webdings";
}

#a_line_edit{
    border-radius: 8px;
    border: 2px solid;
    font-family: "Webdings";
}

#b_line_edit{
    border-radius: 8px;
    border: 2px solid;
    font-family: "Webdings";
}
"""


class EulerWindow(QMainWindow, Ui_euler_window):
    """Класс окна приложения, вычисляющего дифур по методу Эйлера

    Принцип вычисления:
    1) Получение данных для вычисления
    2) Вычисление y(x) с шагом h/2 для погрешности
    3) Вычисление x
    4) Вычисление y(x) с шагом h (решение дифура)
    5) Вычисление погрешности
    6) Занесение данных в таблицу

    """

    # Переданный отрезок будет разбит на 4 части
    _n = 10

    _x_y_table_row_count = _n + 1

    def __init__(self):
        """Конструктор класса EulerWindow

        Подключение файла с дизайном приложения.
        Задание команд кнопкам Cancel и OK.
        Создание строк таблицы.
        Создание заголовков колонок таблицы.

        """

        # Обращение к классу QMainWindow
        # для дополнения текщего класса
        super().__init__()

        # Подключение дизайна
        self.setupUi(self)

        # Задание команд кнопкам OK и Cancel
        self.buttonBox.accepted.connect(self._set_values_in_table)
        self.buttonBox.rejected.connect(self.close)

        # Создание строк таблицы x_y_table
        self.x_y_table.setRowCount(self._x_y_table_row_count)

        # Задание заголовков таблицы x_y_table
        self.x_y_table.setHorizontalHeaderLabels(('x', 'y', 'dy'))

        # Установка курсора на поле для ввода функции
        self.func_line_edit.setFocus()

        # Определение взаимодействия с кнопкой Enter
        self._set_focus_by_enter()

        # Устанавка всплывающих подсказок
        self._set_tool_tips()

        # Установка стиля у элементов окна
        self.setStyleSheet(STYLESHEET)

    def _get_user_data(self):
        """Получение данных для решения уравнения

        Получение данных от пользователя.
        Вычисление шага интегрирования.

        """

        try:
            # Исходная функция
            self._func = self.func_line_edit.text()

            # y(x0) = y0
            self._x0 = float(self.x0_line_edit.text())
            self._y0 = float(self.y0_line_edit.text())

            # Отрезок от a до b
            self._a = float(self.a_line_edit.text())
            self._b = float(self.b_line_edit.text())

        except ValueError:
            QMessageBox.critical(
                self, 'Ошибка',
                'Неверный тип данных переданного значения',
                QMessageBox.Ok
            )

        # Шаг интегрирования
        self._h = (self._b - self._a) / self._n

        return self._h, self._x0, self._y0, self._func, self._n

    def _get_y_with_h_div_2(self):
        """Получение y c шагом h/2 для вычисления погрешности

        Погрешность вычисляется как
        модуль разности y(x) с шагом h и y(x) с шагом h/2.

        """

        h, x, y, func, n = self._get_user_data()

        # В y_with_h_div_2 первый элемент это y0,
        # полученный от пользователя.
        y_with_h_div_2 = [y]

        # Вычисляем y(x) для шага h/2 и заносим в список
        for i in range(2*n + 1):
            # Функция передается как строка,
            # поэтому используем eval
            # для исполнения выражения функции.
            y += h/2*eval(func)
            x += h/2

            y_with_h_div_2.append(round(y, 4))

        # Передаем каждый второй элемент из y_with_h_div_2,
        # т.к. вычисление основного y(x) происходит
        # для h, а не для h/2
        return y_with_h_div_2[::2]

    def _get_data(self):
        """Вычисление x, решения дифура и погрешности

        Получение данных пользователя.
        Получение y_with_h_div_2 для вычисление погрешности.
        Вычисление и внесение значений в списки.

        """

        h, x, y, func, n = self._get_user_data()

        y_with_h_div_2 = self._get_y_with_h_div_2()

        # Списки, в которые будут вноситься значения
        # x, y(решение дифура) и погрешности
        x_values, y_values, inaccuracy_values = [], [], []

        # Вычисление и внесение значений в списки
        for i in range(self._x_y_table_row_count):
            x_values.append(round(x, 4))
            y_values.append(round(y, 4))

            # Погрешность = |y(x) - y_with_h_div_2(x)|
            inaccuracy = round(abs(y - y_with_h_div_2[i]), 4)

            # Функция передается как строка,
            # поэтому используем eval
            # для исполнения выражения функции.
            y += h * eval(func)
            x += h

            inaccuracy_values.append(inaccuracy)

        return x_values, y_values, inaccuracy_values

    def _set_value_in_column(self, values, column_number, column_len):
        """Внесение значений из списка в колонку таблицы x_y_table"""

        for row_number in range(column_len):
            self.x_y_table.setItem(
                row_number,
                column_number,
                QTableWidgetItem(str(values[row_number]))
            )

    def _set_values_in_table(self):
        """Занесение данных в таблицу x_y_table"""

        # Текущее время
        start = datetime.now()

        # Получаем списки с x, y(решение дифура) и погрешностью
        x_values, y_values, inaccuracy_values = self._get_data()

        # Вставка x
        self._set_value_in_column(
            x_values, 0, self._x_y_table_row_count
        )

        # Вставка y
        self._set_value_in_column(
            y_values, 1, self._x_y_table_row_count
        )

        # Вставка погрешности
        self._set_value_in_column(
            inaccuracy_values, 2, self._x_y_table_row_count
        )

        # Вычисляем и выводим время решения уравнения
        print(
            "Время вычисления решения уравнения методом Эйлера:",
            datetime.now() - start
        )

    def keyPressEvent(self, QKeyEvent):
        """Связывание клавиш и команд"""

        # Выход из программы по нажатию на Esc
        if QKeyEvent.key() == Qt.Key_Escape:
            sys.exit()

    def _set_focus_by_enter(self):
        """Метод взаимодействия с Enter

        При нажатии на Enter курсор перемещается
        на следующее по логике поле,
        либо происходит заполнение таблицы (в случае последнего поля)

        """

        self.func_line_edit.returnPressed.connect(
            lambda: self.x0_line_edit.setFocus()
        )

        self.x0_line_edit.returnPressed.connect(
            lambda: self.y0_line_edit.setFocus()
        )

        self.y0_line_edit.returnPressed.connect(
            lambda: self.a_line_edit.setFocus()
        )

        self.a_line_edit.returnPressed.connect(
            lambda: self.b_line_edit.setFocus()
        )

        self.b_line_edit.returnPressed.connect(
            lambda: self._set_values_in_table()
        )

    def _set_tool_tips(self):
        """Установка подсказок для полей a и b"""

        # Подсказка для поля a
        self.a_line_edit.setToolTip("Начало отрезка")
        # Временная продолжительность подсказки a
        self.a_line_edit.setToolTipDuration(3000)

        # Подсказка для поля b
        self.b_line_edit.setToolTip("Конец отрезка")
        # Временная продолжительность подсказки b
        self.b_line_edit.setToolTipDuration(3000)


def main():
    """Основная функция

    Создание и отображение окна приложения.

    """

    euler_window = EulerWindow()
    euler_window.show()


if __name__ == '__main__':
    main()
