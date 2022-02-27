# -- coding:utf-8 --
import random
import math
import numpy as np

global scores, rel_mat, steps, options
para_c = 2

class Node(object):
    def __init__(self):
        self.parent = None
        self.children = []
        self.value = 0
        self.visit_times = 0
        self.option = 0
        self.fin_options = []

    def ucb(self):
        return self.value / self.visit_times + para_c * math.sqrt(math.log(self.parent.visit_times) / self.visit_times)

    def get_best_child(self):
        best_child = None
        max_val = -10000
        for it in self.children:
            cur_ucb = it.ucb()
            if cur_ucb > max_val:
                max_val = cur_ucb
                best_child = it
        return best_child


class MCTSTree(object):
    def __init__(self):
        self.root = Node()
        self.max_round = 500

    def selection(self):
        cur = self.root
        while True:
            if len(cur.children) == 0 or len(cur.children) + len(cur.fin_options) < options:
                break
            cur = cur.get_best_child()
        return cur

    def expansion(self, node):
        used_ops = node.fin_options + list(map(lambda u: u.option, node.children))
        av_ops = list(filter(lambda u: u not in used_ops, range(options)))
        new_op = av_ops[random.randint(0, len(av_ops) - 1)]
        new_node = Node()
        new_node.parent = node
        new_node.option = new_op
        new_node.fin_options = node.fin_options + [new_op]
        node.children.append(new_node)
        return new_node

    def simulation(self, node):
        op_list = list(node.fin_options)
        while len(op_list) <= steps:
            av_ops = list(filter(lambda u: u not in op_list, range(options)))
            new_op = av_ops[random.randint(0, len(av_ops) - 1)]
            op_list.append(new_op)
        value = 0
        for i in range(steps):
            value += scores[i] * rel_mat[op_list[i]][i]
        return value

    def back_propagation(self, node, value):
        cur = node
        while cur is not None:
            cur.visit_times += 1
            cur.value += value
            cur = cur.parent

    def single_search(self):
        leaf = self.selection()
        if len(leaf.fin_options) >= steps:
            return
        new_node = self.expansion(leaf)
        value = self.simulation(new_node)
        self.back_propagation(new_node, value)

    def get_options(self):
        op_list = []
        cur = self.root
        while len(cur.children) > 0:
            cur = cur.get_best_child()
            op_list.append(cur.option)
        value = 0
        for i in range(steps):
            value += scores[i] * rel_mat[op_list[i]][i]
        return op_list, value

    def search(self):
        for i in range(self.max_round):
            self.single_search()
        return self.get_options()


def mcts_init(p_scores, p_rel_mat):
    global scores, rel_mat, steps, options
    scores = p_scores
    rel_mat = p_rel_mat
    steps = len(scores)
    options = len(rel_mat)


def mcts_search(p_scores, p_rel_mat):
    mcts_init(p_scores, p_rel_mat)
    mcts_tree = MCTSTree()
    return mcts_tree.search()
