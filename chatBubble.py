from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt


class ChatBubble(QtWidgets.QWidget):
    def __init__(self, text, is_user=True, maxWidth=380):
        super().__init__()
        self.layout = QtWidgets.QHBoxLayout()

        self.label = QtWidgets.QLabel(text)
        self.label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.label.setMaximumWidth(maxWidth)

        self.label.setStyleSheet(
            """QLabel { background-color: qradialgradient(cx:0, cy:0, radius: 1, fx:0, fy:0, stop:0 rgba(0, 0, 0, 60), stop:1 rgba(0, 0, 0, 30));
                border: 1px solid rgba(255, 255, 255, 0.6);
                color: white; %s;
                padding-top: 12px; padding-bottom: 12px; padding-left: 8px; padding-right: 8px;
                }"""
            % (
                """border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                border-bottom-right-radius: 0;
                border-bottom-left-radius: 10px;"""
                if is_user
                else """border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                border-bottom-right-radius: 10px;
                border-bottom-left-radius: 0;"""
            )
        )

        if is_user:
            self.layout.addWidget(self.label, alignment=QtCore.Qt.AlignRight)
        else:
            self.layout.addWidget(self.label, alignment=QtCore.Qt.AlignLeft)

        self.setLayout(self.layout)
        self.layout.setContentsMargins(8, 8, 8, 8)
        self.label.setWordWrap(True)
        self.setFixedHeight(
            max(self.label.sizeHint().height(), self.label.heightForWidth(maxWidth))
            + 16
        )
        print(text)
        self.updateGeometry()
