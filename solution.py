import sys
from constants import *
from environment import *
from state import State
from heapq import *

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
        heapify(queue)
        while len(queue):
            # print(queue[0][2]
            cost, history_actions, state = heappop(queue)
            if self.environment.is_solved(state):
                print(history_actions)
                return history_actions
            # Check visited & cost check
            if visited.get(state):
                if visited[state] > cost:
                    visited[state]=cost
            else:
                self.loop_counter.inc()
                visited[state]=cost
                for next_state in state.get_successor():
                    heappush(queue,(cost + next_state[1],history_actions + [next_state[3]],next_state[2]))
                        
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
        widget_cells = [widget_get_occupied_cells(self.environment.widget_types[i], state.widget_centres[i],state.widget_orients[i]) for i in range(self.environment.n_widgets)]
        value = 0
        max_distance = 0
        for tgt in self.environment.target_list:
            # loop over all widgets to find a match
            for i in range(self.environment.n_widgets):
                if tgt not in widget_cells[i]:
                    # match found
                    value += 1.5
        for wd in state.widget_centres:
            x=abs(wd[0]-state.BEE_posit[0])
            y=abs(wd[1]-state.BEE_posit[1])
            distance = x+y-1
            if distance > max_distance:
                max_distance = distance
        value += max_distance
        return value

    def solve_a_star(self):
        """
        Find a path which solves the environment using A* search.
        :return: path (list of actions, where each action is an element of BEE_ACTIONS)
        """
        # Data format: tuple (cost+heuristic,cost,history_actions,state)
        queue = [(self.compute_heuristic(self.environment.get_init_state()),0,[],self.environment.get_init_state())]
        visited = {}
        heapify(queue)
        while len(queue):
            # print(queue[0][2]
            totalcost,cost, history_actions, state = heappop(queue)
            if self.environment.is_solved(state):
                print(history_actions)
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
                    heappush(queue,(self.compute_heuristic(next_state[2])+newcost,newcost,history_actions + [next_state[3]],next_state[2]))
        pass

    #
    #
    # TODO: Add any additional methods here
    #
    #
