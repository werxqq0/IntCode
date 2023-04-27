from tkinter import *
import ctypes
import re
import os
from tkinter import filedialog
import tkinter.messagebox as messagebox
import json

with open('themes.json') as f:
    themes = json.load(f)

with open('languages.json', encoding='UTF-8') as f:
    languages = json.load(f)

with open('fonts.json', encoding='UTF-8') as f:
    fonts = json.load(f)

print(f'IntCode, 1.4.7 version') # DON'T TOUCH THIS IF YOU CONTRIBUTE SOMETHING
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
root.iconbitmap('images/icon.ico')
previousText = ''


default_theme = themes['default']
mariana_theme = themes['mariana']
one_dark_theme = themes['one_dark']
tomorrow_theme = themes['tomorrow']
dracula_theme = themes['dracula']
monokai_theme = themes['monokai']
material_theme = themes['material']
gruvbox_theme = themes['gruvbox']

lang = languages['default']
ru = languages['russian']
en = languages['english']

default_font = themes['default']

def restart_ide():
    msg = lang["IDE_restart"]
    choice = messagebox.askquestion(lang["IDE_restart_window"], msg, icon='warning')
    if choice == 'yes':
        print('Restaring IDE...')
        root.destroy()
        root.mainloop()

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
    restart_ide()

def set_material_style():
    global background, normal, w1, w2, w3, w4, w5, w6, w7, w8, comments, string, function
    background = rgb((material_theme['background']))
    normal = rgb((material_theme['normal']))
    w1 = rgb((material_theme['w1']))  # def
    w2 = rgb((material_theme['w2']))  # def name
    w3 = rgb((material_theme['w3']))
    w4 = rgb((material_theme['w4']))
    w5 = rgb((material_theme['w5']))  # print
    w6 = rgb((material_theme['w6']))
    w7 = rgb((material_theme['w7']))
    w8 = rgb((material_theme['w8']))  # self
    comments = rgb((material_theme['comments']))
    string = rgb((material_theme['string']))
    function = rgb((material_theme['function']))
    editArea.config(background=background, foreground=normal)
    for pat, col in repl:
        editArea.tag_configure(str(col), foreground=col)
    with open('themes.json', 'r') as f:
        data = json.load(f)
    data['default']['background'] = data['material']['background']
    data['default']['normal'] = data['material']['normal']
    data['default']['w1'] = data['material']['w1']
    data['default']['w2'] = data['material']['w2']
    data['default']['w3'] = data['material']['w3']
    data['default']['w4'] = data['material']['w4']
    data['default']['w5'] = data['material']['w5']
    data['default']['w6'] = data['material']['w6']
    data['default']['w7'] = data['material']['w7']
    data['default']['w8'] = data['material']['w8']
    data['default']['comments'] = data['material']['comments']
    data['default']['string'] = data['material']['string']
    data['default']['function'] = data['material']['function']
    with open('themes.json', 'w') as f:
        json.dump(data, f, indent=2)
    restart_ide()

def set_monokai_style():
    global background, normal, w1, w2, w3, w4, w5, w6, w7, w8, comments, string, function
    background = rgb((monokai_theme['background']))
    normal = rgb((monokai_theme['normal']))
    w1 = rgb((monokai_theme['w1']))  # def
    w2 = rgb((monokai_theme['w2']))  # def name
    w3 = rgb((monokai_theme['w3']))
    w4 = rgb((monokai_theme['w4']))
    w5 = rgb((monokai_theme['w5']))  # print
    w6 = rgb((monokai_theme['w6']))
    w7 = rgb((monokai_theme['w7']))
    w8 = rgb((monokai_theme['w8']))  # self
    comments = rgb((monokai_theme['comments']))
    string = rgb((monokai_theme['string']))
    function = rgb((monokai_theme['function']))
    editArea.config(background=background, foreground=normal)
    for pat, col in repl:
        editArea.tag_configure(str(col), foreground=col)
    with open('themes.json', 'r') as f:
        data = json.load(f)
    data['default']['background'] = data['monokai']['background']
    data['default']['normal'] = data['monokai']['normal']
    data['default']['w1'] = data['monokai']['w1']
    data['default']['w2'] = data['monokai']['w2']
    data['default']['w3'] = data['monokai']['w3']
    data['default']['w4'] = data['monokai']['w4']
    data['default']['w5'] = data['monokai']['w5']
    data['default']['w6'] = data['monokai']['w6']
    data['default']['w7'] = data['monokai']['w7']
    data['default']['w8'] = data['monokai']['w8']
    data['default']['comments'] = data['monokai']['comments']
    data['default']['string'] = data['monokai']['string']
    data['default']['function'] = data['monokai']['function']
    with open('themes.json', 'w') as f:
        json.dump(data, f, indent=2)
    restart_ide()

