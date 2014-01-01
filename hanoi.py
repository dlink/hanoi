#!/usr/bin/env python

'''Tower of Hanoi Puzzle Solver

   Developed based on Game Therory Lecture by Peter Norvig in
   Introduction to Artificial Intelligence given by Stamford
   University.
'''

import sys
from copy import deepcopy
from collections import defaultdict

SEARCH_TYPE = 'breath-first'
#SEARCH_TYPE = 'depth-first'
#SEARCH_TYPE = 'A*' # with a poor heuristic

MAX_DISKS = 4
NUM_POSTS = 3
DISPLAY_NUM_ROWS = 7

D1 = 1
D2 = 2 
D3 = 3
D4 = 4

class State(object):
    def __init__(self, posts):
        self.posts = posts
        self.paths = []

    def getPost(self, num):
        if num not in range(1, NUM_POSTS+1):
            raise Exception("State.get: bad num: %s" % num)
        return self.posts[num-1]

    def equals(self, state2):
        for i in range(0, 3):
            if self.posts[i].disks != state2.posts[i].disks:
                return False
        return True

    def __repr__(self):
        t = []
        for p in self.posts:
            t.append(str(p))
        #return "posts: %s; paths: %s" % (self.posts, self.paths)
        return "posts: %s; paths: %s" % ("-".join(t), self.paths)

    def display(self):
        '''Output state displayed like this:
                |               |               |       
               xxx              |               |       
              xxxxx             |               |       
             xxxxxxx            |               |       
            xxxxxxxxx           |               |       
          -------------   -------------   ------------- 
          '''
        rep = []
        for post in self.posts:
            rep.append(post.representation())
        print
        for y in range(0, DISPLAY_NUM_ROWS):
            for x in range(0, NUM_POSTS):
                print rep[x][y],
            print
        #print self.paths

class Post(object):
    num_posts = 0

    def __init__(self, disks=None):
        self.disks = []
        if disks:
            self.disks = disks
        Post.num_posts +=1
        self.num = Post.num_posts

    @property
    def hasDisks(self):
        return len(self.disks)

    @property
    def topDisk(self):
        if self.hasDisks:
            return self.disks[-1]
        else:
            return None

    def representation(self):
        '''Render post state like this:
                |
               xxx 
              xxxxx
             xxxxxxx
            xxxxxxxxx
          -------------
                1
        '''
        o = []
        o.append("       |       ")
        for r in range(0, MAX_DISKS-len(self.disks)):
            o.append("       |       ")
        for d in reversed(self.disks):
            o.append('%s%sx%s%s%s' % (' '*(7-d), 'x'*d, 'x'*d, d, ' '*(6-d)))
        o.append(" ------------- ")
        o.append("       %s       " % self.num)
        return o

    def __repr__(self):
        return "(%s)" % "-".join(["D%s" % x for x in self.disks]) 

class Action(object):
    def __init__(self, disk, src, dst):
        """Disk number, source post number and dest. post number"""
        self.disk = disk
        self.src = src
        self.dst = dst
        
    def getNumbers(self):
        return (self.disk, self.src, self.dst)
        
    def __repr__(self):
        #return "(D%s: P%s->P%s)" % (self.disk, self.src, self.dst)
        #return "(p%s:d%s, p%s)" % (self.src, self.disk, self.dst)
        return "P%s:D%s -> P%s" % (self.src, self.disk, self.dst)

