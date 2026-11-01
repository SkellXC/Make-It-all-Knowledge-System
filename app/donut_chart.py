from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget


class DonutChart(QWidget):
    """A ring split into coloured segments, with the total written in the middle.

    segments: list of (label, value, "#hexcolour")
    """

    def __init__(self, segments, total_label="Total", parent=None):
        super().__init__(parent)
        self.segments = segments
        self.total_label = total_label
        self.setMinimumSize(190, 190)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        total = sum(value for _, value, _ in self.segments)
        side = min(self.width(), self.height())
        thickness = side * 0.11

        # drawArc draws the pen centred on the rectangle edge, so shrink the
        # rectangle by half the pen width to keep the ring inside the widget.
        rect = QRectF(
            (self.width() - side) / 2 + thickness / 2,
            (self.height() - side) / 2 + thickness / 2,
            side - thickness,
            side - thickness,
        )

        pen = QPen()
        pen.setWidthF(thickness)
        pen.setCapStyle(Qt.PenCapStyle.FlatCap)

        if total == 0:
            pen.setColor(QColor("#d8e0e5"))  # empty grey ring
            painter.setPen(pen)
            painter.drawArc(rect, 0, 360 * 16)
        else:
            start = 90 * 16  # Qt measures angles in 1/16 degree; 90 = 12 o'clock
            for _, value, color in self.segments:
                if value <= 0:
                    continue
                span = -round(value / total * 360 * 16)  # negative = clockwise
                pen.setColor(QColor(color))
                painter.setPen(pen)
                painter.drawArc(rect, start, span)
                start += span

        # Total in the middle
        text_color = self.palette().windowText().color()
        painter.setPen(text_color)

        number_font = QFont(self.font())
        number_font.setPointSizeF(26)
        number_font.setBold(True)
        painter.setFont(number_font)
        painter.drawText(
            QRectF(rect.x(), rect.y(), rect.width(), rect.height() * 0.56),
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom,
            str(total),
        )

        label_font = QFont(self.font())
        label_font.setPointSizeF(10)
        painter.setFont(label_font)
        painter.setPen(QColor("#5a6b75"))
        painter.drawText(
            QRectF(rect.x(), rect.y() + rect.height() * 0.56, rect.width(), rect.height() * 0.3),
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
            self.total_label,
        )


class StatusOverviewCard(QFrame):
    """Card with a title, a one-line description, a donut and a legend."""

    def __init__(self, title, subtitle, segments, total_label="Total", parent=None):
        super().__init__(parent)
        self.setObjectName("dashboardCard")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(4)

        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet("color: #5a6b75;")
        subtitle_label.setWordWrap(True)
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)

        body = QHBoxLayout()
        body.setSpacing(24)
        body.addWidget(DonutChart(segments, total_label), 3)

        legend = QVBoxLayout()
        legend.setSpacing(8)
        legend.addStretch()  # centres the legend next to the ring
        for label, value, color in segments:
            row = QHBoxLayout()
            row.setSpacing(8)
            swatch = QLabel()
            swatch.setFixedSize(12, 12)
            swatch.setStyleSheet(f"background: {color}; border-radius: 3px;")
            row.addWidget(swatch)
            row.addWidget(QLabel(f"{label}: {value}"))
            row.addStretch()
            legend.addLayout(row)
        legend.addStretch()
        body.addLayout(legend, 2)

        layout.addLayout(body, 1)