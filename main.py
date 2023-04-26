from tkinter import *
import ctypes
import re
import os
from tkinter import filedialog

print(f'IntCode, 1.3 version') # DON'T TOUCH THIS IF YOU CONTRIBUTE SOMETHING
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


def rgb(rgb):
    return '#%02x%02x%02x' % rgb


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

background = rgb((40, 44, 52))
normal = rgb((195, 195, 195))
w1 = rgb((213, 95, 222))
w2 = rgb((88, 167, 222))
w3 = rgb((249, 123, 87))
w4 = rgb((222, 85, 84))
w5 = rgb((41, 185, 196))
w6 = rgb((229, 192, 123))
w7 = rgb((208, 140, 98))
comments = rgb((166, 172, 185))
string = rgb((136, 201, 118))
function = rgb((95, 211, 234))
font = 'Consolas'
font_size = 15

repl = [
    ['(^| )(and|as|assert|async|await|break|class|continue|del|elif|else|except|finally|for'
     '|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|return|try|while|with|yield)($| )', w1],
    ['(self|False|True)', w1],
    ['\w+(?=\()', w2],
    ['"[^"]*"', string],
    ["'[^']*'", string],
    ['(get|write|print|open)', w5],
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
    [r'\b\d+\.\d+\b', w7],
    ['(?<!\w)\\d+(?!\w)', w7],
    ['#.*?$', comments],
]

editArea = Text(
    root, background=background, foreground=normal, insertbackground=normal, relief=FLAT, borderwidth=30,
    font=(font, font_size)
)

editArea.pack(fill=BOTH, expand=1)

editArea.insert('1.0', '''Welcome.''')

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
                     menu=tools)
mmenu.add_cascade(label="Settings",
                     menu=settings) """
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

about.add_command(label="GitHub", command=about_github)

changes()

root.mainloop()
