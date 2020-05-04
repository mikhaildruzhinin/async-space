import time
import curses
import asyncio
import random
from itertools import cycle
from curses_tools import draw_frame
from curses_tools import read_controls
from curses_tools import get_frame_size

TIC_TIMEOUT = 0.1

async def blink(canvas, row, column, symbol='*'):
    while True:
        for _ in range(random.randint(10, 30)):
            canvas.addstr(row, column, symbol, curses.A_DIM)
            await asyncio.sleep(0)
        
        for _ in range(3):
            canvas.addstr(row, column, symbol)
            await asyncio.sleep(0)

        for _ in range(5):
            canvas.addstr(row, column, symbol, curses.A_BOLD)
            await asyncio.sleep(0)

        for _ in range(3):
            canvas.addstr(row, column, symbol)
            await asyncio.sleep(0)

async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed

async def animate_spaceship(canvas, row, column, frames, max_x, max_y, frame_rows, frame_columns):
    old_frame = frames[0]
    for frame in cycle(frames):
        draw_frame(canvas, row, column, old_frame, negative=True)

        rows_direction, columns_direction, space_pressed = read_controls(canvas)

        if min(max_y, row + rows_direction + frame_rows) == max_y:
            row += (max_y - row - frame_rows)
        elif row + rows_direction < 1:
            row = 1
        else:
            row += rows_direction

        if min(max_x, column + columns_direction + frame_columns) == max_x:
            column += (max_x - column - frame_columns)
        elif column + columns_direction < 1:
            column = 1
        else:
            column += columns_direction
        
        draw_frame(canvas, row, column, frame)
        old_frame = frame
        await asyncio.sleep(0)

async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0

    while row < rows_number:
        draw_frame(canvas, row, column, garbage_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed

async def fill_orbit_with_garbage():
    pass

def draw(canvas):
    curses.curs_set(False)
    canvas.nodelay(True)
    rows, columns = canvas.getmaxyx() # window.getmaxyx() возвращает не координаты крайней ячейки, а ширину и высоту окна 
    max_y, max_x = rows - 1, columns - 1 # координаты крайней ячейки будут на 1 меньше ширины и высоты окна, потому что нумерация начинается с нуля
    border_size = 2
    num_stars = int(0.05 * ((max_x - border_size) * (max_y - border_size)))

    with open('files/rocket_frame_1.txt', 'rt') as src:
        rocket_frame_1 = src.read()

    with open('files/rocket_frame_2.txt', 'rt') as src:
        rocket_frame_2 = src.read()

    frame_rows, frame_columns = get_frame_size(rocket_frame_1)

    frames = [rocket_frame_1, rocket_frame_1, rocket_frame_2, rocket_frame_2]

    with open('files/duck.txt', 'rt') as src:
        duck = src.read()

    with open('files/hubble.txt', 'rt') as src:
        hubble = src.read()

    with open('files/lamp.txt', 'rt') as src:
        lamp = src.read()

    with open('files/trash_large.txt', 'rt') as src:
        trash_large = src.read()

    with open('files/trash_small.txt', 'rt') as src:
        trash_small = src.read()

    with open('files/trash_xl.txt', 'rt') as src:
        trash_xl = src.read()

    garbage_frames = [duck, lamp, trash_large, trash_small, trash_xl ]

    coroutines = []

    for i in range(num_stars):
        row = random.randint(1, max_y - border_size / 2)
        column = random.randint(1, max_x - border_size / 2)
        symbol = random.choice('+*.:∴')
        coroutine = blink(canvas, row, column, symbol)
        coroutines.append(coroutine)

    coroutine = animate_spaceship(canvas, max_y - frame_rows, max_x / 2 - frame_columns // 2, frames, max_x, max_y, frame_rows, frame_columns)
    coroutines.append(coroutine)

    coroutine = fire(canvas, max_y - frame_rows, max_x / 2)
    coroutines.append(coroutine)

    coroutine = fly_garbage(canvas, max_x / 2, random.choice(garbage_frames))
    coroutines.append(coroutine)

    coroutine = fill_orbit_with_garbage()
    coroutines.append(coroutine)

    canvas.border()

    while len(coroutines):
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)
  
if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
