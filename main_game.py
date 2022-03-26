from PyQt5.QtCore import * #QBasicTimer
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import random
import sys
import collections
#import pygame

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'Snake Game'
        self.setWindowTitle(self.title)
        self.setGeometry(400, 400, 400, 430)

        self.tabwi = myGame(self)
        self.setCentralWidget(self.tabwi)

class myGame(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        #self.tabs.resize(500, 500)

        #add tabs
        self.tabs.addTab(self.tab1, "Start Menu")
        self.tabs.addTab(self.tab2, "Game")
        self.tabs.addTab(self.tab3, "End")

        #tab1 layout
        self.tab1.layout = QGridLayout(self)
        self.tab1_littleLayout = QHBoxLayout(self)
        self.nameEdit = QLineEdit()
        self.nameEdit.setAlignment(Qt.AlignCenter)
        self.name = ""

        # button
        self.startButton = Button("START", self.buttonClicked)
        self.nameButton = Button("OK", self.buttonClicked)
        self.tab1.layout.addWidget(self.startButton, 1, 0, alignment=Qt.AlignCenter)
        self.tab1_littleLayout.addWidget(self.nameEdit)
        self.nameEdit.setFixedSize(200, 30)
        self.tab1_littleLayout.addWidget(self.nameButton)
        self.tab1.layout.addLayout(self.tab1_littleLayout, 0, 0, alignment=Qt.AlignCenter)
        self.tab1.setLayout(self.tab1.layout)

        #tab2 layout
        self.tab2.layout = QVBoxLayout(self)
        self.launch_game = SnakeGame()
        self.tab2.layout.addWidget(self.launch_game)
        self.endButton = Button("End", self.buttonClicked)
        self.tab2.layout.addWidget(self.endButton)
        self.tab2.setLayout(self.tab2.layout)

        #tab3 content
        self.scoreBoard = QTextEdit()
        self.scoreBoard.setReadOnly(True)
        font = self.scoreBoard.font()
        font.setPointSize(15)
        font.setFamily('Courier New')
        self.scoreBoard.setFont(font)

        #tab3 layout
        self.tab3.layout = QGridLayout(self)
        self.scoreBoard.resize(200, 200)
        self.tab3.layout.addWidget(self.scoreBoard)
        self.tab3.setLayout(self.tab3.layout)

        #tabs layout
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    def buttonClicked(self):
        button = self.sender()
        key = button.text()

        if key == "OK":
            self.name = self.nameEdit.text()
            print(self.name)
        elif key == "START":
            if self.name != "": #player가 이름을 입력해야 게임이 start될 수 있도록
                self.on_click_select_tab2()
        elif key == "End":
            self.on_click_select_tab3()

    def on_click_select_tab2(self):
        return self.tabs.setCurrentIndex(1)

    def on_click_select_tab3(self):
        out = open("/home/jje/scoreDB.txt", "a")
        out.write("\n"+self.name+" "+str(Board.SCORE))
        out.close()
        # read scoreDB
        self.scoreBoard.setText("★★명예전당5인★★\n")
        self.scoreBoard.setAlignment(Qt.AlignCenter)

        file = open('/home/jje/scoreDB.txt', "r")
        medi = []
        for line in file:
            medi += line.split()
        print(medi)
        winner = {}

        for i in range(0, len(medi) - 1, 2):
            winner[medi[i]] = medi[i + 1]

        fiveWinner = collections.Counter(winner).most_common(5)
        fiveWinner.sort(key=lambda x: eval(x[1]), reverse=True)

        for win in fiveWinner:
            self.scoreBoard.append("\n"+win[0] + " " + win[1])
            self.scoreBoard.setAlignment(Qt.AlignCenter)

        return self.tabs.setCurrentIndex(2)

class Button(QToolButton):
    def __init__(self, text, callback):
        super().__init__()
        self.setText(text)
        self.clicked.connect(callback)

class SnakeGame(QMainWindow):
    def __init__(self):
        super(SnakeGame, self).__init__() #생성자 가져오기
        self.gboard = Board(self)

        self.statusbar = self.statusBar() #QtWidgets을 상속받음. method 중 하나임.
        self.gboard.msg2statusbar[str].connect(self.statusbar.showMessage) #at the bottom

        self.setCentralWidget(self.gboard) #QMainWindow의 method 사용함.
        #self.setWindowTitle('Snake game')
        self.resize(400, 400)
        screen = QDesktopWidget().screenGeometry() #잘 모름
        size = self.geometry()
        self.move(int((screen.width()-size.width())/2), int((screen.height()-size.height())/2)) #절대위치 지정

        #배경화면 색 설정
        pal = QPalette()
        pal.setColor(QPalette.Background, QColor(255, 255, 250))
        self.setPalette(pal)

        #게임시작
        self.gboard.start()
        self.show()

class Board(QFrame):
    msg2statusbar = pyqtSignal(str) #이벤트 발생을 의미. 문자를 신호로 만들겠다.
    SPEED = 150
    WIDTHINBLOCKS = 20
    HEIGHTINBLOCKS = 20
    SCORE = 0

    # pygame.mixer.init()
    # pygame.mixer.music.load("Jingle_Bells_Instrumental_Jazz(wav).wav")

    def __init__(self, parent):
        super(Board, self).__init__(parent)
        self.level = 1  # level 설정. #########################
        self.timer = QBasicTimer()
        self.snake = [[10, 5], [10, 6]] #초기 뱀 #열, 행
        self.current_x_head = self.snake[0][0]
        self.current_y_head = self.snake[0][1]
        self.food = []
        self.score = len(self.snake)-2
        self.grow_snake = False
        self.board = []
        self.direction = 4
        self.bgame = False #게임의 진행상태
        self.drop_food()
        self.setFocusPolicy(Qt.StrongFocus) #키보드의 입력받음

        # if self.timer:
        #     pygame.mixer.music.play(0)

    def setSpeed(self, speed):
        Board.SPEED = speed

    def raiseLevel(self):
        if self.score <= 2:
            self.level = 1
            self.setSpeed(150)
            self.timer.start(Board.SPEED, self)
        elif self.score <= 4:
            self.level = 2
            self.setSpeed(130)
            self.timer.start(Board.SPEED, self)
        elif self.score <= 6:
            self.level = 3
            self.setSpeed(100)
            self.timer.start(Board.SPEED, self)
        else:
            self.level = 4
            self.setSpeed(70)
            self.timer.start(Board.SPEED, self)

    def square_width(self): #window 너비의 블럭 갯수로 나눈 것의 값
        return self.contentsRect().width() / Board.WIDTHINBLOCKS

    def square_height(self):
        return self.contentsRect().height() / Board.HEIGHTINBLOCKS

    def start(self):
        if not self.bgame:
            self.msg2statusbar.emit("start game by pressing space key")

    def keydown(self, key):
        if (key == Qt.Key_Space):
            self.bgame = True
            self.msg2statusbar.emit("Score: " + str(len(self.snake) - 2) + " / level: " + str(self.level))  # 메세지 방출
            self.timer.start(Board.SPEED, self)


    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.contentsRect()
        boardtop = rect.bottom() - Board.HEIGHTINBLOCKS * self.square_height() #QRect의 method인 bottom

        #뱀머리 색만 다르게
        self.draw_square(painter, rect.left() + self.snake[0][0] * self.square_width(),
                         boardtop + self.snake[0][1] * self.square_height(), QColor(0xFFA7A7))

        for pos in range(1, len(self.snake)):
            self.draw_square(painter, rect.left() + self.snake[pos][0] * self.square_width(),
                             boardtop + self.snake[pos][1] * self.square_height(), QColor(0xFFD8D8))
        for pos in self.food:
            self.draw_square(painter, rect.left() + pos[0] * self.square_width(),
                      boardtop + pos[1] * self.square_height(), QColor(0xCC0000))

    def draw_square(self, painter, x, y, color):
        painter.fillRect(x + 1, y + 1, self.square_width() - 2,
                         self.square_height() - 2, color)

    def keyPressEvent(self, event):
        key = event.key()
        self.keydown(key)
        if key == Qt.Key_Left:
            if self.direction != 2:
                self.direction = 1
        elif key == Qt.Key_Right:
            if self.direction != 1:
                self.direction = 2
        elif key == Qt.Key_Down:
            if self.direction != 4:
                self.direction = 3
        elif key == Qt.Key_Up:
            if self.direction != 3:
                self.direction = 4

    def move_snake(self):
        if self.direction == 1: #왼쪽
            self.current_x_head, self.current_y_head = self.current_x_head - 1, self.current_y_head
            if self.current_x_head < 0: #벽
                self.game_over()
        if self.direction == 2: #오른쪽
            self.current_x_head, self.current_y_head = self.current_x_head + 1, self.current_y_head
            if self.current_x_head == Board.WIDTHINBLOCKS:
                self.game_over()
        if self.direction == 3: #아래
            self.current_x_head, self.current_y_head = self.current_x_head, self.current_y_head + 1
            if self.current_y_head == Board.HEIGHTINBLOCKS:
                self.game_over()
        if self.direction == 4: #위쪽
            self.current_x_head, self.current_y_head = self.current_x_head, self.current_y_head - 1
            if self.current_y_head < 0:
                self.game_over()

        head = [self.current_x_head, self.current_y_head]
        self.snake.insert(0, head)
        if not self.grow_snake: #이게 false일 때
            self.snake.pop() #업데이트 될 때마다 꼬리 잘라주기
        else:
            self.msg2statusbar.emit("Score: "+str(len(self.snake)-2)+ " / level: "+ str(self.level))
            self.grow_snake = False

    def timerEvent(self, event):
        if (event.timerId() == self.timer.timerId()):
            self.raiseLevel()
            self.move_snake()
            self.food_collision()
            self.is_suicide()
            self.update()

    def is_suicide(self):  # If snake collides with itself, game is over
        for i in range(1, len(self.snake)):
            if self.snake[i] == self.snake[0]:
                self.game_over()

    def food_collision(self): #eat food
        for pos in self.food:
            if pos == self.snake[0]:
                self.food.remove(pos)
                self.drop_food()
                self.grow_snake = True

    def drop_food(self):
        x = random.randint(2, 18)
        y = random.randint(2, 18)
        for pos in self.snake:  # Do not drop food on snake / 닿아있으면 음식 그 자리에 놓지 않도록 하는 메소드
            if pos == [x, y]:
                self.drop_food()
        self.food.append([x, y])

    def game_over(self):
        self.msg2statusbar.emit(str("game over"))
        self.timer.stop()
        Board.SCORE = len(self.snake) -2
        print(Board.SCORE)
        # pygame.mixer.music.stop()
        # pygame.mixer.music.load("Babies_Cry(wav).wav")
        # pygame.mixer.music.play(27)
        self.snake = [  # End 수놓기
            [4, 8], [4, 9], [4, 10], [4, 11], [4, 12],
            [5, 8], [5, 10], [5, 12],
            [6, 8], [6, 10], [6, 12],
            [8, 10], [8, 11], [8, 12],
            [9, 10],
            [10, 10], [10, 11], [10, 12],
            [12, 10], [12, 11], [12, 12],
            [13, 10], [13, 12],
            [14, 8], [14, 9], [14, 10], [14, 11], [14, 12], [14, 13]
            # [14, 13] 은 pop때문에 마지막 수가 표현되지 않기 때문에 임의로 적어넣은 값이다.
        ]


def main():
    app = QApplication([])
    ex = App()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()