class Game(object):
    '''Preside over the game'''

    def __init__(self):
        self.iterations = 0

    def isGoal(self, state):
        '''Return true if the puzzle is solved'''

        if state.posts[2].disks == [D4, D3, D2, D1]:
            return True
        return False

    def doAction(self, state, action):
        '''Given a state and an action, perform that action
           Return the new state
        '''
        newState = deepcopy(state)
        newState.paths.append(action)
        disk, src_num, dst_num = action.getNumbers()
        src = newState.getPost(src_num)
        dst = newState.getPost(dst_num)
        if src.topDisk != disk:
            raise Exception("Move: D%s not on post%s." % (disk, src.num))
        if dst.hasDisks and disk > dst.topDisk:
            raise Exception("Move: Can not put disk %s on post%s, too big." 
                            % (d, dst.num))
        dst.disks.append(src.disks.pop())
        return newState

    def getPossibleActions(self, state):
        '''Given a state
           Return a LIST of possible actions from that state
        '''
        actions = []
        for i, post in enumerate(state.posts):
            if i == 0:
                opost1 = state.posts[1]
                opost2 = state.posts[2]
            elif i == 1:
                opost1 = state.posts[0]
                opost2 = state.posts[2]
            else:
                opost1 = state.posts[0]
                opost2 = state.posts[1]
            if post.hasDisks:
                if not opost1.hasDisks or post.topDisk < opost1.topDisk:
                    actions.append(Action(post.topDisk, post.num, opost1.num))
                if not opost2.hasDisks or post.topDisk < opost2.topDisk:
                    actions.append(Action(post.topDisk, post.num, opost2.num))
        return actions

    def getFrontier(self, state):
        '''Given a state, perform all possible actions
           Return a LIST of all resulting stages
        '''
        frontier = []
        for action in self.getPossibleActions(state):
            newState = self.doAction(state, action)
            frontier.append(newState)
        return frontier
            
    def stateIn(self, state, state_list):
        '''Given a state, and a LIST of states
           Return True if state is in that list
        '''
        for s in state_list:
            if state.equals(s):
                return True
        return False

    def treeSearch(self, state):
        '''Implements a Tree Search Algorithm to solve the Game

           Starts with a Initial State.
           Maintain two LISTs:  frontier, and explored

           Iterates thru all possible states taken from frontier and
           added to explored.  Then determine new frontier.  Until
           solved or fails.
        '''
        frontier = self.getFrontier(state)
        explored = [state]
        goal_states = []
        done = 0

        while not done:
            if not frontier:
                return "Failed"
            #state = frontier.pop(0)
            state = self.remove_choice(frontier)
            explored.append(state)
            self.iterations += 1
            #print "ITERATION:", self.iterations
            #state.display()
            if self.isGoal(state):
                return state.paths
            for action in self.getPossibleActions(state):
                newState = self.doAction(state, action)
                if self.stateIn(newState, frontier):
                    continue
                if self.stateIn(newState, explored):
                    continue
                frontier.append(newState)
                
    def remove_choice(self, frontier):
        '''Return the next choice from frontier
           Using algorithm Based on SEARCH_TYPE
        '''
        if SEARCH_TYPE == 'breath-first':
            state = frontier.pop(0)
        elif SEARCH_TYPE == 'depth-first':
            state = frontier.pop()
        elif SEARCH_TYPE == 'A*':
            # get lowest total cost:
            states_by_cost = defaultdict(lambda:[])
            for s in frontier:
                total_cost = len(s.paths)
                states_by_cost[total_cost].append(s)
            min_total_cost = min(states_by_cost.keys())
            
            # Heuristic: lest amount of disks on post 1
            states_by_heuristic = defaultdict(lambda:[])
            for s in states_by_cost[min_total_cost]:
                h = len(s.posts[0].disks)
                states_by_heuristic[h].append(s)
            min_h = min(states_by_heuristic.keys())
            
            # choose a state with least cost and least h and remove from f
            state = states_by_heuristic[min_h].pop(0)
            for i, s in enumerate(frontier):
                if state.equals(s):
                    del frontier[i]
                    break
        else:
            print 'unrecognized SEARCH_TYPE: %s' % SEARCH_TYPE
        return state

    def play(self,state, paths):
        '''Play the game, and solve the Puzzle'''

        print "Initial State:"
        state.display()
        i = 0
        for p in paths:
            yn = sys.stdin.readline()
            state = self.doAction(state, p)
            i += 1
            print "Move", i
            state.display()

# Main:

initState = State([Post([D4, D3, D2, D1]), Post(), Post()])
game = Game()
result = game.treeSearch(initState)

# Somme comments:
print "Search type:", SEARCH_TYPE
print "Iterations Checked:", game.iterations
print "Solution Path:", result
print "Num of moves needed:", len(result)
print "Hit Enter to see it played out."
yn = sys.stdin.readline()

# Play solution
game.play(initState, result)
