from PySide6.QtGui import QPainter, QPainterPath, QPen, QColor, QPixmap, QImage
from PySide6.QtCore import Qt, QPointF, QRectF
import fitz
import math

def render_page(page, zoom, annotations):
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
    qimg = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
    pixmap = QPixmap.fromImage(qimg)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    for stroke in annotations:
        t = stroke.get("type", "freehand")
        if t in ["freehand", "line"]:
            color = QColor(stroke["color"])
            color.setAlphaF(stroke["opacity"])
            pen = QPen(color)
            pen.setWidthF(stroke["width"])
            pen.setCapStyle(Qt.RoundCap)
            pen.setJoinStyle(Qt.RoundJoin)
            painter.setPen(pen)
            points = stroke["points"]
            if points:
                path = QPainterPath()
                start = QPointF(points[0][0] * zoom, points[0][1] * zoom)
                path.moveTo(start)
                for x, y in points[1:]:
                    path.lineTo(QPointF(x * zoom, y * zoom))
                painter.drawPath(path)
        elif t == "arrow":
            if len(stroke["points"]) >= 2:
                start = QPointF(stroke["points"][0][0] * zoom, stroke["points"][0][1] * zoom)
                end = QPointF(stroke["points"][-1][0] * zoom, stroke["points"][-1][1] * zoom)
                color = QColor(stroke["color"])
                color.setAlphaF(stroke["opacity"])
                pen = QPen(color)
                pen.setWidthF(stroke["width"])
                pen.setCapStyle(Qt.RoundCap)
                pen.setJoinStyle(Qt.RoundJoin)
                painter.setPen(pen)
                painter.drawLine(start, end)
                # Draw arrowhead
                angle = math.atan2(end.y()-start.y(), end.x()-start.x())
                arrow_size = 10
                p1 = QPointF(
                    end.x() - arrow_size * math.cos(angle - math.pi/6),
                    end.y() - arrow_size * math.sin(angle - math.pi/6)
                )
                p2 = QPointF(
                    end.x() - arrow_size * math.cos(angle + math.pi/6),
                    end.y() - arrow_size * math.sin(angle + math.pi/6)
                )
                arrow_path = QPainterPath()
                arrow_path.moveTo(end)
                arrow_path.lineTo(p1)
                arrow_path.lineTo(p2)
                arrow_path.lineTo(end)
                painter.drawPath(arrow_path)
        elif t == "rectangle" or t == "highlight":
            if len(stroke["points"]) >= 2:
                p1 = stroke["points"][0]
                p2 = stroke["points"][-1]
                left = min(p1[0], p2[0]) * zoom
                top = min(p1[1], p2[1]) * zoom
                width = abs(p2[0]-p1[0]) * zoom
                height = abs(p2[1]-p1[1]) * zoom
                color = QColor(stroke["color"])
                color.setAlphaF(stroke["opacity"])
                pen = QPen(color)
                pen.setWidthF(stroke["width"])
                pen.setCapStyle(Qt.RoundCap)
                pen.setJoinStyle(Qt.RoundJoin)
                painter.setPen(pen)
                if t == "highlight":
                    painter.setBrush(color)
                    painter.setOpacity(0.3)
                    painter.drawRect(QRectF(left, top, width, height))
                    painter.setBrush(Qt.NoBrush)
                    painter.setOpacity(1.0)
                    painter.drawRect(QRectF(left, top, width, height))
                else:
                    painter.drawRect(QRectF(left, top, width, height))
        elif t == "circle":
            if len(stroke["points"]) >= 2:
                p1 = stroke["points"][0]
                p2 = stroke["points"][-1]
                left = min(p1[0], p2[0]) * zoom
                top = min(p1[1], p2[1]) * zoom
                width = abs(p2[0]-p1[0]) * zoom
                height = abs(p2[1]-p1[1]) * zoom
                color = QColor(stroke["color"])
                color.setAlphaF(stroke["opacity"])
                pen = QPen(color)
                pen.setWidthF(stroke["width"])
                pen.setCapStyle(Qt.RoundCap)
                pen.setJoinStyle(Qt.RoundJoin)
                painter.setPen(pen)
                painter.drawEllipse(QRectF(left, top, width, height))
        elif t == "text":
            if stroke["points"]:
                x, y = stroke["points"][0]
                color = QColor(stroke["color"])
                color.setAlphaF(stroke["opacity"])
                pen = QPen(color)
                pen.setWidthF(stroke["width"])
                painter.setPen(pen)
                painter.drawText(QPointF(x * zoom, y * zoom), stroke.get("text", ""))
        elif t == "callout":
            if len(stroke["points"]) >= 2:
                # Draw callout box
                p1 = stroke["points"][0]
                p2 = stroke["points"][-1]
                left = min(p1[0], p2[0]) * zoom
                top = min(p1[1], p2[1]) * zoom
                width = abs(p2[0]-p1[0]) * zoom
                height = abs(p2[1]-p1[1]) * zoom
                color = QColor(stroke["color"])
                color.setAlphaF(stroke["opacity"])
                pen = QPen(color)
                pen.setWidthF(stroke["width"])
                painter.setPen(pen)
                painter.drawRect(QRectF(left, top, width, height))
                # Draw arrow from anchor to top center of the box
                anchor = stroke.get("anchor")
                if anchor:
                    anchor_pt = QPointF(anchor[0]*zoom, anchor[1]*zoom)
                    box_mid_x = (left + left + width) / 2
                    box_top_y = top
                    painter.drawLine(QPointF(box_mid_x, box_top_y), anchor_pt)
                    # Draw arrowhead
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
                    arrow_path = QPainterPath()
                    arrow_path.moveTo(anchor_pt)
                    arrow_path.lineTo(p1)
                    arrow_path.lineTo(p2)
                    arrow_path.lineTo(anchor_pt)
                    painter.drawPath(arrow_path)
                    # Draw text in center of the box if provided
                    if "text" in stroke:
                        painter.drawText(QRectF(left, top, width, height), Qt.AlignCenter, stroke["text"])
    painter.end()
    return pixmap
