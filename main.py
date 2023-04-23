from tkinter import *
import ctypes
import re
import os

print('IntCode, 1.0.0 version') #DONT TOUCH THIS IF YOU CONTRIBUTE SOMETHING
print('Made by Matveev_')
print('https://github.com/UnMatveev/IntCode')


def execute(event=None):
    with open('run.py', 'w', encoding='utf-8') as f:
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


ctypes.windll.shcore.SetProcessDpiAwareness(True)

root = Tk()
root.geometry('700x500')
root.title('IntCode')
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

editArea.bind('<KeyRelease>', changes)

editArea.bind("<KeyPress>", handle_opening_bracket)

root.bind('<Control-r>', execute)

changes()

root.mainloop()
