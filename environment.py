import os
from constants import *
from state import State

"""
environment.py

This file contains a class representing a BeeBot environment and supporting helper methods. You should make use of this
class in your solver.

COMP3702 2024 Assignment 1 Support Code
"""


class Environment:
    """
    Instance of a BeeBot environment.

    The hex grid is indexed top to bottom, left to right (i.e. the top left corner has coordinates (0, 0) and the bottom
    right corner has coordinates (n_rows-1, n_cols-1)). Even numbered columns (starting from zero) are in the top half
    of the row, odd numbered columns are in the bottom half of the row.

    e.g.
        row 0, col 0            row 0, col 2                ...
                    row 0, col 1            row 0, col 3
        row 1, col 0            row 1, col 2                ...
                    row 1, col 1            row 1, col 3
            ...         ...         ...         ...
    """

    def __init__(self, filename, force_valid=True):
        """
        Process the given input file and create a new game environment instance based on the input file.

        :param filename: name of input file
        :param force_valid: When creating states, raise exception if the created State violates validity constraints
        """
        os.system('color')  # enable coloured terminal output

        self.force_valid = force_valid
        f = open(filename, 'r')

        self.n_rows = None
        self.n_cols = None
        self.cost_tgt = None
        self.time_tgt = None
        self.exp_tgt = None

        self.obstacle_map = None
        self.target_list = []

        self.BEE_init_posit = None
        self.BEE_init_orient = None

        widget_types_list = []
        widget_init_posits_list = []
        widget_init_orients_list = []

        line_num = 0
        row = None
        for line in f:
            line_num += 1

            # skip annotations in input file
            if line.strip()[0] == '#':
                continue

            # read meta data
            if self.n_rows is None or self.n_cols is None:
                try:
                    self.n_rows, self.n_cols = tuple([int(x) for x in line.strip().split(',')])
                    self.obstacle_map = [[0 for _ in range(self.n_cols)] for __ in range(self.n_rows)]
                except ValueError:
                    assert False, f'!!! Invalid input file - n_rows and n_cols (line {line_num}) !!!'
            elif self.cost_tgt is None:
                try:
                    self.cost_tgt = float(line.strip())
                except ValueError:
                    assert False, f'!!! Invalid input file - cost target (line {line_num}) !!!'
            elif self.time_tgt is None:
                try:
                    self.time_tgt = tuple([float(x) for x in line.strip().split(',')])
                except ValueError:
                    assert False, f'!!! Invalid input file - time target (line {line_num}) !!!'
            elif self.exp_tgt is None:
                try:
                    self.exp_tgt = tuple([int(x) for x in line.strip().split(',')])
                except ValueError:
                    assert False, f'!!! Invalid input file - nodes expanded target (line {line_num}) !!!'

            # read hex grid data
            if line[0] in ['/', '\\']:
                # handle start of new row
                if line[0] == '/':
                    if row is None:
                        row = 0
                    else:
                        row += 1
                    col_offset = 0
                    len_offset = 1 if self.n_cols % 2 == 1 else 0
                else:
                    col_offset = 1
                    len_offset = 0

                # split line into symbols and strip formatting characters
                symbols = [s.replace('\\', '').replace('/', '').replace('_', '') for s in line.strip().split('\\__/')]
                symbols = [s for s in symbols if len(s) > 0]    # remove empty symbols
                if len(symbols) != ((self.n_cols // 2) + len_offset):
                    assert False, f'!!! Invalid input file - incorrect hex grid row length (line {line_num}) !!!'

                # process the symbol in each cell of the row
                for col, sym in enumerate(symbols):
                    assert sym in ALL_VALID_SYMBOLS, \
                        f'!!! Invalid input file - unrecognised hex grid symbol (line {line_num}) !!!'
                    if sym == OBSTACLE:
                        self.obstacle_map[row][(2 * col) + col_offset] = 1
                    elif sym == TARGET:
                        self.target_list.append((row, (2 * col) + col_offset))
                    elif sym in BEE_ORIENTATIONS:
                        assert self.BEE_init_posit is None and self.BEE_init_orient is None, \
                            f'!!! Invalid input file - more than one initial BEE position (line {line_num}) !!!'
                        self.BEE_init_posit = (row, (2 * col) + col_offset)
                        self.BEE_init_orient = sym
                    elif sym[0] in WIDGET_TYPES:
                        w_type, w_orient = sym
                        assert w_orient in WIDGET_ORIENTS[w_type], \
                            f'!!! Invalid input file - invalid orientation for this widget type (line {line_num}) !!!'
                        widget_types_list.append(w_type)
                        widget_init_posits_list.append((row, (2 * col) + col_offset))
                        widget_init_orients_list.append(w_orient)

        assert row == self.n_rows - 1, '!!! Invalid input file - incorrect number of rows !!!'
        assert self.BEE_init_posit is not None and self.BEE_init_orient is not None,\
            '!!! Invalid input file - no initial BEE position !!!'

        self.widget_types = tuple(widget_types_list)
        self.widget_init_posits = tuple(widget_init_posits_list)
        self.widget_init_orients = tuple(widget_init_orients_list)
        self.n_widgets = len(self.widget_types)

    def get_init_state(self):
        """
        Get a state representation instance for the initial state.

        :return: initial state
        """
        return State(self, self.BEE_init_posit, self.BEE_init_orient, self.widget_init_posits,
                     self.widget_init_orients, self.force_valid)

    def perform_action(self, state, action):
        """
        Perform the given action on the given state, and return whether the action was successful (i.e. valid and
        collision free), the cost of performing the action, and the resulting new state.
        :param state:
        :param action:
        :return: (successful [True/False], cost [float], next_state [instance of State])
        """
        if action == SPIN_LEFT or action == SPIN_RIGHT:
            # no collision possible for spin actions
            cost = ACTION_BASE_COST[action]
            if action == SPIN_LEFT:
                new_orient = {BEE_UP: BEE_UP_LEFT,
                              BEE_UP_LEFT: BEE_DOWN_LEFT,
                              BEE_DOWN_LEFT: BEE_DOWN,
                              BEE_DOWN: BEE_DOWN_RIGHT,
                              BEE_DOWN_RIGHT: BEE_UP_RIGHT,
                              BEE_UP_RIGHT: BEE_UP}[state.BEE_orient]
            else:
                new_orient = {BEE_UP: BEE_UP_RIGHT,
                              BEE_UP_RIGHT: BEE_DOWN_RIGHT,
                              BEE_DOWN_RIGHT: BEE_DOWN,
                              BEE_DOWN: BEE_DOWN_LEFT,
                              BEE_DOWN_LEFT: BEE_UP_LEFT,
                              BEE_UP_LEFT: BEE_UP}[state.BEE_orient]
            new_state = State(self, state.BEE_posit, new_orient, state.widget_centres, state.widget_orients,
                              self.force_valid)
            return True, cost, new_state
        else:
            forward_direction = state.BEE_orient
            # get coordinates of position forward of the BEE
            forward_BEE_posit = get_adjacent_cell_coords(state.BEE_posit, forward_direction)
            if action == FORWARD:
                move_direction = state.BEE_orient
                new_BEE_posit = forward_BEE_posit
            else:
                move_direction = {BEE_UP: BEE_DOWN,
                                  BEE_DOWN: BEE_UP,
                                  BEE_UP_LEFT: BEE_DOWN_RIGHT,
                                  BEE_UP_RIGHT: BEE_DOWN_LEFT,
                                  BEE_DOWN_LEFT: BEE_UP_RIGHT,
                                  BEE_DOWN_RIGHT: BEE_UP_LEFT}[state.BEE_orient]
                new_BEE_posit = get_adjacent_cell_coords(state.BEE_posit, move_direction)

            # test for out of bounds
            nr, nc = new_BEE_posit
            if (not 0 <= nr < self.n_rows) or (not 0 <= nc < self.n_cols):
                return False, None, None

            # test for BEE collision with obstacle
            if self.obstacle_map[nr][nc]:
                return False, None, None

            # check if the new position overlaps with a widget
            widget_cells = [widget_get_occupied_cells(self.widget_types[i], state.widget_centres[i],
                                                      state.widget_orients[i]) for i in range(self.n_widgets)]

            # check for reversing collision
            for i in range(self.n_widgets):
                if action == REVERSE and new_BEE_posit in widget_cells[i]:
                    # this action causes a reversing collision with a widget
                    return False, None, None

            # check if the new position moves a widget
            for i in range(self.n_widgets):
                if forward_BEE_posit in widget_cells[i]:
                    # this action pushes or pulls a widget
                    cost = ACTION_BASE_COST[action] + ACTION_PUSH_COST[action]

                    # get movement type - always use forward direction
                    widget_move_type = widget_get_movement_type(forward_direction, forward_BEE_posit,
                                                                state.widget_centres[i])

                    # apply movement to the widget
                    if widget_move_type == TRANSLATE:
                        # translate widget in movement direction
                        new_centre = get_adjacent_cell_coords(state.widget_centres[i], move_direction)
                        new_cells = widget_get_occupied_cells(self.widget_types[i], new_centre,
                                                              state.widget_orients[i])
                        # test collision for each cell of the widget
                        for (cr, cc) in new_cells:
                            # check collision with boundary
                            if (not 0 <= cr < self.n_rows) or (not 0 <= cc < self.n_cols):
                                # new widget position is invalid - collides with boundary
                                return False, None, None

                            # check collision with obstacles
                            if self.obstacle_map[cr][cc]:
                                # new widget position is invalid - collides with an obstacle
                                return False, None, None

                            # check collision with other widgets
                            for j in range(self.n_widgets):
                                if j == i:
                                    continue
                                if (cr, cc) in widget_cells[j]:
                                    # new widget position is invalid - collides with another widget
                                    return False, None, None

                        # new widget position is collision free
                        new_widget_centres = tuple(state.widget_centres[j] if j != i else new_centre
                                                   for j in range(self.n_widgets))
                        new_state = State(self, new_BEE_posit, state.BEE_orient, new_widget_centres,
                                          state.widget_orients, self.force_valid)
                        return True, cost, new_state

                    else:   # widget_move_type == SPIN_CW or widget_move_type == SPIN_CCW
                        # rotating a widget while reversing is not possible
                        if action == REVERSE:
                            return False, None, None

                        # rotate widget about its centre
                        if self.widget_types[i] == WIDGET3:
                            if widget_move_type == SPIN_CW:
                                new_orient = {VERTICAL: SLANT_RIGHT,
                                              SLANT_RIGHT: SLANT_LEFT,
                                              SLANT_LEFT: VERTICAL}[state.widget_orients[i]]
                            else:
                                new_orient = {VERTICAL: SLANT_LEFT,
                                              SLANT_LEFT: SLANT_RIGHT,
                                              SLANT_RIGHT: VERTICAL}[state.widget_orients[i]]
                        elif self.widget_types[i] == WIDGET4:
                            # CW and CCW are symmetric for this case
                            new_orient = {UP: DOWN, DOWN: UP}[state.widget_orients[i]]
                        else:   # self.widget_types[i] == WIDGET5
                            if widget_move_type == SPIN_CW:
                                new_orient = {HORIZONTAL: SLANT_LEFT,
                                              SLANT_LEFT: SLANT_RIGHT,
                                              SLANT_RIGHT: HORIZONTAL}[state.widget_orients[i]]
                            else:
                                new_orient = {HORIZONTAL: SLANT_RIGHT,
                                              SLANT_RIGHT: SLANT_LEFT,
                                              SLANT_LEFT: HORIZONTAL}[state.widget_orients[i]]
                        new_cells = widget_get_occupied_cells(self.widget_types[i], state.widget_centres[i], new_orient)

                        # check collision with the new BEE position
                        if new_BEE_posit in new_cells:
                            # new widget position is invalid - collides with the BEE
                            return False, None, None

                        # test collision for each cell of the widget
                        for (cr, cc) in new_cells:
                            # check collision with boundary
                            if (not 0 <= cr < self.n_rows) or (not 0 <= cc < self.n_cols):
                                # new widget position is invalid - collides with boundary
                                return False, None, None

                            # check collision with obstacles
                            if self.obstacle_map[cr][cc]:
                                # new widget position is invalid - collides with an obstacle
                                return False, None, None

                            # check collision with other widgets
                            for j in range(self.n_widgets):
                                if j == i:
                                    continue
                                if (cr, cc) in widget_cells[j]:
                                    # new widget position is invalid - collides with another widget
                                    return False, None, None

                        # new widget position is collision free
                        new_widget_orients = tuple(state.widget_orients[j] if j != i else new_orient
                                                   for j in range(self.n_widgets))
                        new_state = State(self, new_BEE_posit, state.BEE_orient, state.widget_centres,
                                          new_widget_orients, self.force_valid)
                        return True, cost, new_state

            # this action does not collide and does not push or pull any widgets
            cost = ACTION_BASE_COST[action]
            new_state = State(self, new_BEE_posit, state.BEE_orient, state.widget_centres,
                              state.widget_orients, self.force_valid)
            return True, cost, new_state

    def is_solved(self, state):
        """
        Check if the environment has been solved (i.e. all target cells are covered by a widget)
        :param state: current state
        :return: True if solved, False otherwise
        """
        widget_cells = [widget_get_occupied_cells(self.widget_types[i], state.widget_centres[i],
                                                  state.widget_orients[i]) for i in range(self.n_widgets)]
        # loop over each target
        env_solved = True
        for tgt in self.target_list:
            tgt_solved = False
            # loop over all widgets to find a match
            for i in range(self.n_widgets):
                if tgt in widget_cells[i]:
                    # match found
                    tgt_solved = True
                    break
            # if no match found, then env is not solved
            if not tgt_solved:
                env_solved = False
                break
        return env_solved

    def render(self, state):
        """
        Render the environment's current state to terminal
        :param state: current state
        """
        class Colours:
            prefix = "\033["
            reset = f"{prefix}0m"

            black = f"{prefix}30m"
            red = f"{prefix}31m"        # BEE colour
            green = f"{prefix}32m"      # target colour
            yellow = f"{prefix}33m"     # w colour
            blue = f"{prefix}34m"
            magenta = f"{prefix}35m"    # w colour
            cyan = f"{prefix}36m"       # w colour
            white = f"{prefix}37m"

            BEE_colour = red
            tgt_colour = green
            widget_colours = [yellow, magenta, cyan]

        buffer = [[' ' for _ in range((self.n_cols * RENDER_CELL_TOP_WIDTH) +
                                      ((self.n_cols + 1) * RENDER_CELL_SIDE_WIDTH))]
                  for __ in range((self.n_rows * RENDER_CELL_DEPTH) + RENDER_CELL_SIDE_WIDTH + 1)]

        # draw hex grid lines
        for i in range(self.n_rows):
            for j in range(0, self.n_cols, 2):
                # draw 2 complete hex cells each loop iteration
                #  __
                # /1 \__
                # \__/2 \
                #    \__/

                for k in range(RENDER_CELL_TOP_WIDTH):
                    # draw top half-row upper boundary '_'
                    y = i * RENDER_CELL_DEPTH
                    x = (j * RENDER_CELL_TOP_WIDTH) + ((j + 1) * RENDER_CELL_SIDE_WIDTH) + k
                    buffer[y][x] = '_'

                    # draw top half-row lower boundary '_'
                    y = (i + 1) * RENDER_CELL_DEPTH
                    x = (j * RENDER_CELL_TOP_WIDTH) + ((j + 1) * RENDER_CELL_SIDE_WIDTH) + k
                    buffer[y][x] = '_'

                    if j < self.n_cols - 1:
                        # draw bottom half-row upper boundary '_'
                        y = (i * RENDER_CELL_DEPTH) + RENDER_CELL_SIDE_WIDTH
                        x = ((j + 1) * RENDER_CELL_TOP_WIDTH) + ((j + 2) * RENDER_CELL_SIDE_WIDTH) + k
                        buffer[y][x] = '_'

                        # draw bottom half-row lower boundary '_'
                        y = ((i + 1) * RENDER_CELL_DEPTH) + RENDER_CELL_SIDE_WIDTH
                        x = ((j + 1) * RENDER_CELL_TOP_WIDTH) + ((j + 2) * RENDER_CELL_SIDE_WIDTH) + k
                        buffer[y][x] = '_'

                for k in range(RENDER_CELL_SIDE_WIDTH):
                    # draw top half-row up-left boundary '/'
                    y = (i * RENDER_CELL_DEPTH) + RENDER_CELL_SIDE_WIDTH - k
                    x = (j * RENDER_CELL_TOP_WIDTH) + (j * RENDER_CELL_SIDE_WIDTH) + k
                    buffer[y][x] = '/'

                    # draw top half-row up-right boundary '\'
                    y = (i * RENDER_CELL_DEPTH) + RENDER_CELL_SIDE_WIDTH - k
                    x = ((j + 1) * RENDER_CELL_TOP_WIDTH) + ((j + 1) * RENDER_CELL_SIDE_WIDTH) - k + 1
                    buffer[y][x] = '\\'

                    # draw top half-row down-left boundary '\'
                    y = ((i + 1) * RENDER_CELL_DEPTH) - k
                    x = (j * RENDER_CELL_TOP_WIDTH) + ((j + 1) * RENDER_CELL_SIDE_WIDTH) - k - 1
                    buffer[y][x] = '\\'

                    # draw top half-row down-right boundary '/'
                    y = ((i + 1) * RENDER_CELL_DEPTH) - k
                    x = ((j + 1) * RENDER_CELL_TOP_WIDTH) + ((j + 1) * RENDER_CELL_SIDE_WIDTH) + k
                    buffer[y][x] = '/'

                    if j < self.n_cols - 1:
                        # draw bottom half-row up-right boundary '\'
                        y = ((i + 1) * RENDER_CELL_DEPTH) - k
                        x = ((j + 2) * RENDER_CELL_TOP_WIDTH) + ((j + 3) * RENDER_CELL_SIDE_WIDTH) - k - 1
                        buffer[y][x] = '\\'

                        # draw bottom half-row down-left boundary '\'
                        y = ((i + 1) * RENDER_CELL_DEPTH) + RENDER_CELL_SIDE_WIDTH - k
                        x = ((j + 1) * RENDER_CELL_TOP_WIDTH) + ((j + 1) * RENDER_CELL_SIDE_WIDTH) - k + 1
                        buffer[y][x] = '\\'

                        # draw bottom half-row down-right boundary '/'
                        y = ((i + 1) * RENDER_CELL_DEPTH) + RENDER_CELL_SIDE_WIDTH - k
                        x = ((j + 2) * RENDER_CELL_TOP_WIDTH) + ((j + 2) * RENDER_CELL_SIDE_WIDTH) + k
                        buffer[y][x] = '/'

        # draw obstacles
        for i in range(self.n_rows):
            for j in range(self.n_cols):
                if self.obstacle_map[i][j]:
                    # draw an obstacle here
                    y = i * RENDER_CELL_DEPTH + (RENDER_CELL_SIDE_WIDTH if j % 2 == 1 else 0) + 1
                    x = (j * RENDER_CELL_TOP_WIDTH) + ((j + 1) * RENDER_CELL_SIDE_WIDTH)

                    # 1st obstacle row
                    for x_offset in range(RENDER_CELL_TOP_WIDTH):
                        buffer[y][x + x_offset] = 'X'
                    # 2nd obstacle row
                    for x_offset in range(-1, RENDER_CELL_TOP_WIDTH + 1):
                        buffer[y + 1][x + x_offset] = 'X'
                    # 3rd obstacle row
                    for x_offset in range(-1, RENDER_CELL_TOP_WIDTH + 1):
                        buffer[y + 2][x + x_offset] = 'X'
                    # 4th obstacle row (overwrites bottom border)
                    for x_offset in range(RENDER_CELL_TOP_WIDTH):
                        buffer[y + 3][x + x_offset] = 'X'

        # draw targets
        for tgt in self.target_list:
            ti, tj = tgt
            # draw in bottom half of cell, horizontally centered
            y = ti * RENDER_CELL_DEPTH + (RENDER_CELL_SIDE_WIDTH if tj % 2 == 1 else 0) + RENDER_CELL_SIDE_WIDTH + 1
            x = (tj * RENDER_CELL_TOP_WIDTH) + ((tj + 1) * RENDER_CELL_SIDE_WIDTH) + (RENDER_CELL_TOP_WIDTH // 2)
            # buffer[y][x] = 'T'
            buffer[y][x - 1] = 't'
            buffer[y][x] = 'g'
            buffer[y][x + 1] = 't'

        # draw widgets
        for w in range(self.n_widgets):
            # assign an alphabetical letter to represent each widget
            w_letter_lc = string.ascii_lowercase[w]
            w_letter_uc = string.ascii_uppercase[w]
            w_cells = widget_get_occupied_cells(self.widget_types[w], state.widget_centres[w], state.widget_orients[w])
            w_cells = widget_get_occupied_cells(self.widget_types[w], state.widget_centres[w], state.widget_orients[w])
            for wi, wj in w_cells:
                # draw in top half of cell, horizontally centered
                y = wi * RENDER_CELL_DEPTH + (RENDER_CELL_SIDE_WIDTH if wj % 2 == 1 else 0) + RENDER_CELL_SIDE_WIDTH
                x = (wj * RENDER_CELL_TOP_WIDTH) + ((wj + 1) * RENDER_CELL_SIDE_WIDTH) + (RENDER_CELL_TOP_WIDTH // 2)
                if (wi, wj) == state.widget_centres[w]:
                    # mark centre point with uppercase letter
                    buffer[y][x] = w_letter_uc
                else:
                    # all other points have lowercase letter
                    buffer[y][x] = w_letter_lc
                buffer[y][x - 1] = '('
                buffer[y][x + 1] = ')'

        # draw BEE
        ri, rj = state.BEE_posit
        # reference coord in top half of cell, horizontally centred (change draw position based on orientation)
        y = ri * RENDER_CELL_DEPTH + (RENDER_CELL_SIDE_WIDTH if rj % 2 == 1 else 0) + RENDER_CELL_SIDE_WIDTH
        x = (rj * RENDER_CELL_TOP_WIDTH) + ((rj + 1) * RENDER_CELL_SIDE_WIDTH) + (RENDER_CELL_TOP_WIDTH // 2)
        # handle each orientation separately
        if state.BEE_orient == BEE_UP:
            buffer[y + 1][x] = 'R'
            buffer[y - 1][x] = '*'
        elif state.BEE_orient == BEE_DOWN:
            buffer[y - 1][x] = 'R'
            buffer[y + 1][x] = '*'
        elif state.BEE_orient == BEE_UP_LEFT:
            buffer[y + 1][x + 1] = 'R'
            buffer[y][x - 2] = '*'
        elif state.BEE_orient == BEE_UP_RIGHT:
            buffer[y + 1][x - 1] = 'R'
            buffer[y][x + 2] = '*'
        elif state.BEE_orient == BEE_DOWN_LEFT:
            buffer[y][x + 1] = 'R'
            buffer[y + 1][x - 2] = '*'
        else:   # state.BEE_orient == BEE_DOWN_RIGHT
            buffer[y][x - 1] = 'R'
            buffer[y + 1][x + 2] = '*'

        # print render buffer to screen
        for row in buffer:
            line = ''
            for i, char in enumerate(row):
                if char in ['t', 'g']:
                    # target
                    line += Colours.tgt_colour
                if char == '(':
                    # widget start
                    next_char = row[i+1]
                    w_idx = string.ascii_lowercase.index(next_char.lower()) % self.n_widgets
                    line += Colours.widget_colours[w_idx]
                if char == 'R' or char == '*':
                    # part of BEE
                    line += Colours.BEE_colour

                line += char

                if char in ['t', 'g']:
                    # end of target
                    line += Colours.reset
                if char == ')':
                    # end of widget
                    line += Colours.reset
                if char == 'R' or char == '*':
                    # end of part of BEE
                    line += Colours.reset
            print(line)
        print('\n')


def get_adjacent_cell_coords(posit, direction):
    """
    Return the coordinates of the cell adjacent to the given position in the given direction.
    orientation.
    :param posit: position
    :param direction: direction (element of BEE_ORIENTATIONS)
    :return: (row, col) of adjacent cell
    """
    r, c = posit
    if direction == BEE_UP:
        return r - 1, c
    elif direction == BEE_DOWN:
        return r + 1, c
    elif direction == BEE_UP_LEFT:
        if c % 2 == 0:
            return r - 1, c - 1
        else:
            return r, c - 1
    elif direction == BEE_UP_RIGHT:
        if c % 2 == 0:
            return r - 1, c + 1
        else:
            return r, c + 1
    elif direction == BEE_DOWN_LEFT:
        if c % 2 == 0:
            return r, c - 1
        else:
            return r + 1, c - 1
    else:   # direction == BEE_DOWN_RIGHT
        if c % 2 == 0:
            return r, c + 1
        else:
            return r + 1, c + 1


def widget_get_occupied_cells(w_type, centre, orient):
    """
    Return a list of cell coordinates which are occupied by this widget (useful for checking if the widget is in
    collision and how the widget should move if pushed or pulled by the BEE).

    :param w_type: widget type
    :param centre: centre point of the widget
    :param orient: orientation of the widget
    :return: [(r, c) for each cell]
    """
    occupied = [centre]
    cr, cc = centre

    # cell in UP direction
    if ((w_type == WIDGET3 and orient == VERTICAL) or
            (w_type == WIDGET4 and orient == UP) or
            (w_type == WIDGET5 and (orient == SLANT_LEFT or orient == SLANT_RIGHT))):
        occupied.append((cr - 1, cc))

    # cell in DOWN direction
    if ((w_type == WIDGET3 and orient == VERTICAL) or
            (w_type == WIDGET4 and orient == DOWN) or
            (w_type == WIDGET5 and (orient == SLANT_LEFT or orient == SLANT_RIGHT))):
        occupied.append((cr + 1, cc))

    # cell in UP_LEFT direction
    if ((w_type == WIDGET3 and orient == SLANT_LEFT) or
            (w_type == WIDGET4 and orient == DOWN) or
            (w_type == WIDGET5 and (orient == SLANT_LEFT or orient == HORIZONTAL))):
        if cc % 2 == 0:
            # even column - row decreases
            occupied.append((cr - 1, cc - 1))
        else:
            # odd column - row stays the same
            occupied.append((cr, cc - 1))

    # cell in UP_RIGHT direction
    if ((w_type == WIDGET3 and orient == SLANT_RIGHT) or
            (w_type == WIDGET4 and orient == DOWN) or
            (w_type == WIDGET5 and (orient == SLANT_RIGHT or orient == HORIZONTAL))):
        if cc % 2 == 0:
            # even column - row decreases
            occupied.append((cr - 1, cc + 1))
        else:
            # odd column - row stays the same
            occupied.append((cr, cc + 1))

    # cell in DOWN_LEFT direction
    if ((w_type == WIDGET3 and orient == SLANT_RIGHT) or
            (w_type == WIDGET4 and orient == UP) or
            (w_type == WIDGET5 and (orient == SLANT_RIGHT or orient == HORIZONTAL))):
        if cc % 2 == 0:
            # even column - row stays the same
            occupied.append((cr, cc - 1))
        else:
            # odd column - row increases
            occupied.append((cr + 1, cc - 1))

    # cell in DOWN_RIGHT direction
    if ((w_type == WIDGET3 and orient == SLANT_LEFT) or
            (w_type == WIDGET4 and orient == UP) or
            (w_type == WIDGET5 and (orient == SLANT_LEFT or orient == HORIZONTAL))):
        if cc % 2 == 0:
            # even column - row stays the same
            occupied.append((cr, cc + 1))
        else:
            # odd column - row increases
            occupied.append((cr + 1, cc + 1))

    return occupied


def widget_get_movement_type(BEE_orient, forward_BEE_posit, centre):
    """
    Test if the given forward BEE position and widget type, position and rotation results in a translation. Assumes
    that new_BEE_posit overlaps with the given widget (implying that new_BEE_posit overlaps or is adjacent to
    the widget centre).

    If the BEE is reversing and this function returns a rotation movement type then the action is invalid.

    :param BEE_orient: BEE orientation
    :param forward_BEE_posit: (row, col) new BEE position
    :param centre: widget centre position
    :return: True if translation
    """
    # simple case --> new posit == centre is always translation
    if forward_BEE_posit == centre:
        return TRANSLATE

    # if direction between new_BEE_posit and centre is the same as BEE_orient, then move is a translation
    nr, nc = forward_BEE_posit
    cr, cc = centre

    # these directions do not depend on even/odd column
    if nr == cr - 1 and nc == cc:
        direction = BEE_DOWN
    elif nr == cr + 1 and nc == cc:
        direction = BEE_UP
    elif nr == cr - 1 and nc == cc - 1:
        direction = BEE_DOWN_RIGHT
    elif nr == cr - 1 and nc == cc + 1:
        direction = BEE_DOWN_LEFT
    elif nr == cr + 1 and nc == cc - 1:
        direction = BEE_UP_RIGHT
    elif nr == cr + 1 and nc == cc + 1:
        direction = BEE_UP_LEFT

    # these directions split based on even/odd
    elif nr == cr and nc == cc - 1:
        direction = BEE_UP_RIGHT if cc % 2 == 0 else BEE_DOWN_RIGHT
    else:  # nr == cr and nc == cc + 1
        direction = BEE_UP_LEFT if cc % 2 == 0 else BEE_DOWN_LEFT

    if direction == BEE_orient:
        return TRANSLATE
    elif (direction == {BEE_UP: BEE_DOWN_RIGHT,
                        BEE_UP_LEFT: BEE_UP_RIGHT,
                        BEE_DOWN_LEFT: BEE_UP,
                        BEE_DOWN: BEE_UP_LEFT,
                        BEE_DOWN_RIGHT: BEE_DOWN_LEFT,
                        BEE_UP_RIGHT: BEE_DOWN}[BEE_orient]):
        return SPIN_CW
    else:
        return SPIN_CCW












