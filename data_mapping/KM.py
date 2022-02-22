import math
import numpy as np

INF = 1000000
global nx, ny, edges, lx, ly, vx, vy, matchx, matchy, delta


def dfs(u):
    global delta
    vx[u] = 1
    for j in range(1, ny + 1):
        if vy[j]:
            continue
        if lx[u] + ly[j] == edges[u][j]:
            vy[j] = 1
            if not matchy[j] or dfs(matchy[j]):
                matchy[j] = u
                matchx[u] = j
                vy[j] = 1
                return True
        else:
            delta = min(delta, lx[u] + ly[j] - edges[u][j])
    return False


def km_init(para_edges):
    global nx, ny, edges, lx, ly, vx, vy, matchx, matchy
    nx, ny = para_edges.shape
    edges = np.zeros((nx + 1, ny + 1), dtype=float)
    for i in range(nx):
        for j in range(ny):
            if (math.isnan(para_edges[i][j])):
                edges[i + 1][j + 1] = -INF
            else:
                edges[i + 1][j + 1] = para_edges[i][j]
    vx = np.zeros(nx + 1, dtype=int)
    vy = np.zeros(ny + 1, dtype=int)
    matchx = np.zeros(nx + 1, dtype=int)
    matchy = np.zeros(ny + 1, dtype=int)
    lx = np.zeros(nx + 1, dtype=float)
    lx.fill(-INF)
    for i in range(1, nx + 1):
        for j in range(1, ny + 1):
            lx[i] = max(lx[i], edges[i][j])
    ly = np.zeros(ny + 1, dtype=float)


def km_algo(para_edges):
    global delta
    km_init(para_edges)
    for i in range(1, nx + 1):
        while True:
            vx.fill(0)
            vy.fill(0)
            delta = INF
            if dfs(i):
                break
            for k in range(1, nx + 1):
                if vx[k]:
                    lx[k] -= delta
            for j in range(1, ny + 1):
                if vy[j]:
                    vy[j] += delta
    return matchx[1:]
