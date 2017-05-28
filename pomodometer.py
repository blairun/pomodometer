import sys

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QWidget, \
    QLabel, QAction, QTableWidget, QTableWidgetItem, QVBoxLayout, QTextEdit, \
    QHBoxLayout, QBoxLayout, QPushButton, QFileDialog, QSizePolicy, QMessageBox, QLineEdit

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as \
    FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as \
    NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.animation as animation

import locale

import random
import numpy as np
from numpy import genfromtxt
import unittest
import csv

# peculiarities of windows 7 requires the following to display icon on taskbar:
import ctypes
myappid = 'mycompany.myproduct.subproduct.version'  # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

# projects = ['first project', 'second project', 'third project']
# savings = [50000, 100000, 100001]
x = y = a = h = k = percent = 0
goal = ""
imagePath = 'background.png'
anim_running = True
img_background = plt.imread(imagePath)
img_tomato = plt.imread("tomato.png")
img_splat = plt.imread("splat.png")

class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'pomodometer'
        self.left = 250
        self.top = 250
        self.width = 1000
        self.height = 600
        self.initUI()
        # set window icon (see above for taskbar)
        self.setWindowIcon(QIcon('tomato.png'))

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('File')
        editMenu = mainMenu.addMenu('Edit')
        # viewMenu = mainMenu.addMenu('View')
        # searchMenu = mainMenu.addMenu('Search')
        # toolsMenu = mainMenu.addMenu('Tools')
        helpMenu = mainMenu.addMenu('Help')
        # TODO menu: help: about: webkit pointing to Energy Trust SEM website
        # (note that this is not endorsed)

        exitButton = QAction(QIcon('splat.png'), 'Exit', self)
        # exitButton.setShortcut('Ctrl+Q')
        exitButton.setShortcut('Ctrl+W')
        exitButton.setStatusTip('Exit application')
        exitButton.triggered.connect(self.close)
        fileMenu.addAction(exitButton)

        ChangeBackgroundImage = QAction(QIcon(imagePath),
                                        'Change Background Image', self)
        ChangeBackgroundImage.setStatusTip('Choose new background image from \
                                            disk')
        ChangeBackgroundImage.triggered.connect(self.openFileNameDialog)
        editMenu.addAction(ChangeBackgroundImage)
        # TODO fix background image replacement

        # pass reference to the canvas to the App. Make a few changes
        # to the App initializer to accomodate canvas reference.
        # Then bind it to App instance
        self.table_widget = MyMainWidget(self)
        self.setCentralWidget(self.table_widget)
        self.statusBar().showMessage('splat')
        # TODO call this from the plt method below

        self.show()

    # File picker for background image
    # enable background image replacement
    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Choose new \
            background image", "", "All Files (*);; Image Files \
            (*.jpg);; Image Files (*.png)", options=options)
        if fileName:
            # print(fileName)
            global imagePath
            imagePath = fileName
            self.table_widget = MyMainWidget(self)
            self.setCentralWidget(self.table_widget)
            global x
            x = 0
            # print(imagePath)
            # m = MyMainWidget(App())
            # m.background_image()
            # MyMainWidget.background_image()
            # MyMainWidget.canvas.draw()
            # https://stackoverflow.com/questions/4618435/tkinter-canvas-access-from-a-separate-class
            # TODO how to refer to mymainwidget from outside of the class


