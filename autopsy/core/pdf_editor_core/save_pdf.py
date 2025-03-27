import fitz
from PySide6.QtGui import QColor
import math

def save_annotated_pdf(path, pdf_document, annotations):
    new_pdf = fitz.open()
    new_pdf.insert_pdf(pdf_document)
    for page_num, strokes in annotations.items():
        page = new_pdf[page_num]
        for stroke in strokes:
            t = stroke.get("type", "freehand")
            # Freehand, line annotations
            if t in ["freehand", "line"]:
                if len(stroke["points"]) > 1:
                    shape = page.new_shape()
                    shape.draw_polyline(stroke["points"])
                    color = QColor(stroke["color"])
                    rgb = (color.red()/255, color.green()/255, color.blue()/255)
                    shape.finish(
                        color=rgb, fill=None, width=stroke["width"],
                        stroke_opacity=stroke["opacity"], closePath=False
                    )
                    shape.commit(overlay=True)

            # Arrow annotation: draw shaft and then arrowhead using add_polygon_annot
            elif t == "arrow":
                if len(stroke["points"]) > 1:
                    # Draw arrow shaft
                    shape = page.new_shape()
                    shape.draw_polyline(stroke["points"])
                    color = QColor(stroke["color"])
                    rgb = (color.red()/255, color.green()/255, color.blue()/255)
                    shape.finish(
                        color=rgb, fill=None, width=stroke["width"],
                        stroke_opacity=stroke["opacity"], closePath=False
                    )
                    shape.commit(overlay=True)
                    
                    # Compute arrowhead at the end of the shaft
                    start = stroke["points"][0]
                    end = stroke["points"][-1]
                    angle = math.atan2(end[1]-start[1], end[0]-start[0])
                    arrow_size = 15  # adjust arrow size as needed
                    p1 = (
                        end[0] - arrow_size * math.cos(angle - math.pi/6),
                        end[1] - arrow_size * math.sin(angle - math.pi/6)
                    )
                    p2 = (
                        end[0] - arrow_size * math.cos(angle + math.pi/6),
                        end[1] - arrow_size * math.sin(angle + math.pi/6)
                    )
                    # Create arrowhead annotation as a filled polygon
                    arrow_annot = page.add_polygon_annot([end, p1, p2])
                    arrow_annot.set_colors({"stroke": rgb, "fill": rgb})
                    arrow_annot.set_opacity(stroke["opacity"])
                    arrow_annot.set_border(width=0)
                    arrow_annot.update()

            # Rectangle / highlight annotations
            elif t in ["rectangle", "highlight"]:
                if len(stroke["points"]) >= 2:
                    p1 = stroke["points"][0]
                    p2 = stroke["points"][-1]
                    rect = fitz.Rect(p1[0], p1[1], p2[0], p2[1])
                    color = QColor(stroke["color"])
                    rgb = (color.red()/255, color.green()/255, color.blue()/255)
                    if t == "highlight":
                        annot = page.add_rect_annot(rect)
                        annot.set_colors({"fill": rgb})
                        annot.set_opacity(stroke["opacity"])
                        annot.update()
                    else:
                        page.draw_rect(rect, color=rgb, width=stroke["width"])

            # Circle annotation
            elif t == "circle":
                if len(stroke["points"]) >= 2:
                    p1 = stroke["points"][0]
                    p2 = stroke["points"][-1]
                    rect = fitz.Rect(p1[0], p1[1], p2[0], p2[1])
                    color = QColor(stroke["color"])
                    rgb = (color.red()/255, color.green()/255, color.blue()/255)
                    page.draw_oval(rect, color=rgb, width=stroke["width"])

            # Text annotation
            elif t == "text":
                if stroke["points"]:
                    x, y = stroke["points"][0]
                    color = QColor(stroke["color"])
                    rgb = (color.red()/255, color.green()/255, color.blue()/255)
                    page.insert_text(
                        (x, y),
                        stroke.get("text", ""),
                        fontsize=12 * stroke["width"] / 2,
                        color=rgb
                    )

            # Callout annotation
            elif t == "callout":
                if len(stroke["points"]) >= 2:
                    p1 = stroke["points"][0]
                    p2 = stroke["points"][-1]
                    rect = fitz.Rect(p1[0], p1[1], p2[0], p2[1])
                    color = QColor(stroke["color"])
                    rgb = (color.red()/255, color.green()/255, color.blue()/255)
                    anchor = stroke.get("anchor", p1)
                    text_str = stroke.get("text", "")
                    callout_points = [
                        (anchor[0], anchor[1]),
                        (rect.x0, rect.y0)
                    ]
                    callout_annot = page.add_freetext_annot(
                        rect,
                        text_str,
                        fontsize=12 * stroke["width"] / 2,
                        fontname="helv",
                        text_color=rgb,
                        fill_color=(1, 1, 1),
                        border_width=stroke["width"],
                        callout=callout_points,
                        line_end=fitz.PDF_ANNOT_LE_OPEN_ARROW,
                        opacity=stroke["opacity"],
                        align=fitz.TEXT_ALIGN_CENTER
                    )
                    callout_annot.update()
    new_pdf.save(path)
