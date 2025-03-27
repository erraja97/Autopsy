from PySide6.QtGui import QPainter, QPen, QColor, QPainterPath
from PySide6.QtCore import Qt, QPointF
from PySide6.QtWidgets import QInputDialog
import math

def handle_mouse_press(window, event):
    if not window.pdf_document or event.button() != Qt.LeftButton:
        return

    pos = window.to_pdf_coords(event.position().toPoint())
    atype = window.annotation_type

    # -------------------------------------------------------------
    # 1) For callout, we do a two-click approach:
    #    - If user hasn’t set anchor yet, store it in "window.callout_temp"
    #    - Next press sets up the stroke using that anchor
    # -------------------------------------------------------------
    if atype == "callout":
        if not hasattr(window, "callout_temp") or window.callout_temp is None:
            # First click sets the arrow anchor
            window.callout_temp = pos
            return
        else:
            # Second click: start drawing the callout box from this new click
            window.drawing = True
            window.last_point = pos
            window.current_stroke = {
                "type": "callout",
                "points": [pos],  # we'll store 2 points => (start, end) for the box
                "anchor": window.callout_temp,  # store the anchor from first click
                "color": window.pen_color.name(),
                "width": window.pen_width,
                "opacity": window.pen_opacity,
                # We'll prompt for text on mouse_release
            }

    elif atype in ["freehand", "line", "rectangle", "highlight", "arrow", "circle"]:
        window.drawing = True
        window.last_point = pos
        window.current_stroke = {
            "type": atype,
            "points": [pos],
            "color": window.pen_color.name(),
            "width": window.pen_width,
            "opacity": window.pen_opacity
        }

    elif atype == "text":
        text, ok = QInputDialog.getText(window, "Enter Text", "Text:")
        if ok and text:
            stroke = {
                "type": "text",
                "points": [pos],
                "color": window.pen_color.name(),
                "width": window.pen_width,
                "opacity": window.pen_opacity,
                "text": text
            }
            window.state.add_stroke(window.current_page_num, stroke)
            window.display_page()

    elif atype == "eraser":
        window.state.erase_near(window.current_page_num, pos, 10, window.zoom_factor)
        window.display_page()

