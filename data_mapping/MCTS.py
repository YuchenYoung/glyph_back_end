# -- coding:utf-8 --
import random
import math
import numpy as np

global scores, rel_mat, steps, options, groups, levels, mapped_levels, mapped_eles, av_axis
para_c = 1 / math.sqrt(2.0)
# para_c = 6


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
        self.max_round = 50000

    def judge_to_expansion(self, node, cur_level):
        if cur_level < len(mapped_levels) and mapped_levels[cur_level] >= 0:
            return len(node.children) == 0
        children_used = list(map(lambda u: u.option, node.children))
        used_ops = node.fin_options + children_used
        av_ops = list(filter(lambda u: u not in used_ops and u not in mapped_eles, range(1, options + 1)))
        if options not in children_used and options not in av_ops:
            av_ops.append(options)
        if cur_level >= len(groups) and 0 not in children_used and node.axis < 2:
            av_ops.append(0)
        return len(av_ops) > 0

    def selection(self):
        cur = self.root
        while True:
            if cur is None:
                return None
            cur_level = len(cur.fin_options)
            # cur_options = options
            # if cur_level < len(groups):
            #     cur_options -= 1
            # if len(cur.children) == 0 or (
            #         mapped_levels[cur_level] < 0 and len(cur.children) + len(cur.fin_options) < cur_options):
            #     break
            if self.judge_to_expansion(cur, cur_level):
                break
            cur = cur.get_best_child_ucb()
        return cur

    def expansion(self, node):
        cur_level = len(node.fin_options)
        new_op = mapped_levels[cur_level]
        if new_op < 0:
            children_used = list(map(lambda u: u.option, node.children))
            used_ops = node.fin_options + children_used
            av_ops = list(filter(lambda u: u not in used_ops and u not in mapped_eles, range(1, options + 1)))
            if options not in children_used and options not in av_ops:
                av_ops.append(options)
            if cur_level >= len(groups) and 0 not in children_used and node.axis < 2:
                av_ops.append(0)
            new_op = av_ops[random.randint(0, len(av_ops) - 1)]
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

    def simulation(self, node):
        op_list = list(node.fin_options)
        axis = node.axis
        while len(op_list) < steps:
            cur_level = len(op_list)
            new_op = mapped_levels[cur_level]
            if new_op < 0:
                av_ops = list(filter(lambda u: u not in op_list and u not in mapped_eles, range(1, options)))
                av_ops.append(options)
                if cur_level >= len(groups) and axis < 2:
                    av_ops.append(0)
                new_op = av_ops[random.randint(0, len(av_ops) - 1)]
            if new_op == 0:
                axis += 1
            op_list.append(new_op)
        value = 0
        match_cnt = 0
        for i in range(steps):
            if op_list[i] < options:
                rel = rel_mat[op_list[i]][levels[i]]
                if i < len(groups):
                    rel = 0
                    for t in range(len(groups[i])):
                        rel += rel_mat[op_list[i]][groups[i][t]]
                    rel /= len(groups[i])
                match_cnt += 1
                value += scores[i] * rel
        if match_cnt > 2:
            value /= match_cnt
        else:
            value = 0
        return value

    def back_propagation(self, node, value):
        cur = node
        while cur is not None:
            cur.visit_times += 1
            cur.value += value
            cur = cur.parent

    def single_search(self):
        leaf = self.selection()
        if leaf is None or len(leaf.fin_options) >= steps:
            return
        new_node = self.expansion(leaf)
        value = self.simulation(new_node)
        self.back_propagation(new_node, value)

    def get_options(self):
        op_list = []
        cur = self.root
        while len(cur.children) > 0:
            cur = cur.get_best_child_value()
            op_list.append(cur.option)
        value = 0
        match_cnt = 0
        for i in range(len(op_list)):
            if op_list[i] < options:
                match_cnt += 1
                if i < len(groups):
                    group_val = 0
                    for j in range(len(groups[i])):
                        group_val += scores[groups[i][j]] * rel_mat[op_list[i]][groups[i][j]]
                    group_val /= len(groups[i])
                    value += group_val
                else:
                    value += scores[i] * rel_mat[op_list[i]][i]
        if match_cnt > 2:
            value /= match_cnt
        else:
            value = 0
        return op_list, value

    def search(self):
        for i in range(self.max_round):
            # print(i)
            self.single_search()
        return self.get_options()


def mcts_init(p_scores, p_rel_mat, p_groups, p_mapped):
    global scores, rel_mat, steps, options, groups, levels, mapped_levels, mapped_eles, av_axis
    av_axis = 0
    scores = p_scores
    rel_mat = p_rel_mat
    groups = p_groups
    levels = []
    group_props = []
    level_map = []
    mapped_levels = []
    mapped_eles = []
    for i in range(len(groups)):
        levels.append(0)
        mapped_levels.append(-1)
        group_props += groups[i]
    for i in range(len(scores)):
        if i not in group_props:
            level_map.append(len(levels))
            levels.append(i)
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


def mcts_search(p_scores, p_rel_mat, p_groups, p_mapped):
    mcts_init(p_scores, p_rel_mat, p_groups, p_mapped)
    mcts_tree = MCTSTree()
    return mcts_tree.search()
