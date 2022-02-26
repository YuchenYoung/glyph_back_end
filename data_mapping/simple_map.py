import numpy as np

def map_data(header, img_num, rel_matrix):
    header_mapped = np.zeros(len(header), dtype=np.int)
    svg_mapped = np.zeros(img_num, dtype=np.int)
    map_res = {}
    map_cnt = 0
    loop_cnt = 0
    while map_cnt < len(header) and loop_cnt < 50:
        loop_cnt += 1
        for j in range(len(header)):
            if header_mapped[j] > 0:
                continue
            max_pos = -1
            max_val = -1
            for i in range(img_num):
                if svg_mapped[i]:
                    continue
                if rel_matrix[i][j] > max_val:
                    max_val = rel_matrix[i][j]
                    max_pos = i
            # print(f"j {j} maxpos {max_pos} maxval {max_val}")
            max_available = True
            for k in range(len(header)):
                if not header_mapped[k] and rel_matrix[max_pos][k] >= max_val and k != j:
                    max_available = False
                    break
            # print("======")
            if max_available:
                map_res[header[j]] = max_pos
                header_mapped[j] = 1
                svg_mapped[max_pos] = 1
                map_cnt += 1
                # print(map_res)
                break
    print(map_res)
    return map_res
