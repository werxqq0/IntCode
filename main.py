from tkinter import *
import ctypes
import re
import os
from tkinter import filedialog
import json

with open('themes.json') as f:
    themes = json.load(f)

print(f'IntCode, 1.3.1 version') # DON'T TOUCH THIS IF YOU CONTRIBUTE SOMETHING
print('Made by Matveev_')
print('https://github.com/UnMatveev/IntCode')

py_compiler = 'run.py'
win = 'start cmd /K "python run.py"'
Linux = {'ubuntu': 'gnome-terminal -- bash -c "python3 run.py; exec bash"'}

def execute(event=True):
    with open(py_compiler, 'w', encoding='utf-8') as f:
        f.write(editArea.get('1.0', END))

    os.system(win)  # or (Linux['ubuntu'])


def changes(event=True):
    global previousText

    if editArea.get('1.0', END) == previousText:
        return

    for tag in editArea.tag_names():
        editArea.tag_remove(tag, '1.0', 'end')

    i = 0
    for pattern, color in repl:
        for start, end in search_re(pattern, editArea.get('1.0', END)):
            editArea.tag_add(f'{i}', start, end)
            editArea.tag_config(f'{i}', foreground=color)

            i += 1

    previousText = editArea.get('1.0', END)


def search_re(pattern, text):
    matches = []
    text = text.splitlines()

    for i, line in enumerate(text):
        for match in re.finditer(pattern, line):
            matches.append((f'{i + 1}.{match.start()}', f'{i + 1}.{match.end()}'))

    return matches


def rgb(color):
    return '#{:02x}{:02x}{:02x}'.format(*color)


def handle_opening_bracket(event):
    opening_bracket = event.char

    brackets = {
        "(": ")",
        "{": "}",
        "[": "]",
        "'": "'",
        '"': '"',
    }

    if opening_bracket in brackets:
        closing_bracket = brackets[opening_bracket]
        editArea.insert(INSERT, closing_bracket)
        editArea.mark_set(INSERT, f"{INSERT}-1c")


def handle_tab(event):
    editArea.insert(INSERT, " " * 4)
    return 'break'


def handle_enter(event):
    cursor_position = editArea.index(INSERT)

    current_line_text = editArea.get(f"{cursor_position} linestart", cursor_position)

    if current_line_text.endswith(":"):
        indent = len(current_line_text) - len(current_line_text.lstrip())

        editArea.insert(INSERT, "\n" + " " * (indent + 4))
        return "break"
    else:
        indent = len(current_line_text) - len(current_line_text.lstrip())
        next_char = editArea.get(cursor_position)

        if next_char in [")", "]", "}"]:
            editArea.insert(INSERT, f"\n{' ' * (indent + 4)}\n")
            editArea.mark_set(INSERT, f"{cursor_position}+5c")
        else:
            editArea.insert(INSERT, "\n" + " " * indent)
        return "break"


def handle_backspace(event):
    cursor_position = editArea.index(INSERT)

    current_line_text = editArea.get(f"{cursor_position} linestart", cursor_position)

    if current_line_text.endswith("    "):
        editArea.delete(f"{cursor_position}-4c", cursor_position)
        return "break"

    prev_char = editArea.get(cursor_position + " - 1c")
    next_char = editArea.get(cursor_position)

    brackets = {
        "(": ")",
        "{": "}",
        "[": "]",
        "'": "'",
        '"': '"',
    }

    if prev_char in brackets and next_char in brackets.values() and brackets[prev_char] == next_char:
        editArea.delete(cursor_position, f"{cursor_position}+1c")

    return None


def handle_enter_second(event):
    # получаем координаты текущей выделенной области
    sel_start, sel_end = editArea.tag_ranges("sel")

    # если выделения нет, то не обрабатываем
    if not sel_start or not sel_end:
        return

    # получаем текст между выделенными координатами
    text = editArea.get(sel_start, sel_end)

    # определяем тип скобки, если это скобки вообще
    if text in ["()", "[]", "{}"]:
        # получаем координаты курсора
        cursor = editArea.index(INSERT)

        # определяем новые координаты для скобки
        row, col = map(int, cursor.split("."))
        new_row, new_col = row + 2, col

        # перемещаем скобку в новую позицию
        editArea.delete(sel_start, sel_end)
        editArea.insert(f"{new_row}.{new_col}", text)

        # вставляем отступ
        editArea.insert(cursor, "\n" + " " * 4)

        # устанавливаем курсор в новую позицию
        editArea.mark_set(INSERT, f"{new_row}.{new_col + 4}")


def on_font_change(event):
    # Обработчик изменения размера шрифта"""
    current_font_size = int(editArea['font'].split()[1])
    # изменяем размер шрифта в зависимости от направления прокрутки
    if event.num == 5 or event.delta == -120:
        new_font_size = max(current_font_size - 1, 10)
    elif event.num == 4 or event.delta == 120:
        new_font_size = min(current_font_size + 1, 45)
    else:
        return

    editArea.yview_moveto(editArea.yview()[0])
    editArea['yscrollcommand'] = None

    editArea.configure(font=(font, new_font_size))


