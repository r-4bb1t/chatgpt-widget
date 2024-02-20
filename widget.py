from PyQt5 import QtWidgets, QtCore, QtGui
from chatBubble import ChatBubble
import asyncio
from PyQt5.QtCore import QPropertyAnimation, QRect
from utils import getGPTResponse, resetHistory


class ChatWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setGeometry(0, 0, 400, 200)
        self.isExpanded = False
        self.originalHeight = 200

        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.makeMainWidget()
        self.makeChatWidget()

        self.addChatlog(self.chatsLayout)
        self.addInput(self.chatsLayout)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.mainLayout.addWidget(self.chats)
        layout.addWidget(self.mainWidget)
        self.addTopbar(self.mainWidget)

        self.showOnBottomRight()

    def makeMainWidget(self):
        self.mainWidget = QtWidgets.QWidget()
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainWidget.setLayout(self.mainLayout)
        self.mainWidget.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        self.mainWidget.setStyleSheet(
            """background: qradialgradient(cx:0, cy:0, radius: 1, fx:0, fy:0, stop:0 rgba(50, 50, 50, 90), stop:1 rgba(50, 50, 50, 60));
            border: 1px solid rgba(255,255,255, 50);
            border-radius: 10px;
            padding: 0;
            """
        )
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)

    def makeChatWidget(self):
        self.chats = QtWidgets.QWidget()
        self.chatsLayout = QtWidgets.QVBoxLayout()
        self.chats.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        self.chats.setLayout(self.chatsLayout)

    def addTopbar(self, parent):
        self.topBar = QtWidgets.QWidget(parent)
        topBarLayout = QtWidgets.QHBoxLayout()
        self.topBar.setLayout(topBarLayout)
        self.topBar.setGeometry(0, 0, 400, 48)
        self.topBar.setStyleSheet(
            """
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(255, 255, 255, 60), stop:1 rgba(255, 255, 255, 0));
            border: none;
            padding: 0;
            """
        )
        self.topBar.setContentsMargins(0, 0, 0, 0)
        self.addResetButton(topBarLayout)
        self.addSizeButton(topBarLayout)
        self.addCloseButton(topBarLayout)
        self.topBar.mousePressEvent = self.mousePressEvent
        self.topBar.mouseMoveEvent = self.mouseMoveEvent
        self.topBar.raise_()

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QtCore.QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def addSizeButton(self, layout: QtWidgets.QHBoxLayout):
        self.sizeButton = QtWidgets.QPushButton()
        self.sizeButton.setFixedSize(32, 32)
        self.sizeButton.setIcon(QtGui.QIcon("icons/chevron-up.png"))
        self.sizeButton.setIconSize(QtCore.QSize(24, 24))
        self.sizeButton.setStyleSheet(
            """
            QPushButton {
                background: none;
                border: none;
                border-radius: 16px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 30);
                border: none;
            }
            """
        )
        self.sizeButton.clicked.connect(self.toggleSize)
        self.sizeButton.raise_()
        layout.addWidget(self.sizeButton)

    def addCloseButton(self, layout: QtWidgets.QHBoxLayout):
        self.closeButton = QtWidgets.QPushButton()
        self.closeButton.setFixedSize(32, 32)
        self.closeButton.setIcon(QtGui.QIcon("icons/close.png"))
        self.closeButton.setIconSize(QtCore.QSize(24, 24))
        self.closeButton.setStyleSheet(
            """
            QPushButton {
                background: none;
                border: none;
                border-radius: 16px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 30);
                border: none;
            }
            """
        )
        self.closeButton.clicked.connect(self.close)
        self.closeButton.raise_()
        layout.addWidget(self.closeButton)

    def addResetButton(self, layout: QtWidgets.QHBoxLayout):
        self.resetButton = QtWidgets.QPushButton()
        self.resetButton.setFixedSize(32, 32)
        self.resetButton.setIcon(QtGui.QIcon("icons/reset.png"))
        self.resetButton.setIconSize(QtCore.QSize(24, 24))
        self.resetButton.setStyleSheet(
            """
            QPushButton {
                background: none;
                border: none;
                border-radius: 16px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 30);
                border: none;
            }
            """
        )
        self.resetButton.clicked.connect(self.reset)
        self.resetButton.raise_()
        layout.addWidget(self.resetButton)

    def reset(self):
        resetHistory()
        self.chatLog.clear()

    def toggleSize(self):
        startGeometry = self.geometry()

        if self.isExpanded:
            self.sizeButton.setIcon(QtGui.QIcon("icons/chevron-up.png"))
            self.isExpanded = False
            endHeight = self.originalHeight
        else:
            self.sizeButton.setIcon(QtGui.QIcon("icons/chevron-down.png"))
            self.isExpanded = True
            endHeight = 600

        endY = startGeometry.y() + startGeometry.height() - endHeight
        endGeometry = QRect(startGeometry.x(), endY, startGeometry.width(), endHeight)

        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(100)
        self.animation.setStartValue(startGeometry)
        self.animation.setEndValue(endGeometry)
        self.animation.start()
        self.animation.finished.connect(self.scrollChatLogBottom)

        self.scrollChatLogBottom()

    def addChatlog(self, layout: QtWidgets.QVBoxLayout):
        self.chatLog = QtWidgets.QListWidget()
        self.chatLog.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.chatLog.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.chatLog.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        self.chatLog.setContentsMargins(10, 20, 10, 10)

        self.chatLog.setStyleSheet(
            """
            QListWidget {
                border: none;
                background: rgba(0,0,0,0);
                padding-top: 20px;
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
        layout.addWidget(self.chatLog)

    def addInput(self, layout: QtWidgets.QVBoxLayout):
        self.inputContainer = QtWidgets.QWidget()
        self.inputContainerLayout = QtWidgets.QHBoxLayout()
        self.inputContainer.setLayout(self.inputContainerLayout)
        self.inputContainer.setStyleSheet(
            """
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(255, 255, 255, 30), stop:1 rgba(255, 255, 255, 15));
            border: 1px solid rgba(255, 255, 255, 50);
            border-radius: 20px;
            padding: 5px;
            """
        )

        self.chatInput = QtWidgets.QTextEdit()

        def keyPressEvent(event):
            if event.key() == QtCore.Qt.Key_Return:
                if event.modifiers() & QtCore.Qt.ShiftModifier:
                    self.chatInput.insertPlainText("\n")
                else:
                    asyncio.create_task(self.sendChat())
            else:
                QtWidgets.QTextEdit.keyPressEvent(self.chatInput, event)
            lineCount = self.chatInput.document().lineCount()
            self.chatInput.setFixedHeight(20 + 20 * min(lineCount, 4))

        self.chatInput.keyPressEvent = keyPressEvent
        self.chatInput.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.chatInput.setFixedHeight(40)
        self.chatInput.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum
        )

        self.chatInput.setStyleSheet(
            """
            background: rgba(255, 255, 255, 0);
            border: none;
            color: white;
            """
        )

        sendButton = QtWidgets.QPushButton()
        sendButton.setFixedSize(40, 24)
        sendButton.setIcon(QtGui.QIcon("icons/send.png"))
        sendButton.setIconSize(QtCore.QSize(24, 24))
        sendButton.clicked.connect(lambda: asyncio.create_task(self.sendChat()))
        sendButton.setStyleSheet(
            """
            background: rgba(255, 255, 255, 0);
            border: none;
            """
        )
        sendButton.setSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
        )

        self.inputContainerLayout.addWidget(self.chatInput)
        self.inputContainerLayout.addWidget(sendButton)
        layout.addWidget(self.inputContainer)

    async def sendChat(self):
        userInput = self.chatInput.toPlainText().strip()
        self.chatInput.clear()
        if userInput:
            self.addChatBubble(userInput, True)

            self.addChatBubble("...", False)
            self.scrollChatLogBottom()

            response = await getGPTResponse(userInput)

            self.chatLog.takeItem(self.chatLog.count() - 1)

            self.addChatBubble(response, False)
            self.scrollChatLogBottom()

    def addChatBubble(self, text, isUser):
        bubble = ChatBubble(text, isUser, maxWidth=self.chatLog.width() - 20 - 16)
        item = QtWidgets.QListWidgetItem(self.chatLog)
        item.setSizeHint(
            QtCore.QSize(
                self.chatLog.width() - 20,
                bubble.height(),
            )
        )
        item.setFlags(item.flags() & ~QtCore.Qt.ItemIsSelectable)
        self.chatLog.addItem(item)
        self.chatLog.setItemWidget(item, bubble)
        self.topBar.raise_()
        return item

    def showOnBottomRight(self):
        screenGeometry = QtWidgets.QApplication.desktop().screenGeometry()
        screenWidth = screenGeometry.width()
        screenHeight = screenGeometry.height()
        windowSize = self.geometry()

        self.move(
            screenWidth - windowSize.width() - 100,
            screenHeight - windowSize.height() - 100,
        )
        self.show()

    def scrollChatLogBottom(self):
        self.chatLog.scrollToBottom()

    def closeEvent(self, event):
        asyncio.get_event_loop().stop()