def set_dracula_style():
    global background, normal, w1, w2, w3, w4, w5, w6, w7, w8, comments, string, function
    background = rgb((dracula_theme['background']))
    normal = rgb((dracula_theme['normal']))
    w1 = rgb((dracula_theme['w1']))  # def
    w2 = rgb((dracula_theme['w2']))  # def name
    w3 = rgb((dracula_theme['w3']))
    w4 = rgb((dracula_theme['w4']))
    w5 = rgb((dracula_theme['w5']))  # print
    w6 = rgb((dracula_theme['w6']))
    w7 = rgb((dracula_theme['w7']))
    w8 = rgb((dracula_theme['w8']))  # self
    comments = rgb((dracula_theme['comments']))
    string = rgb((dracula_theme['string']))
    function = rgb((dracula_theme['function']))
    editArea.config(background=background, foreground=normal)
    for pat, col in repl:
        editArea.tag_configure(str(col), foreground=col)
    with open('themes.json', 'r') as f:
        data = json.load(f)
    data['default']['background'] = data['dracula']['background']
    data['default']['normal'] = data['dracula']['normal']
    data['default']['w1'] = data['dracula']['w1']
    data['default']['w2'] = data['dracula']['w2']
    data['default']['w3'] = data['dracula']['w3']
    data['default']['w4'] = data['dracula']['w4']
    data['default']['w5'] = data['dracula']['w5']
    data['default']['w6'] = data['dracula']['w6']
    data['default']['w7'] = data['dracula']['w7']
    data['default']['w8'] = data['dracula']['w8']
    data['default']['comments'] = data['dracula']['comments']
    data['default']['string'] = data['dracula']['string']
    data['default']['function'] = data['dracula']['function']
    with open('themes.json', 'w') as f:
        json.dump(data, f, indent=2)
    restart_ide()

def set_tomorrow_style():
    global background, normal, w1, w2, w3, w4, w5, w6, w7, w8, comments, string, function
    background = rgb((tomorrow_theme['background']))
    normal = rgb((tomorrow_theme['normal']))
    w1 = rgb((tomorrow_theme['w1']))  # def
    w2 = rgb((tomorrow_theme['w2']))  # def name
    w3 = rgb((tomorrow_theme['w3']))
    w4 = rgb((tomorrow_theme['w4']))
    w5 = rgb((tomorrow_theme['w5']))  # print
    w6 = rgb((tomorrow_theme['w6']))
    w7 = rgb((tomorrow_theme['w7']))
    w8 = rgb((tomorrow_theme['w8']))  # self
    comments = rgb((tomorrow_theme['comments']))
    string = rgb((tomorrow_theme['string']))
    function = rgb((tomorrow_theme['function']))
    editArea.config(background=background, foreground=normal)
    for pat, col in repl:
        editArea.tag_configure(str(col), foreground=col)
    with open('themes.json', 'r') as f:
        data = json.load(f)
    data['default']['background'] = data['tomorrow']['background']
    data['default']['normal'] = data['tomorrow']['normal']
    data['default']['w1'] = data['tomorrow']['w1']
    data['default']['w2'] = data['tomorrow']['w2']
    data['default']['w3'] = data['tomorrow']['w3']
    data['default']['w4'] = data['tomorrow']['w4']
    data['default']['w5'] = data['tomorrow']['w5']
    data['default']['w6'] = data['tomorrow']['w6']
    data['default']['w7'] = data['tomorrow']['w7']
    data['default']['w8'] = data['tomorrow']['w8']
    data['default']['comments'] = data['tomorrow']['comments']
    data['default']['string'] = data['tomorrow']['string']
    data['default']['function'] = data['tomorrow']['function']
    with open('themes.json', 'w') as f:
        json.dump(data, f, indent=2)
    restart_ide()

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
    restart_ide()