def highlight_functions(text):
    # Регулярное выражение для поиска имен функций
    pattern = r'\b\w+\('

    # Ищем имена функций в тексте и проверяем их наличие в текущем контексте
    for match in re.finditer(pattern, text):
        func_name = match.group()[:-1]
        if func_name in globals() or func_name in locals():
            yield match.start(), match.end(), function


def new_file():
    editArea.delete("1.0", END)


def save_file():
    file = filedialog.asksaveasfile(mode="w", defaultextension=".txt")
    if file is not None:
        text = str(editArea.get(1.0, END))
        file.write(text)
        file.close()


def open_file():
    file = filedialog.askopenfile(mode="r")
    if file is not None:
        content = file.read()
        editArea.delete(1.0, END)
        editArea.insert(END, content)
        file.close()


def exit_program():
    root.destroy()


def about_github():
    os.system('start https://github.com/UnMatveev/IntCode')


ctypes.windll.shcore.SetProcessDpiAwareness(True)

sw = '700'
hw = '500'
shw = f'{sw}x{hw}'

root = Tk()
root.geometry(shw)
root.title(f'IntCode - {py_compiler}')
previousText = ''

default_theme = themes['default']
mariana_theme = themes['mariana']
one_dark_theme = themes['one_dark']

def set_one_dark_style():
    global background, normal, w1, w2, w3, w4, w5, w6, w7, w8, comments, string, function
    background = rgb((one_dark_theme['background']))
    normal = rgb((one_dark_theme['normal']))
    w1 = rgb((one_dark_theme['w1']))  # def
    w2 = rgb((one_dark_theme['w2']))  # def name
    w3 = rgb((one_dark_theme['w3']))
    w4 = rgb((one_dark_theme['w4']))
    w5 = rgb((one_dark_theme['w5']))  # print
    w6 = rgb((one_dark_theme['w6']))
    w7 = rgb((one_dark_theme['w7']))
    w8 = rgb((one_dark_theme['w8']))  # self
    comments = rgb((one_dark_theme['comments']))
    string = rgb((one_dark_theme['string']))
    function = rgb((one_dark_theme['function']))
    editArea.config(background=background, foreground=normal)
    for pat, col in repl:
        editArea.tag_configure(str(col), foreground=col)
    with open('themes.json', 'r') as f:
        data = json.load(f)
    data['default']['background'] = data['one_dark']['background']
    data['default']['normal'] = data['one_dark']['normal']
    data['default']['w1'] = data['one_dark']['w1']
    data['default']['w2'] = data['one_dark']['w2']
    data['default']['w3'] = data['one_dark']['w3']
    data['default']['w4'] = data['one_dark']['w4']
    data['default']['w5'] = data['one_dark']['w5']
    data['default']['w6'] = data['one_dark']['w6']
    data['default']['w7'] = data['one_dark']['w7']
    data['default']['w8'] = data['one_dark']['w8']
    data['default']['comments'] = data['one_dark']['comments']
    data['default']['string'] = data['one_dark']['string']
    data['default']['function'] = data['one_dark']['function']
    with open('themes.json', 'w') as f:
        json.dump(data, f, indent=2)

def set_mariana_style():
    global background, normal, w1, w2, w3, w4, w5, w6, w7, w8, comments, string, function
    background = rgb((mariana_theme['background']))
    normal = rgb((mariana_theme['normal']))
    w1 = rgb((mariana_theme['w1'])) #def
    w2 = rgb((mariana_theme['w2'])) #def name
    w3 = rgb((mariana_theme['w3']))
    w4 = rgb((mariana_theme['w4']))
    w5 = rgb((mariana_theme['w5'])) #print
    w6 = rgb((mariana_theme['w6']))
    w7 = rgb((mariana_theme['w7']))
    w8 = rgb((mariana_theme['w8'])) #self
    comments = rgb((mariana_theme['comments']))
    string = rgb((mariana_theme['string']))
    function = rgb((mariana_theme['function']))
    editArea.config(background=background, foreground=normal)
    for pat, col in repl:
        editArea.tag_configure(str(col), foreground=col)
    with open('themes.json', 'r') as f:
        data = json.load(f)
    data['default']['background'] = data['mariana']['background']
    data['default']['normal'] = data['mariana']['normal']
    data['default']['w1'] = data['mariana']['w1']
    data['default']['w2'] = data['mariana']['w2']
    data['default']['w3'] = data['mariana']['w3']
    data['default']['w4'] = data['mariana']['w4']
    data['default']['w5'] = data['mariana']['w5']
    data['default']['w6'] = data['mariana']['w6']
    data['default']['w7'] = data['mariana']['w7']
    data['default']['w8'] = data['mariana']['w8']
    data['default']['comments'] = data['mariana']['comments']
    data['default']['string'] = data['mariana']['string']
    data['default']['function'] = data['mariana']['function']
    with open('themes.json', 'w') as f:
        json.dump(data, f, indent=2)

