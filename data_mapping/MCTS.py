# -- coding:utf-8 --
import random
import math
import numpy as np

global scores, rel_mat, steps, options, groups, types, levels, mapped_levels, mapped_eles, av_axis
# para_c = 1 / math.sqrt(2.0)
para_c = 4


class Node(object):
    def __init__(self):
        self.parent = None
        self.children = []
        self.value = 0
        self.visit_times = 0
        self.option = 0
        self.axis = 2 - av_axis
        self.fin_options = []

    def ucb(self):
        return self.value / self.visit_times + para_c * math.sqrt(math.log(self.parent.visit_times) / self.visit_times)

    def get_best_child_ucb(self):
        best_child = None
        max_val = -10000
        for it in self.children:
            cur_ucb = it.ucb()
            if cur_ucb >= max_val:
                max_val = cur_ucb
                best_child = it
        return best_child

    def get_best_child_value(self):
        best_child = None
        max_val = -10000
        for it in self.children:
            cur_val = it.value
            if cur_val >= max_val:
                max_val = cur_val
                best_child = it
        return best_child


class MCTSTree(object):
    def __init__(self):
        self.root = Node()
        self.max_round = 200000
        self.best_option = []
        self.max_reward = -1

    def get_one_option(self, fin_ops, chi_ops, axis):
        cur_level = len(fin_ops)
        used_ops = fin_ops + chi_ops
        av_ops = list(filter(lambda u: u not in used_ops and u not in mapped_eles, range(1, options)))
        if options not in chi_ops and options not in av_ops and cur_level > len(groups):
            av_ops.append(options)
        if cur_level >= len(groups) and 0 not in chi_ops and axis < 2:
            av_ops.append(0)
        if cur_level >= len(groups) and len(fin_ops) > len(groups):
            for i in range(len(groups), len(fin_ops)):
                if fin_ops.count(fin_ops[i]) <= 1 and fin_ops[i] not in av_ops and fin_ops[i] not in chi_ops and types[i] >= 0 and types[cur_level] >= 0 and types[i] != types[cur_level]:
                    av_ops.append(fin_ops[i])
        if len(av_ops) < 1:
            return -1
        return av_ops[random.randint(0, len(av_ops) - 1)]

    def judge_to_expansion(self, node):
        cur_level = len(node.fin_options)
        if cur_level >= len(levels):
            return -1
        if mapped_levels[cur_level] >= 0:
            if len(node.children) == 0:
                return mapped_levels[cur_level]
            return -1
        children_used = list(map(lambda u: u.option, node.children))
        return self.get_one_option(node.fin_options, children_used, node.axis)


    def selection(self):
        cur = self.root
        while True:
            new_op = self.judge_to_expansion(cur)
            if new_op >= 0:
                return cur, new_op
            if len(cur.fin_options) >= steps:
                return cur, -1
            cur = cur.get_best_child_ucb()

    def expansion(self, node, new_op):
        new_node = Node()
        new_node.parent = node
        new_node.option = new_op
        new_node.fin_options = node.fin_options + [new_op]
        if new_op == 0:
            new_node.axis = node.axis + 1
        else:
            new_node.axis = node.axis
        node.children.append(new_node)
        return new_node

    def cal_reward(self, op_list):
        value = 0
        match_cnt = 0
        axis_cnt = 0
        for i in range(len(op_list)):
            if op_list[i] < options:
                if op_list[i] == 0:
                    axis_cnt += 1
                rel = rel_mat[op_list[i]][levels[i]]
                if i < len(groups):
                    rel = 0
                    for t in range(len(groups[i])):
                        rel += rel_mat[op_list[i]][groups[i][t]]
                    rel /= len(groups[i])
                    rel *= 1.05
                match_cnt += 1
                value += scores[levels[i]] * rel
        if match_cnt > 2 and match_cnt - axis_cnt > 2:
            value /= match_cnt
        else:
            value = 0
        if value > self.max_reward:
            self.best_option = op_list
            self.max_reward = value
        return value

    def simulation(self, node):
        op_list = list(node.fin_options)
        axis = node.axis
        while len(op_list) < steps:
            new_op = mapped_levels[len(op_list)]
            if new_op < 0:
                new_op = self.get_one_option(op_list, [], axis)
            if new_op == 0:
                axis += 1
            op_list.append(new_op)
        return self.cal_reward(op_list)

    def back_propagation(self, node, value):
        cur = node
        while cur is not None:
            cur.visit_times += 1
            cur.value += value
            cur = cur.parent

    def single_search(self):
        leaf, op = self.selection()
        if len(leaf.fin_options) >= steps:
            new_node = leaf
        else:
            new_node = self.expansion(leaf, op)
        value = self.simulation(new_node)
        self.back_propagation(new_node, value)

    def get_options_by_value(self):
        op_list = []
        cur = self.root
        while len(cur.children) > 0:
            cur = cur.get_best_child_value()
            op_list.append(cur.option)
        value = self.cal_reward(op_list)
        return op_list, value

    def get_options_by_ucb(self):
        op_list = []
        cur = self.root
        while len(cur.children) > 0:
            cur = cur.get_best_child_ucb()
            op_list.append(cur.option)
        value = self.cal_reward(op_list)
        return op_list, value

    def search(self):
        for i in range(self.max_round):
            # print(i)
            self.single_search()
        self.get_options_by_ucb()
        self.get_options_by_value()
        return self.best_option, self.max_reward


def mcts_init(p_scores, p_rel_mat, p_groups, p_types, p_mapped):
    global scores, rel_mat, steps, options, groups, types, levels, mapped_levels, mapped_eles, av_axis
    av_axis = 0
    scores = p_scores
    rel_mat = p_rel_mat
    groups = p_groups
    levels = []
    types = []
    group_props = []
    level_map = []
    mapped_levels = []
    mapped_eles = []
    for i in range(len(groups)):
        levels.append(0)
        types.append(-1)
        mapped_levels.append(-1)
        group_props += groups[i]
    for i in range(len(scores)):
        if i not in group_props:
            level_map.append(len(levels))
            levels.append(i)
            types.append(p_types[i])
            mapped_levels.append(-1)
        else:
            level_map.append(-1)
    for it in p_mapped:
        mapped_eles.append(it["ele"])
        if it["is_group"]:
            mapped_levels[it["level"]] = it["ele"]
        else:
            mapped_levels[level_map[it["level"]]] = it["ele"]
    for it in rel_mat[0]:
        if it > 0.01:
            av_axis = 2
            break
    steps = len(levels)
    options = len(rel_mat)
    print(levels)


def mcts_search(p_scores, p_rel_mat, p_groups, p_types, p_mapped):
    mcts_init(p_scores, p_rel_mat, p_groups, p_types, p_mapped)
    mcts_tree = MCTSTree()
    return mcts_tree.search()