def handle_mouse_move(window, event):
    if not window.drawing or not window.last_point:
        return

    new_point = window.to_pdf_coords(event.position().toPoint())
    atype = window.annotation_type

    # For freehand, accumulate points; for others, keep two points (start->end).
    if atype == "freehand":
        window.current_stroke["points"].append(new_point)
    else:
        if len(window.current_stroke["points"]) == 1:
            window.current_stroke["points"].append(new_point)
        else:
            window.current_stroke["points"][-1] = new_point

    # Redraw base, then ephemeral shape
    window.display_page()
    ephemeral_pixmap = window.pdf_view.pixmap().copy()

    painter = QPainter(ephemeral_pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    color = QColor(window.pen_color)
    color.setAlphaF(window.pen_opacity)
    pen = QPen(color, window.pen_width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
    painter.setPen(pen)

    if atype == "freehand":
        pts = window.current_stroke["points"]
        if pts:
            path = QPainterPath()
            path.moveTo(QPointF(pts[0][0]*window.zoom_factor, pts[0][1]*window.zoom_factor))
            for x, y in pts[1:]:
                path.lineTo(QPointF(x*window.zoom_factor, y*window.zoom_factor))
            painter.drawPath(path)

    elif atype == "line":
        start = window.current_stroke["points"][0]
        end = window.current_stroke["points"][-1]
        painter.drawLine(
            QPointF(start[0]*window.zoom_factor, start[1]*window.zoom_factor),
            QPointF(end[0]*window.zoom_factor, end[1]*window.zoom_factor)
        )

    elif atype == "rectangle" or atype == "highlight":
        start = window.current_stroke["points"][0]
        end = window.current_stroke["points"][-1]
        left = min(start[0], end[0]) * window.zoom_factor
        top = min(start[1], end[1]) * window.zoom_factor
        width = abs(end[0]-start[0]) * window.zoom_factor
        height = abs(end[1]-start[1]) * window.zoom_factor
        if atype == "highlight":
            # fill rect with alpha color
            fill_color = QColor(window.pen_color)
            fill_color.setAlphaF(window.pen_opacity)
            painter.setBrush(fill_color)
            painter.setPen(Qt.NoPen)
            painter.drawRect(left, top, width, height)
            painter.setBrush(Qt.NoBrush)
            painter.setPen(pen)
            painter.drawRect(left, top, width, height)
        else:
            painter.drawRect(left, top, width, height)

    elif atype == "arrow":
        start = window.current_stroke["points"][0]
        end = window.current_stroke["points"][-1]
        painter.drawLine(
            QPointF(start[0]*window.zoom_factor, start[1]*window.zoom_factor),
            QPointF(end[0]*window.zoom_factor, end[1]*window.zoom_factor)
        )
        angle = math.atan2((end[1]-start[1]), (end[0]-start[0]))
        arrow_size = 10
        arrow_x = end[0]*window.zoom_factor
        arrow_y = end[1]*window.zoom_factor
        p1 = QPointF(
            arrow_x - arrow_size * math.cos(angle - math.pi/6),
            arrow_y - arrow_size * math.sin(angle - math.pi/6)
        )
        p2 = QPointF(
            arrow_x - arrow_size * math.cos(angle + math.pi/6),
            arrow_y - arrow_size * math.sin(angle + math.pi/6)
        )
        path = QPainterPath(QPointF(arrow_x, arrow_y))
        path.lineTo(p1)
        path.lineTo(p2)
        path.lineTo(QPointF(arrow_x, arrow_y))
        painter.drawPath(path)

    elif atype == "circle":
        start = window.current_stroke["points"][0]
        end = window.current_stroke["points"][-1]
        left = min(start[0], end[0]) * window.zoom_factor
        top = min(start[1], end[1]) * window.zoom_factor
        width = abs(end[0]-start[0]) * window.zoom_factor
        height = abs(end[1]-start[1]) * window.zoom_factor
        painter.drawEllipse(left, top, width, height)

    elif atype == "callout":
        start = window.current_stroke["points"][0]
        end = window.current_stroke["points"][-1]
        left = min(start[0], end[0]) * window.zoom_factor
        top = min(start[1], end[1]) * window.zoom_factor
        w = abs(end[0]-start[0]) * window.zoom_factor
        h = abs(end[1]-start[1]) * window.zoom_factor
        painter.drawRect(left, top, w, h)
        anchor = window.current_stroke.get("anchor")  # the arrow tip
        if anchor:
            anchor_pt = QPointF(anchor[0]*window.zoom_factor, anchor[1]*window.zoom_factor)
            # line from top center of box to anchor
            box_mid_x = (left + left + w)/2
            box_top_y = top
            painter.drawLine(QPointF(box_mid_x, box_top_y), anchor_pt)
            # draw arrowhead
            angle = math.atan2(anchor_pt.y()-box_top_y, anchor_pt.x()-box_mid_x)
            arrow_size = 10
            p1 = QPointF(
                anchor_pt.x() - arrow_size * math.cos(angle - math.pi/6),
                anchor_pt.y() - arrow_size * math.sin(angle - math.pi/6)
            )
            p2 = QPointF(
                anchor_pt.x() - arrow_size * math.cos(angle + math.pi/6),
                anchor_pt.y() - arrow_size * math.sin(angle + math.pi/6)
            )
            path = QPainterPath(anchor_pt)
            path.lineTo(p1)
            path.lineTo(p2)
            path.lineTo(anchor_pt)
            painter.drawPath(path)

    painter.end()
    window.pdf_view.setPixmap(ephemeral_pixmap)
    window.last_point = new_point

def handle_mouse_release(window, event):
    if window.drawing and window.current_stroke:
        if window.annotation_type == "callout":
            # Optionally prompt for text here
            from PySide6.QtWidgets import QInputDialog
            text, ok = QInputDialog.getText(window, "Callout Text", "Text:")
            if ok and text:
                window.current_stroke["text"] = text
            # After the first callout is done, we reset the anchor so next callout is fresh
            window.callout_temp = None

        # Add stroke to permanent annotations
        window.state.add_stroke(window.current_page_num, window.current_stroke)

    window.drawing = False
    window.last_point = None
    window.current_stroke = None
    window.live_preview_pixmap = None
    window.display_page()