background = rgb((default_theme['background']))
normal = rgb((default_theme['normal']))
w1 = rgb((default_theme['w1'])) #def
w2 = rgb((default_theme['w2'])) #def name
w3 = rgb((default_theme['w3']))
w4 = rgb((default_theme['w4']))
w5 = rgb((default_theme['w5'])) #print
w6 = rgb((default_theme['w6']))
w7 = rgb((default_theme['w7']))
w8 = rgb((default_theme['w8'])) #self
comments = rgb((default_theme['comments']))
string = rgb((default_theme['string']))
function = rgb((default_theme['function']))
font = 'Consolas'
font_size = 15

repl = [
    ['(^| )(and|as|assert|async|await|break|class|continue|del|elif|else|except|finally|for'
     '|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|return|try|while|with|yield)($| )', w1],
    ['(?<!self)\.(?=\w+)', w8],
    ['(self|False|True)', w8],
    ['\w+(?=\()', w2],
    ['"[^"]*"', string],
    ["'[^']*'", string],
    [r'==|!=|>|<|>=|<=|=|\+|\-|\*|\/|\%', w3],
    ['(None)', w4],
    ['".*?"', string],
    ['\".*?\"', string],
    ['\'.*?\'', string],
    ['(?<=class\s)\w+', w6],
    ['class', w1],
    ['(?<=def\s)\w+', w2],
    ['def', w1],
    ['(?<=\.)\w+', w2],
    ['(?<!\w)\\d+(?!\w)', w7],
    ['#.*?$', comments],
    ['(get|write|print|open|__init__)', w5],
]

editArea = Text(
    root, background=background, foreground=normal, insertbackground=normal, relief=FLAT, borderwidth=30,
    font=(font, font_size)
)

editArea.pack(fill=BOTH, expand=1)

editArea.insert('1.0', '''# Определение функции
def greet(name):
    print(f"Привет, {name}!")

# Определение класса
class Car:
    # Определение конструктора
    def __init__(self, make, model, year):
        self.make = make
        self.model = model
        self.year = year
        self.odometer_reading = 0
    
    # Определение метода
    def get_descriptive_name(self):
        long_name = f"{self.year} {self.make} {self.model}"
        return long_name.title()
    
    # Определение метода
    def read_odometer(self):
        print(f"Пробег этого автомобиля составляет {self.odometer_reading} миль.")
    
    # Определение метода
    def update_odometer(self, mileage):
        if mileage >= self.odometer_reading:
            self.odometer_reading = mileage
        else:
            print("Вы не можете откатить показания одометра!")

# Создание экземпляра класса
my_car = Car('audi', 'a4', 2022)
print(my_car.get_descriptive_name())

# Вызов метода
my_car.read_odometer()

# Обновление атрибута
my_car.odometer_reading = 100

# Вызов метода
my_car.read_odometer()

# Обновление атрибута через метод
my_car.update_odometer(200)

# Вызов метода
my_car.read_odometer()

# Вызов функции
greet("Михаил")''')

mmenu = Menu(root)
root.config(menu=mmenu)

file = Menu(mmenu, tearoff=False)
edit = Menu(mmenu, tearoff=False)
find = Menu(mmenu, tearoff=False)
view = Menu(mmenu, tearoff=False)
tools = Menu(mmenu, tearoff=False)
settings = Menu(mmenu, tearoff=False)
about = Menu(mmenu, tearoff=False)

mmenu.add_cascade(label="File",
                  menu=file)
mmenu.add_cascade(label="Edit",
                  menu=edit)
""" mmenu.add_cascade(label="Find",
                     menu=find)
mmenu.add_cascade(label="View",
                     menu=view)
mmenu.add_cascade(label="Tools",
                     menu=tools) """
mmenu.add_cascade(label="Settings",
                     menu=settings)
mmenu.add_cascade(label="About",
                  menu=about)

editArea.bind('<KeyRelease>', changes)
editArea.bind("<KeyPress>", handle_opening_bracket)
editArea.bind("<Tab>", handle_tab)
editArea.bind('<Return>', handle_enter)
editArea.bind("<BackSpace>", handle_backspace)
editArea.bind('<Control-MouseWheel>', on_font_change)

file.add_command(label="New File", command=new_file)
file.add_command(label="Open File...", command=open_file)
file.add_command(label="Save As...", command=save_file)
file.add_separator()
file.add_command(label="Compile", command=execute)
file.add_separator()
file.add_command(label="Exit", command=exit_program)

themes = Menu(settings, tearoff=False)
settings.add_cascade(label="Themes", menu=themes)
themes.add_command(label="One Dark", command=set_one_dark_style)
themes.add_command(label="Mariana", command=set_mariana_style)

about.add_command(label="GitHub", command=about_github)

changes()

root.mainloop()
