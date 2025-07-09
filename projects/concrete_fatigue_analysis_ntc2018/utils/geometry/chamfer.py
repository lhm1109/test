import numpy as np

def apply_chamfer(coordinates, chamfer_sizes, strict=True):
    """
    coords: dict with 'y' and 'z' keys forming a closed polygon (first == last point).
    chamfer_sizes: list of [prev_len, next_len] chamfer values for each unique vertex.
    strict: if True, raise error when chamfer length exceeds segment length.
            if False, automatically clamp to max possible.
    Returns: dict with chamfered 'y' and 'z' lists (closed loop).
    """
    y_list = coordinates["y"]
    z_list = coordinates["z"]
    n = len(y_list)

    # 1. 폐곡선 검사
    if n < 4 or (y_list[0], z_list[0]) != (y_list[-1], z_list[-1]):
        return {"error": "Input coordinates must form a closed polygon (first == last point)."}

    n_vertices = n - 1  # exclude closure point

    if len(chamfer_sizes) != n_vertices:
        return {"error": "Length of chamfer_sizes must match number of unique vertices."}

    new_y, new_z = [], []

    def safe_chamfer_length(p1, p2, desired_length):
        seg_len = np.linalg.norm(p2 - p1)
        if desired_length > seg_len:
            if strict:
                raise ValueError(
                    f"Chamfer length {desired_length:.4f} exceeds segment length {seg_len:.4f}"
                )
            else:
                return seg_len
        return desired_length

    for i in range(n_vertices):
        p_prev = np.array([y_list[(i - 1) % n_vertices], z_list[(i - 1) % n_vertices]])
        p_curr = np.array([y_list[i], z_list[i]])
        p_next = np.array([y_list[(i + 1) % n_vertices], z_list[(i + 1) % n_vertices]])

        cp, cn = chamfer_sizes[i]

        # 2. 길이 확인 및 제한
        cp = safe_chamfer_length(p_curr, p_prev, cp)
        cn = safe_chamfer_length(p_curr, p_next, cn)

        # 3. 방향 벡터 계산 및 chamfer 점 생성
        v_prev = p_prev - p_curr
        v_prev = v_prev / np.linalg.norm(v_prev) * cp if cp > 0 else np.array([0.0, 0.0])

        v_next = p_next - p_curr
        v_next = v_next / np.linalg.norm(v_next) * cn if cn > 0 else np.array([0.0, 0.0])

        pt1 = p_curr + v_prev
        pt2 = p_curr + v_next

        if cp > 0:
            new_y.append(pt1[0])
            new_z.append(pt1[1])
        else:
            new_y.append(p_curr[0])
            new_z.append(p_curr[1])

        if cn > 0:
            new_y.append(pt2[0])
            new_z.append(pt2[1])

    # 4. 폐곡선 유지
    new_y.append(new_y[0])
    new_z.append(new_z[0])

    return {"y": new_y, "z": new_z}