import sys
from constants import *
from environment import *
from state import State
import heapq
import math
import functools

"""
solution.py

This file is a template you should use to implement your solution.

You should implement 

COMP3702 2024 Assignment 1 Support Code
"""


class Solver:

    def __init__(self, environment, loop_counter):
        self.environment = environment
        self.loop_counter = loop_counter
        #
        # TODO: Define any class instance variables you require here.
        # NOTE: avoid performing any computationally expensive heuristic preprocessing operations here - use the preprocess_heuristic method below for this purpose
        #

    # === Uniform Cost Search ==========================================================================================
    def solve_ucs(self):
        # old slower one for backup
        """
        Find a path which solves the environment using Uniform Cost Search (UCS).
        :return: path (list of actions, where each action is an element of BEE_ACTIONS)
        """
        # Data format: tuple (cost,history_actions,state)
        queue = [(0,[],self.environment.get_init_state())]
        visited = {}
        heapq.heapify(queue)
        while len(queue):
            cost, history_actions, state = heapq.heappop(queue)
            if cached_solved(self.environment,state.widget_centres,state.widget_orients):
                return history_actions
            # Check visited & cost check
            if visited.get(state):
                if visited[state] > cost:
                    visited[state]=cost
            else:
                self.loop_counter.inc()
                visited[state]=cost
                for next_state in state.get_successor():
                    heapq.heappush(queue,(cost + next_state[1],history_actions + [next_state[3]],next_state[2]))
                        
        pass

    # === A* Search ====================================================================================================

    def preprocess_heuristic(self):
        """
        Perform pre-processing (e.g. pre-computing repeatedly used values) necessary for your heuristic,
        """

        #
        #
        # TODO: (Optional) Implement code for any preprocessing required by your heuristic here (if your heuristic
        #  requires preprocessing).
        #
        # If you choose to implement code here, you should call this method from your solve_a_star method (e.g. once at
        # the beginning of your search).
        #
        #

        pass
    

    def compute_heuristic(self, state):
        """
        Compute a heuristic value h(n) for the given state.
        :param state: given state (GameState object)
        :return a real number h(n)
        """
        return cached_heuristic(self.environment,state.widget_centres,state.BEE_posit)

    def solve_a_star(self):
        """
        Find a path which solves the environment using A* search.
        :return: path (list of actions, where each action is an element of BEE_ACTIONS)
        """
        # Data format: tuple (cost+heuristic,history_actions,cost,state)
        queue = [(self.compute_heuristic(self.environment.get_init_state()),[],0,self.environment.get_init_state())]
        visited = {}
        heapq.heapify(queue)
        while True:
            totalcost,history_actions,cost, state = heapq.heappop(queue)
            if cached_solved(self.environment,state.widget_centres,state.widget_orients):
                return history_actions
            # Check visited & cost check
            if visited.get(state):
                if visited[state] > cost:
                    visited[state]=cost
            else:
                self.loop_counter.inc()
                visited[state]=cost
                for next_state in state.get_successor():
                    newcost=cost + next_state[1]
                    heapq.heappush(queue,(self.compute_heuristic(next_state[2])+newcost,history_actions + [next_state[3]],newcost,next_state[2]))
        pass

    #
    #
    # TODO: Add any additional methods here
    #
@functools.cache
def cached_heuristic(environment,widget_centres,BEE_posit):
    value = 0
    for widget in widget_centres:
        if widget in environment.target_list:
            continue
        min_dist = 99
        for target in environment.target_list:
            min_dist = min(min_dist,abs(widget[0]-target[0])+abs(widget[1]-target[1]))
        value += 1.5*min_dist
    for wd in widget_centres:
        value += math.dist(wd,BEE_posit)
    return value

@functools.cache
def cached_solved(environment,widget_centres,widget_orients):
    if widget_centres[0] not in environment.target_list:
        return False
    widget_cells = []
    for i in range(environment.n_widgets):
        widget_cells+=cached_widget_get_occupied_cells(environment.widget_types[i], widget_centres[i],
                                                widget_orients[i])
    for tgt in environment.target_list:
        if tgt not in widget_cells:
            return False
    return True

@functools.cache
def cached_widget_get_occupied_cells(w_type, centre, orient):
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