def set_gruvbox_style():
    global background, normal, w1, w2, w3, w4, w5, w6, w7, w8, comments, string, function
    background = rgb((gruvbox_theme['background']))
    normal = rgb((gruvbox_theme['normal']))
    w1 = rgb((gruvbox_theme['w1'])) #def
    w2 = rgb((gruvbox_theme['w2'])) #def name
    w3 = rgb((gruvbox_theme['w3']))
    w4 = rgb((gruvbox_theme['w4']))
    w5 = rgb((gruvbox_theme['w5'])) #print
    w6 = rgb((gruvbox_theme['w6']))
    w7 = rgb((gruvbox_theme['w7']))
    w8 = rgb((gruvbox_theme['w8'])) #self
    comments = rgb((gruvbox_theme['comments']))
    string = rgb((gruvbox_theme['string']))
    function = rgb((gruvbox_theme['function']))
    editArea.config(background=background, foreground=normal)
    for pat, col in repl:
        editArea.tag_configure(str(col), foreground=col)
    with open('themes.json', 'r') as f:
        data = json.load(f)
    data['default']['background'] = data['gruvbox']['background']
    data['default']['normal'] = data['gruvbox']['normal']
    data['default']['w1'] = data['gruvbox']['w1']
    data['default']['w2'] = data['gruvbox']['w2']
    data['default']['w3'] = data['gruvbox']['w3']
    data['default']['w4'] = data['gruvbox']['w4']
    data['default']['w5'] = data['gruvbox']['w5']
    data['default']['w6'] = data['gruvbox']['w6']
    data['default']['w7'] = data['gruvbox']['w7']
    data['default']['w8'] = data['gruvbox']['w8']
    data['default']['comments'] = data['gruvbox']['comments']
    data['default']['string'] = data['gruvbox']['string']
    data['default']['function'] = data['gruvbox']['function']
    with open('themes.json', 'w') as f:
        json.dump(data, f, indent=2)
    restart_ide()

background = rgb((default_theme['background'])) #background
normal = rgb((default_theme['normal'])) #normal text
w1 = rgb((default_theme['w1'])) #def
w2 = rgb((default_theme['w2'])) #def name
w3 = rgb((default_theme['w3'])) #+ - = ==
w4 = rgb((default_theme['w4'])) #None
w5 = rgb((default_theme['w5'])) #print
w6 = rgb((default_theme['w6'])) #class name
w7 = rgb((default_theme['w7'])) #numbers
w8 = rgb((default_theme['w8'])) #self, False, True
comments = rgb((default_theme['comments'])) #comments
string = rgb((default_theme['string'])) #text in ""
function = rgb((default_theme['function'])) #(doesnt used)
font = fonts['default_font']
font_size = fonts['default_size']

repl = [
    ['(^| )(and|as|assert|async|await|break|class|continue|del|elif|else|except|finally|for'
     '|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|return|try|while|with|yield|int|str|float|complex'
     'float|complex|list|tuple|range|dict|bool|set|frozeenset)($| )', w1],
    ['(public|args)', w4],
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
    ['(?<!\w)\\d+(?!\w)', w7],
    ['(get|write|print|open|__init__)', w5],
    ['#.*?$', comments],
    ['//.*?$', comments],
    ['(?<=\.)\w+', w2],
]

def set_consolas_font():
    with open('fonts.json', 'r', encoding='UTF-8') as f:
        data = json.load(f)

    data['default_font'] = data['consolas']

    with open('fonts.json', 'w', encoding='UTF-8') as f:
        json.dump(data, f, indent=2)
    restart_ide()

def set_english_language():
    with open('languages.json', 'r', encoding='UTF-8') as f:
        data = json.load(f)

    data['default']['en_lang'] = data['english']['en_lang']
    data['default']['ru_lang'] = data['english']['ru_lang']
    data['default']['languages'] = data['english']['languages']
    data['default']['themes'] = data['english']['themes']
    data['default']['exit'] = data['english']['exit']
    data['default']['compile'] = data['english']['compile']
    data['default']['save_as'] = data['english']['save_as']
    data['default']['open_file'] = data['english']['open_file']
    data['default']['new_file'] = data['english']['new_file']
    data['default']['about'] = data['english']['about']
    data['default']['settings'] = data['english']['settings']
    data['default']['tools'] = data['english']['tools']
    data['default']['view'] = data['english']['view']
    data['default']['find'] = data['english']['find']
    data['default']['edit'] = data['english']['edit']
    data['default']['file'] = data['english']['file']
    data['default']['IDE_restart'] = data['english']['IDE_restart']
    data['default']['IDE_restart_window'] = data['english']['IDE_restart_window']
    data['default']['fonts'] = data['english']['fonts']
    data['default']['size'] = data['english']['size']

    with open('languages.json', 'w', encoding='UTF-8') as f:
        json.dump(data, f, indent=2)
    restart_ide()


