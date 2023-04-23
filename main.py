from tkinter import *
import ctypes
import re
import os
from tkinter import filedialog

print('IntCode, 1.1.0 version')  # DON'T TOUCH THIS IF YOU CONTRIBUTE SOMETHING
print('Made by Matveev_')
print('https://github.com/UnMatveev/IntCode')

py_compiler = 'run.py'


def execute(event=None):
    with open(py_compiler, 'w', encoding='utf-8') as f:
        f.write(editArea.get('1.0', END))

    os.system('start cmd /K "python run.py"')


def changes(event=None):
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

        editArea.insert(INSERT, "\n" + " " * indent)
        return "break"


def handle_backspace(event):
    cursor_position = editArea.index(INSERT)

    # Получаем текст текущей строки
    current_line_text = editArea.get(f"{cursor_position} linestart", cursor_position)

    # Проверяем, заканчивается ли строка на 4 пробела
    if current_line_text.endswith("    "):
        # Удаляем все 4 пробела
        editArea.delete(f"{cursor_position}-4c", cursor_position)
        # Возвращаем строку "break", чтобы избежать удаления символа по умолчанию
        return "break"

    # Далее, проверяем, является ли предыдущий символ скобкой или кавычкой
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


ctypes.windll.shcore.SetProcessDpiAwareness(True)

root = Tk()
root.geometry('700x500')
root.title(f'IntCode - {py_compiler}')
previousText = ''

normal = rgb((234, 234, 234))
keywords = rgb((234, 95, 95))
comments = rgb((95, 234, 165))
string = rgb((234, 162, 95))
function = rgb((95, 211, 234))
background = rgb((42, 42, 42))
font = 'Consolas'

repl = [
    ['(^| )(False|None|True|and|as|assert|async|await|break|class|continue|def|del|elif|else|except|finally|for'
     '|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|return|try|while|with|yield)($| )', keywords],
    ['".*?"', string],
    ['\".*?\"', string],
    ['#.*?$', comments],
]


editArea = Text(
    root, background=background, foreground=normal, insertbackground=normal, relief=FLAT, borderwidth=30, font=font
)

editArea.pack(fill=BOTH, expand=1)

editArea.insert('1.0', '''from random import randint

print([randint(1, 20) for i in range(10)])

''')

menu = Menu(root)
root.config(menu=menu)
file_menu = Menu(menu, tearoff=False)
menu.add_cascade(label="File", menu=file_menu)


# Добавление кнопок в меню "File"
file_menu.add_command(label="New", command=new_file)
file_menu.add_command(label="Open", command=open_file)
file_menu.add_command(label="Save", command=save_file)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=exit_program)

editArea.bind('<KeyRelease>', changes)

editArea.bind("<KeyPress>", handle_opening_bracket)
editArea.bind("<Tab>", handle_tab)
editArea.bind('<Return>', handle_enter)
editArea.bind("<BackSpace>", handle_backspace)

root.bind('<Control-r>', execute)

changes()

root.mainloop()
