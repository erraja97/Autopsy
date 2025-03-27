import math

class AnnotationState:
    def __init__(self):
        # Each stroke is a dict with keys:
        # "type": "freehand", "line", "rectangle", "highlight", "arrow", "circle", "text", "callout"
        # "points": list of (x, y) in PDF coordinates.
        # For "callout", also store "anchor": (x, y) and optionally "text".
        # "color": hex color string, "width": line thickness, "opacity": 0.0-1.0.
        self.annotations = {}  # {page_num: [stroke, ...]}
        self.undo_stack = {}   # {page_num: [stroke, ...]}
        self.redo_stack = {}   # {page_num: [stroke, ...]}

    def reset(self):
        self.annotations.clear()
        self.undo_stack.clear()
        self.redo_stack.clear()

    def add_stroke(self, page, stroke):
        self.annotations.setdefault(page, []).append(stroke)
        self.undo_stack.setdefault(page, []).clear()
        self.redo_stack.setdefault(page, []).clear()

    def undo(self, page):
        redos = self.redo_stack.get(page, [])
        if redos:
            restored = redos.pop()
            self.annotations.setdefault(page, []).append(restored)
            return True
        strokes = self.annotations.get(page, [])
        if strokes:
            last = strokes.pop()
            self.undo_stack.setdefault(page, []).append(last)
            return True
        return False

    def redo(self, page):
        undos = self.undo_stack.get(page, [])
        if undos:
            last = undos.pop()
            self.annotations.setdefault(page, []).append(last)
            return True
        return False

    def erase_near(self, page, pos, distance_thresh, zoom):
        import math

        def point_line_distance(pt, p1, p2):
            x, y = pt
            x1, y1 = p1
            x2, y2 = p2
            dx = x2 - x1
            dy = y2 - y1
            seg_len_sq = dx * dx + dy * dy
            if seg_len_sq == 0:
                return math.hypot(x - x1, y - y1)
            t = ((x - x1) * dx + (y - y1) * dy) / seg_len_sq
            t = max(0, min(1, t))
            proj_x = x1 + t * dx
            proj_y = y1 + t * dy
            return math.hypot(x - proj_x, y - proj_y)

        strokes = self.annotations.get(page, [])
        if not strokes:
            return False

        for i, stroke in enumerate(strokes):
            t = stroke.get("type", "freehand")
            points = stroke.get("points", [])
            hit = False
            # For freehand, use the default threshold.
            if t == "freehand":
                for x, y in points:
                    if math.hypot(x - pos[0], y - pos[1]) <= (distance_thresh / zoom):
                        hit = True
                        break
            # For text annotations, use a larger threshold since there is only one point.
            elif t == "text":
                for x, y in points:
                    if math.hypot(x - pos[0], y - pos[1]) <= ((distance_thresh * 2) / zoom):
                        hit = True
                        break
            elif t in ["line", "arrow"]:
                if len(points) >= 2:
                    if point_line_distance(pos, points[0], points[-1]) <= (distance_thresh / zoom):
                        hit = True
            elif t in ["rectangle", "highlight", "circle"]:
                if len(points) >= 2:
                    x_min = min(points[0][0], points[-1][0])
                    x_max = max(points[0][0], points[-1][0])
                    y_min = min(points[0][1], points[-1][1])
                    y_max = max(points[0][1], points[-1][1])
                    margin = distance_thresh / zoom
                    if (x_min - margin <= pos[0] <= x_max + margin and 
                        y_min - margin <= pos[1] <= y_max + margin):
                        hit = True
            elif t == "callout":
                if len(points) >= 2:
                    x_min = min(points[0][0], points[-1][0])
                    x_max = max(points[0][0], points[-1][0])
                    y_min = min(points[0][1], points[-1][1])
                    y_max = max(points[0][1], points[-1][1])
                    margin = distance_thresh / zoom
                    in_box = (x_min - margin <= pos[0] <= x_max + margin and 
                            y_min - margin <= pos[1] <= y_max + margin)
                    anchor = stroke.get("anchor")
                    in_anchor = False
                    if anchor:
                        in_anchor = math.hypot(anchor[0] - pos[0], anchor[1] - pos[1]) <= ((distance_thresh * 2) / zoom)
                    if in_box or in_anchor:
                        hit = True

            if hit:
                removed = strokes.pop(i)
                self.redo_stack.setdefault(page, []).append(removed)
                self.undo_stack.setdefault(page, []).clear()
                return True
        return False