class MyMainWidget(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)

        # CHANGED replace background image with matplotlib
        # Create widget
        # label1 = QLabel(self)
        # pixmap = QPixmap('image.jpg')
        # label1.setPixmap(pixmap)
        # #self.resize(pixmap.width() + 250, pixmap.height())
        # self.setMinimumSize(pixmap.width() + 250, pixmap.height())

        # a figure instance to plot on
        self.figure = plt.figure()

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        # self.toolbar = NavigationToolbar(self.canvas, self)

        # Just a button connected to `plot` method
        self.button = QPushButton('Throw!')
        self.button.clicked.connect(self.plot)

        # set the layout
        self.plotLayout = QVBoxLayout()
        # self.plotLayout.addWidget(self.toolbar)
        self.plotLayout.addWidget(self.canvas)
        self.plotLayout.addWidget(self.button)
        # self.setLayout(layout)

        with open('Projects.txt') as f:
            projectsText = f.readlines()
        with open('Savings.txt') as f:
            savingsText = f.readlines()
        # with open('goal.txt') as f:
        #     goal = f.readlines()
        # Create table for projects
        self.createTable(max(len(projectsText), len(savingsText))+1)

        # button to kick off an action such as throwing pomodoro
        # button = QPushButton('PyQt5 button', self)
        # button.setToolTip('This is an example button')

        self.labelSavings = QLabel('', self)
        self.savings_calc()
        self.labelSavings.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        # self.goal_calc()
        # self.labelGoal = QLabel('Goal: ' + '{:,}'.format(int(goal[0])), self)
        self.labelGoal = QLabel('Goal: ')  # +
        #                       '{:,}'.format(self.goal_calc()), self)
        self.labelGoal.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        # self.labelGoal.doubleClicked.connect(self.dbl_click)
        # self.labelGoal.mousePressEvent = self.dbl_click

        self.textGoalEdit = QLineEdit()
        self.textGoalEdit.setFixedWidth(80)
        self.textGoalEdit.setAlignment(QtCore.Qt.AlignLeft)
        self.textGoalEdit.setText(str('{:,}'.format(self.goal_calc())))
        self.textGoalEdit.textEdited.connect(self.update_goal)

        # nested savings and goal layout
        self.SavingsGoalLayout = QHBoxLayout()
        self.SavingsGoalLayout.addWidget(self.labelGoal, 0)
        self.SavingsGoalLayout.addWidget(self.textGoalEdit, 0)
        self.SavingsGoalLayout.addWidget(self.labelSavings, 1)

        # create vertical layout widget for table and button
        self.tablelayout = QVBoxLayout()
        self.tablelayout.addWidget(self.tableWidget)
        self.tablelayout.addLayout(self.SavingsGoalLayout)

        # self.tablelayout.addWidget(button)
        # self.setLayout(self.tablelayout)

        # set a horizontal layout, add plot and table layouts
        self.layout = QHBoxLayout()
        self.layout.addLayout(self.plotLayout, 3)
        self.layout.addLayout(self.tablelayout, 1)
        self.setLayout(self.layout)

        # HACK Create widget for small image overlay
        # label2 = QLabel(self)
        # pixmap = QPixmap('exit243.png')
        # label2.setPixmap(pixmap)
        # label2.move(300, 50)

        # Show widgets
        self.show()

    # TODO Consolidate all calls to savings.txt and projects.txt
    def savings_calc(self):
        # populate total project savings
        sumTotal = 0
        with open('Savings.txt') as f:
            savingsText = f.readlines()
            for i in range(0, len(savingsText)):
                # if isinstance(savingsText[i], int):
                try:
                    int(savingsText[i])
                except ValueError:
                    continue
                sumTotal = int(savingsText[i]) + sumTotal
        self.labelSavings.setText('Total Savings: '
                                  + '{:,}'.format(sumTotal))
        return sumTotal

    def goal_calc(self):
        locale.setlocale(locale.LC_ALL, '')
        # populate total project savings
        with open('goal.txt') as f:
            goaltext = f.readlines()
            global goal
            # print(goal)
            goal = locale.atoi(goaltext[0])
            # print(goal)
            return goal

    def update_goal(self):
        global goal
        # check if goal is an integer
        # print(goal)
        try:
            locale.atoi(self.textGoalEdit.text())
            # print(goal)
            goal = locale.atoi(self.textGoalEdit.text())
        except ValueError:
            print("error")

        # set min and max
        if goal < 1: goal = 1
        if goal > 9999999999: goal = 9999999999

        # update persistent goal and textbox
        with open('goal.txt', 'w') as f:
            f.seek(0)
            f.truncate()
            # f.write(str(goal))
            f.write(str('{:,}'.format(goal)))
            print(goal)
        self.textGoalEdit.setText(str('{:,}'.format(goal)))

    @classmethod
    def background_image(cls):
        img = plt.imread(imagePath)
        # ax = cls.figure.add_subplot(111)
        # ax.imshow(img_background, extent=[0, 1000, 0, 1000])
        print(imagePath)
        cls.canvas.draw()

    # initialization function: plot the background of each frame
    @staticmethod
    def init_plot():
        global img_background
        plt.imshow(img_background, extent=(0, 1000, 0, 1000))

    @staticmethod
    def updatefig(i):
        # TODO optimize this method!
        # global x, y
        i += 1
        # plt.imshow(img_tomato, extent=(0, 50, 0, 50))
        # data =
        # img_p.set_data(data)
        # self.canvas.draw()
        plt.clf()
        # img_background = plt.imread(imagePath)
        global img_background, img_tomato, img_splat, x, y
        plt.imshow(img_background, extent=[0, 1000, 0, 1000])
        axes = plt.gca()
        axes.set_xlim([-100, 1100])
        axes.set_ylim([-100, 1100])
        # plt.draw()
        # img_background = plt.imread(imagePath)
        # global percent
        # if percent > 1:
        #     percent = 1

        # define parabola based on magnitude of kwh/joules
        # a = -0.004 / percent  # adjusts stretch, min -100, max -0.004
        # h = 500 * percent    # adjusts midpoint, max 500
        # k = 1000 * percent   # adjusts height, max 1000

        # print(x, k)

        if x >= k:
            # Splat
            x = k
            # img_tomato = plt.imread("tomatometer pics/ink (2).png")
            # img_tomato = plt.imread("12.jpg")
            plt.imshow(img_splat, extent=(x - 50, x + 50, y - 50, y + 50))
            x = y = 0
            # print(x, y)
            # TODO fix splat when percent = 1
        else:
            # Parabola
            x = i
            y = a * (x - h) ** 2 + k
            # img_tomato = plt.imread("tomatometer pics/tomato-clipart-tomato5.png")
            # img_tomato = plt.imread("exit243.png")
            plt.imshow(img_tomato, extent=(x - 25, x + 25, y - 25, y + 25))

        axes.set_aspect('auto')
        plt.axis('off')  # hide axis
        # print(i)

    # @staticmethod
    def plot(self):
        ''' plot some random stuff '''
        # random data
        # data = [random.random() for i in range(10)]
        # i = [random.random() * 1000]

        # Adjust parabola based on savings value
        global percent
        percent = self.savings_calc() / self.goal_calc()
        if percent > 1:
            percent = 1

        # define parabola based on magnitude of kwh/joules
        global a, h, k
        a = -0.004 / percent  # adjusts stretch, min -100, max -0.004
        h = 500 * percent    # adjusts midpoint, max 500
        k = 1000 * percent   # adjusts height, max 1000

        # self.figure.clear()

        # add background image to plot. See
        # http://stackoverflow.com/questions/34458251/plot-over-an-image-background-in-python
        # img_background = plt.imread(imagePath)
        # # print(imagePath)
        # # subplot grid parameters encoded as a single integer. "111" means
        # # "1x1 grid, first subplot" and "234" means "2x3 grid, 4th subplot"
        # ax = self.figure.add_subplot(111)
        # ax.imshow(img_background, extent=[0, 1000, 0, 1000])
        # axes = plt.gca()
        # axes.set_xlim([0, 1000])
        # axes.set_ylim([0, 1000])
        # # automatically fills / stretches figure rectangle with data
        # axes.set_aspect('auto')
        # plt.axis('off')  # hide axis

        # plot data
        # ax.plot(data, '*-')

        # i = int(self.tableWidget.item(0, 1).text())
        # for i in range(0 To k):
        # x = i
        # global x
        # y = a * (x - h) ** 2 + k
        # Next
        # self.tableWidget.setItem(0, 1, QTableWidgetItem(str(i + 100)))

        # ax.plot(x, y, 'o', color='firebrick')

        # if x >= k:
        #     x = k
        # else:
        #     x += 100
        self.button.setText('Throw Again!')

        # print(percent*1000)
        ani = animation.FuncAnimation(self.figure, self.updatefig, repeat=False,
                                      interval=10, frames=int(percent*1000)+2)
        # init_func = self.init_plot,

        # Pause and restart animation
        global anim_running
        # print(anim_running)
        if anim_running:
            ani.event_source.stop()
            anim_running = False
        else:
            ani.event_source.start()
            anim_running = True

        self.canvas.draw()

    def createTable(self, rows):
        # Create table w/ two columns for proj descriptions and savings values
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(rows)
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setHorizontalHeaderLabels(['Project Description',
                                                    'Savings Value'])
        self.tableWidget.horizontalHeader().setSectionResizeMode(0, 1)
        self.tableWidget.setColumnWidth(1, 100)
        # self.tableWidget.resizeColumnsToContents()
        # IDEA limit column 2 to numbers
        # self.tableWidget.setItem(0,0, QTableWidgetItem("Cell (1,1)"))
        # self.tableWidget.move(1,1)

        # Store description and savings values between sessions
        # probably easiest by reading from and storing to between csv/txt files
        # with open('projectData.csv', 'r') as f:  # for 2 columns
        # with open('projectData.csv') as f:
        #     reader = csv.reader(f, delimiter=",")
        #     your_list = list(reader)

        # print(your_list)
        # [['This is the first line', 'Line1'],
        #  ['This is the second line', 'Line2'],
        #  ['This is the third line', 'Line3']]

        # my_data = genfromtxt('Projects.txt', delimiter=',')

        with open('Projects.txt') as f:
            projectsText = f.readlines()
        for i in range(0, len(projectsText)):
            self.tableWidget.setItem(i, 0, QTableWidgetItem(
                str(projectsText[i])))

        with open('Savings.txt') as f:
            savingsText = f.readlines()
        for i in range(0, len(savingsText)):
            self.tableWidget.setItem(i, 1, QTableWidgetItem(
                str(savingsText[i])))

        # table selection change
        # self.tableWidget.doubleClicked.connect(self.on_click)
        self.tableWidget.itemChanged.connect(self.on_click)

    @pyqtSlot()
    def on_click(self):

        # rewrite projects and savings after change
        with open('Projects.txt', 'w') as f:
            f.seek(0)
            f.truncate()
        with open('Projects.txt', 'w') as f:
            for i in range(0, self.tableWidget.rowCount()):
                if self.tableWidget.item(i, 0):
                    f.write(self.tableWidget.item(i, 0).text().rstrip())
                    f.write('\n')
        with open('Savings.txt', 'w') as f:
            f.seek(0)
            f.truncate()
        with open('Savings.txt', 'w') as f:
            for i in range(0, self.tableWidget.rowCount()):
                if self.tableWidget.item(i, 1):
                    f.write(self.tableWidget.item(i, 1).text().rstrip())
                    f.write('\n')
        self.savings_calc()

        for currentQTableWidgetItem in self.tableWidget.selectedItems():
            # # TODO limit second column to integer input
            # savings = 0
            # while 1 > savings or 1000000 < savings:
            # 	try:
            # 		savings = int(currentQTableWidgetItem.text())
            # 	except ValueError:
            # 		# Remember, print is a function in 3.x
            # 		print("That wasn't an integer :(\n")
            # 		# App.statusBar().showMessage('splat')

            # print(currentQTableWidgetItem.row(),
            #       currentQTableWidgetItem.column(),
            #       currentQTableWidgetItem.text())
            # Add row when last row has some text

            # BUG crashes if text is entered in project description before
            # savings is entered because savings cell is null so it doesn't
            # have a text property
            with open('Savings.txt') as f:
                savingsText = f.readlines()
            with open('Projects.txt') as f:
                projectsText = f.readlines()
            # print(len(savingsText))
            # print(self.tableWidget.rowCount())
            if max(len(savingsText), len(projectsText)) >= \
                    self.tableWidget.rowCount():
                # if currentQTableWidgetItem.row() ==
                # self.tableWidget.rowCount() - 1:
                # if currentQTableWidgetItem.text():
                rowPosition = self.tableWidget.rowCount()
                self.tableWidget.insertRow(rowPosition)
                # print(currentQTableWidgetItem.row(),
                #       currentQTableWidgetItem.column(),
                #       currentQTableWidgetItem.text())
                # print(self.tableWidget.rowCount())
                # self.tableWidget.setItem(rowPosition , 0,
                #                          QtGui.QTableWidgetItem("text1"))
                # sumTotal = 0
                # for i in range(0, self.tableWidget.rowCount()-1):
                #     if self.tableWidget.item(i, 1):
                #         sumTotal = int(self.tableWidget.item(i, 1).text()) + sumTotal
                # print('{:,}'.format(sumTotal))
                # self.labelSavings.setText('Total Savings: ' +
                #                           '{:,}'.format(sumTotal))

    def dbl_click(self, event):
        # TODO add input box for new goal value
        goal_input = input('Enter the new goal: ')
        print('new goal: ', goal_input)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
    # unittest.main()
    # TODO package app
    # TODO 2 learn how to store classes and functions in separate .py files
