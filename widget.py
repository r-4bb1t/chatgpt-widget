from PyQt5 import QtWidgets, QtCore, QtGui
from chatBubble import ChatBubble
import asyncio
from PyQt5.QtCore import QPropertyAnimation, QRect
from utils import get_gpt_response


class ChatWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setGeometry(0, 0, 400, 200)
        self.is_expanded = False
        self.original_height = 200

        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.set_main_widget()
        self.make_chat_widget()

        self.add_logs(self.chats_layout)
        self.add_input(self.chats_layout)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.main_layout.addWidget(self.chats)
        layout.addWidget(self.main_widget)
        self.add_topbar(self.main_widget)

        self.show_on_bottom_right()
        self.show()

    def set_main_widget(self):
        self.main_widget = QtWidgets.QWidget()
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_widget.setLayout(self.main_layout)
        self.main_widget.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        self.main_widget.setStyleSheet(
            """background: qradialgradient(cx:0, cy:0, radius: 1, fx:0, fy:0, stop:0 rgba(50, 50, 50, 90), stop:1 rgba(50, 50, 50, 60));
            border: 1px solid rgba(255,255,255, 50);
            border-radius: 10px;
            padding: 0;
            """
        )
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

    def make_chat_widget(self):
        self.chats = QtWidgets.QWidget()
        self.chats_layout = QtWidgets.QVBoxLayout()
        self.chats.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        self.chats.setLayout(self.chats_layout)

    def add_topbar(self, parent):
        self.topbar = QtWidgets.QWidget(parent)
        topbar_layout = QtWidgets.QHBoxLayout()
        self.topbar.setLayout(topbar_layout)
        self.topbar.setGeometry(0, 0, 400, 36)
        self.topbar.setStyleSheet(
            """
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(255, 255, 255, 60), stop:1 rgba(255, 255, 255, 0));
            border: none;
            """
        )

        self.add_size_button(topbar_layout)
        self.topbar.mousePressEvent = self.mousePressEvent
        self.topbar.mouseMoveEvent = self.mouseMoveEvent
        self.topbar.raise_()

    def mousePressEvent(self, event):
        self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QtCore.QPoint(event.globalPos() - self.old_pos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.old_pos = event.globalPos()

    def add_size_button(self, layout: QtWidgets.QHBoxLayout):
        self.size_button = QtWidgets.QPushButton()
        self.size_button.setFixedSize(40, 24)
        self.size_button.setIcon(QtGui.QIcon("icons/chevron-up.png"))
        self.size_button.setIconSize(QtCore.QSize(24, 24))
        self.size_button.setStyleSheet(
            """
            background: none;
            border: none;
            """
        )
        self.size_button.clicked.connect(self.toggle_size)
        self.size_button.raise_()
        layout.addWidget(self.size_button)

    def toggle_size(self):
        start_geometry = self.geometry()

        if self.is_expanded:
            self.size_button.setIcon(QtGui.QIcon("icons/chevron-up.png"))
            self.is_expanded = False
            end_height = self.original_height
        else:
            self.size_button.setIcon(QtGui.QIcon("icons/chevron-down.png"))
            self.is_expanded = True
            end_height = 600

        end_y = start_geometry.y() + start_geometry.height() - end_height
        end_geometry = QRect(
            start_geometry.x(), end_y, start_geometry.width(), end_height
        )

        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(100)
        self.animation.setStartValue(start_geometry)
        self.animation.setEndValue(end_geometry)
        self.animation.start()
        self.animation.finished.connect(self.scrollChatLogBottom)

        self.scrollChatLogBottom()

    def add_logs(self, layout: QtWidgets.QVBoxLayout):
        self.chat_log = QtWidgets.QListWidget()
        self.chat_log.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.chat_log.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.chat_log.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        self.chat_log.setContentsMargins(10, 20, 10, 10)

        self.chat_log.setStyleSheet(
            """
            QListWidget {
                border: none;
                background: rgba(0,0,0,0);
            }
            QListWidget::item:hover,
            QListWidget::item:disabled:hover,
            QListWidget::item:hover:!active {
                background: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: rgba(0,0,0,0);
                width: 8px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                border: none;
                background: white;
                border-radius: 4px;
                min-height: 0px;
            }
            QScrollBar::add-line:vertical {
                height: 0px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
                border: none;
            }
            QScrollBar::sub-line:vertical {
                height: 0px;
                subcontrol-position: top;   
                subcontrol-origin: margin;
                border: none;
            }
            """
        )
        layout.addWidget(self.chat_log)

    def add_input(self, layout: QtWidgets.QVBoxLayout):
        self.input_container = QtWidgets.QWidget()
        self.input_container_layout = QtWidgets.QHBoxLayout()
        self.input_container.setLayout(self.input_container_layout)
        self.input_container.setStyleSheet(
            """
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(255, 255, 255, 30), stop:1 rgba(255, 255, 255, 15));
            border: 1px solid rgba(255, 255, 255, 50);
            border-radius: 20px;
            padding: 5px;
            """
        )

        self.chat_input = QtWidgets.QLineEdit()
        self.chat_input.returnPressed.connect(
            lambda: asyncio.create_task(self.send_chat())
        )
        self.chat_input.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )

        self.chat_input.setStyleSheet(
            """
            background: rgba(255, 255, 255, 0);
            border: none;
            color: white;
            """
        )

        send_button = QtWidgets.QPushButton()
        send_button.setFixedSize(40, 24)
        send_button.setIcon(QtGui.QIcon("icons/send.png"))
        send_button.setIconSize(QtCore.QSize(24, 24))
        send_button.clicked.connect(lambda: asyncio.create_task(self.send_chat()))
        send_button.setStyleSheet(
            """
            background: rgba(255, 255, 255, 0);
            border: none;
            """
        )
        send_button.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
        )

        self.input_container_layout.addWidget(self.chat_input)
        self.input_container_layout.addWidget(send_button)
        layout.addWidget(self.input_container)

    async def send_chat(self):
        user_input = self.chat_input.text()
        self.chat_input.clear()
        if user_input:
            self.addChatBubble(user_input, True)
            self.scrollChatLogBottom()

            self.addChatBubble("...", False)

            response = await get_gpt_response(user_input)

            self.chat_log.takeItem(self.chat_log.count() - 1)

            self.addChatBubble(response, False)
            self.scrollChatLogBottom()

    def addChatBubble(self, text, is_user):
        bubble = ChatBubble(text, is_user, max_width=self.chat_log.width() - 20 - 16)
        item = QtWidgets.QListWidgetItem(self.chat_log)
        item.setSizeHint(
            QtCore.QSize(
                self.chat_log.width() - 20,
                bubble.height(),
            )
        )
        item.setFlags(item.flags() & ~QtCore.Qt.ItemIsSelectable)
        self.chat_log.addItem(item)
        self.chat_log.setItemWidget(item, bubble)
        self.topbar.raise_()
        return item

    def show_on_bottom_right(self):
        screen_geometry = QtWidgets.QApplication.desktop().screenGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()
        window_size = self.geometry()

        self.move(
            screen_width - window_size.width() - 100,
            screen_height - window_size.height() - 100,
        )

    def scrollChatLogBottom(self):
        self.chat_log.scrollToBottom()

    def closeEvent(self, event):
        asyncio.get_event_loop().stop()