def set_russian_language():
    with open('languages.json', 'r', encoding='UTF-8') as f:
        data = json.load(f)

    data['default']['en_lang'] = data['russian']['en_lang']
    data['default']['ru_lang'] = data['russian']['ru_lang']
    data['default']['languages'] = data['russian']['languages']
    data['default']['themes'] = data['russian']['themes']
    data['default']['exit'] = data['russian']['exit']
    data['default']['compile'] = data['russian']['compile']
    data['default']['save_as'] = data['russian']['save_as']
    data['default']['open_file'] = data['russian']['open_file']
    data['default']['new_file'] = data['russian']['new_file']
    data['default']['about'] = data['russian']['about']
    data['default']['settings'] = data['russian']['settings']
    data['default']['tools'] = data['russian']['tools']
    data['default']['view'] = data['russian']['view']
    data['default']['find'] = data['russian']['find']
    data['default']['edit'] = data['russian']['edit']
    data['default']['file'] = data['russian']['file']
    data['default']['IDE_restart'] = data['russian']['IDE_restart']
    data['default']['IDE_restart_window'] = data['russian']['IDE_restart_window']
    data['default']['fonts'] = data['russian']['fonts']
    data['default']['size'] = data['russian']['size']

    with open('languages.json', 'w', encoding='UTF-8') as f:
        json.dump(data, f, indent=2)
    restart_ide()

editArea = Text(
    root, background=background, foreground=normal, insertbackground=normal, relief=FLAT, borderwidth=15,
    font=(font, font_size)
)

editArea.pack(fill=BOTH, expand=1)

editArea.insert('1.0', '''"""// Java program to print the sum of two numbers
class Main {
  public static void main(String[] args) {
    int num1 = 5;
    int num2 = 10;
    int sum = num1 + num2;
    System.out.println("The sum of " + num1 + " and " + num2 + " is: " + sum);
  }
}
"""

print('Hello, mir')
''')

mmenu = Menu(root)
root.config(menu=mmenu)

file = Menu(mmenu, tearoff=False)
edit = Menu(mmenu, tearoff=False)
find = Menu(mmenu, tearoff=False)
view = Menu(mmenu, tearoff=False)
tools = Menu(mmenu, tearoff=False)
settings = Menu(mmenu, tearoff=False)
about = Menu(mmenu, tearoff=False)

mmenu.add_cascade(label=lang['file'],
                  menu=file)
mmenu.add_cascade(label=lang['edit'],
                  menu=edit)
""" mmenu.add_cascade(label=lang['find'],
                     menu=find)
mmenu.add_cascade(label=lang['view'],
                     menu=view)
mmenu.add_cascade(label=lang['tools'],
                     menu=tools) """
mmenu.add_cascade(label=lang['settings'],
                     menu=settings)
mmenu.add_cascade(label=lang['about'],
                  menu=about)

editArea.bind('<KeyRelease>', changes)
editArea.bind("<KeyPress>", handle_opening_bracket)
editArea.bind("<Tab>", handle_tab)
editArea.bind('<Return>', handle_enter)
editArea.bind("<BackSpace>", handle_backspace)

file.add_command(label=lang['new_file'], command=new_file)
file.add_command(label=lang['open_file'], command=open_file)
file.add_command(label=lang['save_as'], command=save_file)
file.add_separator()
file.add_command(label=lang['compile'], command=execute)
file.add_separator()
file.add_command(label=lang['exit'], command=exit_program)

languages = Menu(settings, tearoff=False)
settings.add_cascade(label=lang['languages'], menu=languages)
languages.add_command(label=lang['en_lang'], command=set_english_language)
languages.add_command(label=lang['ru_lang'], command=set_russian_language)

themes = Menu(settings, tearoff=False)
settings.add_cascade(label=lang['themes'], menu=themes)
themes.add_command(label="One Dark", command=set_one_dark_style)
themes.add_command(label="Mariana", command=set_mariana_style)
themes.add_command(label="Dracula", command=set_dracula_style)
themes.add_command(label="Tomorrow", command=set_tomorrow_style)
themes.add_command(label="Monokai", command=set_monokai_style)
themes.add_command(label="Material", command=set_material_style)
themes.add_command(label="Gruvbox", command=set_gruvbox_style)

fonts = Menu(settings, tearoff=False)
settings.add_cascade(label=lang['fonts'], menu=fonts)
font_options = Menu(fonts, tearoff=False)
fonts.add_cascade(label="Select Font", menu=font_options)
font_options.add_command(label="Consolas", command=set_consolas_font)
size_options = Menu(fonts, tearoff=False)
fonts.add_cascade(label="Select Size", menu=size_options)
size_options.add_command(label="5")
size_options.add_command(label="6")
size_options.add_command(label="7")

about.add_command(label="GitHub", command=about_github)

changes()

root.mainloop()
