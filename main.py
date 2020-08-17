import itertools
import math
import random
from bisect import bisect_left

pc = 0.80
pm = 0.001


class Data:

    def __init__(self, value):
        self.value = value

    def set_value(self, v):
        self.value = v


a0, a1, a2, a3, d0, d1 = [Data(True) for _ in range(6)]


def a0_var():
    return a0.value


def a1_var():
    return a1.value


def a2_var():
    return a2.value


def a3_var():
    return a3.value


def d0_var():
    return d0.value


def d1_var():
    return d1.value


def multiplex(a0, a1, a2, a3, d0, d1):
    if d0 and d1:
        return a3

    if not d0 and not d1:
        return a0

    if not d1 and d0:
        return a1

    if d1 and not d0:
        return a2


def and_function(a: bool, b: bool):
    return a and b


def or_function(a: bool, b: bool):
    return a or b


def if_function(a: bool, b: bool, c: bool):
    return a if b else c


def not_function(a: bool):
    return not a


signatures = {
    a0_var: 0,
    a1_var: 0,
    a2_var: 0,
    a3_var: 0,
    d0_var: 0,
    d1_var: 0,
    and_function: 2,
    or_function: 2,
    if_function: 3,
    not_function: 1,
}

first_nodes = [if_function,and_function,or_function, not_function]
nodes = [a0_var, a1_var, a2_var, a3_var, d0_var, d1_var, if_function,and_function,or_function, not_function]


class Node:

    def __init__(self, current):
        self.current = current
        self.children = []

        self.parent = None
        self.n_parents = 0
        self.fitness = 0

    def generate_children(self):
        n_parameters = signatures[self.current]
        for _ in range(n_parameters):
            n = Node(random.choice(nodes))
            n.parent = self
            n.n_parents = self.n_parents + 1
            n.generate_children()
            self.children.append(n)

    def evaluate(self):
        n_parameters = signatures[self.current]
        if n_parameters == 0:
            return self.current()
        if n_parameters == 1:
            return self.current(self.children[0].evaluate())
        if n_parameters == 2:
            return self.current(self.children[0].evaluate(), self.children[1].evaluate())
        if n_parameters == 3:
            return self.current(self.children[0].evaluate(), self.children[1].evaluate(), self.children[2].evaluate())

    def print(self, n_tab=0):
        print('\t' * n_tab, self.current.__name__)
        for c in self.children:
            c.print(n_tab + 1)

    def list(self):
        nodes_list = []
        nodes_to_cross = [self]

        while len(nodes_to_cross) > 0:
            n = nodes_to_cross.pop()
            nodes_list.append(n)
            nodes_to_cross.extend(n.children)

        return nodes_list

    def depth(self):
        nodes_list = []
        nodes_to_cross = [(self, 1)]

        while len(nodes_to_cross) > 0:
            n, i = nodes_to_cross.pop()
            nodes_list.append((n, i))
            for c in n.children:
                nodes_to_cross.append((c, i + 1))

        return max(i for n, i in nodes_list)

    @staticmethod
    def copy(node):
        n = Node(node.current)
        n.children = []
        for c in node.children:
            n.children.append(Node.copy(c))
            n.children[-1].parent = n
        return n


def random_tree():
    while True:
        n = Node(random.choice(first_nodes))
        n.generate_children()
        n.print()
        print(n.depth())
        if 6> n.depth(): return n


def evaluate_pop(pop):
    for tree in pop:
        for r in itertools.product([True, False], repeat=6):
            a0.set_value(r[0])
            a1.set_value(r[1])
            a2.set_value(r[2])
            a3.set_value(r[3])
            d0.set_value(r[4])
            d1.set_value(r[5])
            a = tree.evaluate()
            if a == multiplex(a0.value, a1.value, a2.value, a3.value, d0.value, d1.value):
                tree.fitness += 1


def cross_over(t1, t2):
    t1l = t1.list()
    #t1l = [t for t in t1l if t.parent != None]
    t2l = t2.list()
    #t2l = [t for t in t2l if t.parent != None]

    if t1l == [] or t2l == []:
        return t1, t2

    c1 = random.choice(t1l)
    c2 = random.choice(t2l)

    pc1 = c1.parent
    if pc1:
        index1 = pc1.children.index(c1)

    pc2 = c2.parent
    if pc2 :
        index2 = pc2.children.index(c2)

    c1.parent, c2.parent = pc2, pc1
    if pc1 :
        pc1.children[index1] = c2
    if pc2 :
        pc2.children[index2] = c1

    if t1.depth() > 6 or t2.depth() >6:
        return None

    return t1, t2


def evolve(pop):
    next_pop = []
    max_fit = max(t.fitness for t in pop)
    for t in pop:
        t.fitness = ((t.fitness - 32)/ 32.)/t.depth()
        if t.fitness < 0 :  t.fitness = 0
    total_fitness = sum(t.fitness for t in pop)
    print("mean fitness ", total_fitness / len(pop))
    print("max fitness ", max_fit)
    print("mean node per tree ", str(sum(len(t.list())for t in pop)/len(pop)))
    print("mean depth per tree ", str(sum(t.depth() for t in pop)/len(pop)))

    if max_fit  >63.5:
        for t in pop:
            if t.fitness*t.depth()*32. > 31.5:
                t.print()
                exit()
    probas = [0.]
    for t in pop:
        probas.append(probas[-1] + (t.fitness / total_fitness))
    probas[-1] = 1.001

    while len(next_pop) < len(pop):
        p1, p2 = random.random(), random.random()
        t1, t2 = Node.copy(pop[bisect_left(probas, p1) - 1]), Node.copy(pop[bisect_left(probas, p2) - 1])

        if random.random() < pc:
            r = cross_over(t1, t2)
            if r is not None :
                t1, t2 = r
            else :
                t1, t2 = Node.copy(pop[bisect_left(probas, p1) - 1]), Node.copy(pop[bisect_left(probas, p2) - 1])


        if t1.depth() > 8 or t2.depth() > 8:
            print(t1.depth())
        next_pop.append(t1)
        next_pop.append(t2)


    return next_pop


pop = [random_tree() for _ in range(4000)]
gen = 0
while True:
    print("GEN ", gen)
    gen += 1

    evaluate_pop(pop)
    pop = evolve(pop)
