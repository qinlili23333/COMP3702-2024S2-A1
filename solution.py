import sys
from constants import *
from environment import *
from state import State
from heapq import heapify, heappush, heappop
from math import dist
from functools import cache

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
        queue = [(0,[],self.environment.get_init_state())]
        visited = {}
        heapify(queue)
        while True:
            cost, history_actions, state = heappop(queue)
            if cached_solved(self.environment,state.widget_centres,state.widget_orients):
                return history_actions
            if visited.get(state):
                if visited[state] > cost:
                    visited[state]=cost
            else:
                self.loop_counter.inc()
                visited[state]=cost
                for next_state in state.get_successor():
                    heappush(queue,(cost + next_state[0][1],history_actions + [next_state[1]],next_state[0][2]))


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
        return cached_heuristic(self.environment,state.widget_centres,state.BEE_posit)

    def solve_a_star(self):
        queue = [(self.compute_heuristic(self.environment.get_init_state()),[],0,self.environment.get_init_state())]
        visited = {}
        heapify(queue)
        while True:
            totalcost,history_actions,cost, state = heappop(queue)
            if cached_solved(self.environment,state.widget_centres,state.widget_orients):
                return history_actions
            if visited.get(state):
                if visited[state] > cost:
                    visited[state]=cost
            else:
                self.loop_counter.inc()
                visited[state]=cost
                for next_state in state.get_successor():
                    newcost=cost + next_state[0][1]
                    heappush(queue,(self.compute_heuristic(next_state[0][2])+newcost,history_actions + [next_state[1]],newcost,next_state[0][2]))


@cache
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
        value += dist(wd,BEE_posit)
    return value

@cache
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

@cache
def cached_widget_get_occupied_cells(w_type, centre, orient):
    occupied = [centre]
    cr, cc = centre
    if ((w_type == WIDGET3 and orient == VERTICAL) or
            (w_type == WIDGET4 and orient == UP) or
            (w_type == WIDGET5 and (orient == SLANT_LEFT or orient == SLANT_RIGHT))):
        occupied.append((cr - 1, cc))
    if ((w_type == WIDGET3 and orient == VERTICAL) or
            (w_type == WIDGET4 and orient == DOWN) or
            (w_type == WIDGET5 and (orient == SLANT_LEFT or orient == SLANT_RIGHT))):
        occupied.append((cr + 1, cc))
    if ((w_type == WIDGET3 and orient == SLANT_LEFT) or
            (w_type == WIDGET4 and orient == DOWN) or
            (w_type == WIDGET5 and (orient == SLANT_LEFT or orient == HORIZONTAL))):
        if cc % 2 == 0:
            occupied.append((cr - 1, cc - 1))
        else:
            occupied.append((cr, cc - 1))

    if ((w_type == WIDGET3 and orient == SLANT_RIGHT) or
            (w_type == WIDGET4 and orient == DOWN) or
            (w_type == WIDGET5 and (orient == SLANT_RIGHT or orient == HORIZONTAL))):
        if cc % 2 == 0:
            occupied.append((cr - 1, cc + 1))
        else:
            occupied.append((cr, cc + 1))

    if ((w_type == WIDGET3 and orient == SLANT_RIGHT) or
            (w_type == WIDGET4 and orient == UP) or
            (w_type == WIDGET5 and (orient == SLANT_RIGHT or orient == HORIZONTAL))):
        if cc % 2 == 0:
            occupied.append((cr, cc - 1))
        else:
            occupied.append((cr + 1, cc - 1))

    if ((w_type == WIDGET3 and orient == SLANT_LEFT) or
            (w_type == WIDGET4 and orient == UP) or
            (w_type == WIDGET5 and (orient == SLANT_LEFT or orient == HORIZONTAL))):
        if cc % 2 == 0:
            occupied.append((cr, cc + 1))
        else:
            occupied.append((cr + 1, cc + 1))

    return occupied