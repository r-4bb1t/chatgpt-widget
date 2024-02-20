import sys
from PyQt5 import QtWidgets
from PyQt5.QtGui import QFontDatabase, QFont

from widget import ChatWidget

import asyncio
import qasync

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    font_db = QFontDatabase()
    font_db.addApplicationFont("fonts/Pretendard-Regular.otf")
    app.setFont(QFont("Pretendard"))

    chat_widget = ChatWidget()

    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    with loop:
        loop.run_forever()
