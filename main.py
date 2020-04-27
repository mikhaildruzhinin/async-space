import time
import curses
import asyncio
import random
import itertools
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
    frame1, frame2 = frames
    draw_frame(canvas, row, column, frame1)
    while True:
        rows_direction, columns_direction, space_pressed = read_controls(canvas)
        draw_frame(canvas, row, column, frame1, negative=True)
        if max(max_y, row + rows_direction + frame_rows + 1) == max_y and (row + rows_direction) > 0:
            row += rows_direction
        if max(max_x, column + columns_direction + frame_columns + 1) == max_x and (column + columns_direction) > 0:
            column += columns_direction
        draw_frame(canvas, row, column, frame2)
        await asyncio.sleep(0)

        rows_direction, columns_direction, space_pressed = read_controls(canvas)
        draw_frame(canvas, row, column, frame2, negative=True)
        if max(max_y, row + rows_direction + frame_rows + 1) == max_y and (row + rows_direction) > 0:
            row += rows_direction
        if max(max_x, column + columns_direction + frame_columns + 1) == max_x and (column + columns_direction) > 0:
            column += columns_direction
        draw_frame(canvas, row, column, frame1)
        await asyncio.sleep(0)

def draw(canvas):
    curses.curs_set(False)
    canvas.nodelay(True)
    max_y, max_x = canvas.getmaxyx()
    num_stars = int(0.05 * ((max_x - 2) * (max_y - 2)))

    with open('files/rocket_frame_1.txt', 'rt') as src:
        rocket_frame_1 = src.read()

    with open('files/rocket_frame_2.txt', 'rt') as src:
        rocket_frame_2 = src.read()

    frame_rows, frame_columns = get_frame_size(rocket_frame_1)

    frames = (rocket_frame_1, rocket_frame_2)

    coroutines = []

    for i in range(num_stars):
        row = random.randint(1, max_y - 2)
        column = random.randint(1, max_x - 2)
        symbol = random.choice('+*.:∴')
        coroutine = blink(canvas, row, column, symbol)
        coroutines.append(coroutine)

    coroutine = animate_spaceship(canvas, max_y - frame_rows - 1, max_x / 2 - frame_columns / 2 + 1, frames, max_x, max_y, frame_rows, frame_columns)
    coroutines.append(coroutine)

    coroutine = fire(canvas, max_y - frame_rows - 1, max_x / 2)
    coroutines.append(coroutine)

    canvas.border()

    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        if len(coroutines) == 0:
            break
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)
  
if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
