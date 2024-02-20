from PyQt5 import QtWidgets, QtCore


class ChatBubble(QtWidgets.QWidget):
    def __init__(self, text, is_user=True, max_width=380):
        super().__init__()
        self.layout = QtWidgets.QHBoxLayout()

        self.label = QtWidgets.QLabel(text)
        self.label.setWordWrap(True)

        self.label.setStyleSheet(
            "QLabel { background-color: white; color: black; %s; padding: 5px; }"
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
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum
        )
        self.label.adjustSize()
        self.updateGeometry()
