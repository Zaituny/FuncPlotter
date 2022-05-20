# importing various libraries
import sys

from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QDialog, QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QLineEdit, QLabel, QMessageBox, QDoubleSpinBox

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import random
from sympy import * 
import numpy as np

import pytest


# === Window Class ===
class Window(QDialog):
    """
    this class contains all the widgets 
    and functions necessary to run the application
    """      
    # constructor
    def __init__(self, parent=None):
        """
        Class Constructor
        """
        super(Window, self).__init__(parent)
        
        #set the window title
        self.setWindowTitle("FuncPlotter")

        # a figure instance to plot on
        self.figure = plt.figure()
  
        # this is the Canvas Widget that
        # displays the 'figure'it takes the
        # 'figure' instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)
  
        # this is the Navigation widget
        # it takes the Canvas widget and a parent object
        self.toolbar = NavigationToolbar(self.canvas, self)
  
        # button for plotting
        self.plotButton = QPushButton('Plot')

        #button for viewing the help message
        self.helpButton = QPushButton('Help')

        #range labels
        self.minLabel = QLabel("start of range")
        self.maxLabel = QLabel("end of range")

        #range spin box
        self.minBox = QDoubleSpinBox()
        self.maxBox = QDoubleSpinBox()

        #setting the spinbox range from negative infinte to infinte
        self.minBox.setMinimum(float('-inf'))
        self.minBox.setMaximum(float('inf'))

        self.maxBox.setMinimum(float('-inf'))
        self.maxBox.setMaximum(float('inf'))

        #the function textBox and label
        self.functionBox = QLineEdit()
        self.label = QLabel("Function") 

        #a spacer to adjust the spaces between widgets
        self.spacer = QLabel("")
          
        # adding action to the button
        self.plotButton.clicked.connect(self.plot)
        self.helpButton.clicked.connect(self.helpDialog)
  
        # defining layouts
        mainLayout = QVBoxLayout()
        functionLayout = QHBoxLayout()
        rangeLayout = QHBoxLayout()
        toolbarLayout = QHBoxLayout()
        plotLayout = QHBoxLayout()

        #adding widgets to layouts
        functionLayout.addWidget(self.label)
        functionLayout.addWidget(self.functionBox)
        
        rangeLayout.addWidget(self.minLabel)
        rangeLayout.addWidget(self.minBox)

        rangeLayout.addWidget(self.spacer)

        rangeLayout.addWidget(self.maxLabel)
        rangeLayout.addWidget(self.maxBox)

        toolbarLayout.addWidget(self.toolbar)
        toolbarLayout.addWidget(self.helpButton)

        plotLayout.addWidget(self.spacer)
        plotLayout.addWidget(self.plotButton)
        plotLayout.addWidget(self.spacer)


        # adding layouts to the main layout
        mainLayout.addLayout(toolbarLayout)
          
        # adding canvas to the layout
        mainLayout.addWidget(self.canvas)
          
        mainLayout.addLayout(functionLayout)
        mainLayout.addLayout(rangeLayout)
        mainLayout.addLayout(plotLayout)

        # setting main layout to the main window
        self.setLayout(mainLayout)
  
    # === Error messages function ===
    def myMessage(self, msgText, msgTitle = "Invalid Input", msgIcon = QMessageBox.Critical):
        """
        used to generate messages to explain usages
        and incorrect inputs
        """
        msg = QMessageBox()
        msg.setWindowTitle(msgTitle)
        msg.setText(msgText)
        msg.setIcon(msgIcon)
        msg.exec_()

    # === input sanitizer function
    def inputSanitizing(self):
        """
        used to sanitize the input to filter out invalid input 
        """
        functionSympified = 0 
        unsanitizedString = self.functionBox.text()
        validInput = True
        #checks whether the input is only letters
        if unsanitizedString.isalpha() and len(unsanitizedString) > 1:
            self.myMessage("Please, input at least 1 letter or at most 2 letters separated by an operator")
            validInput = False

        #checks if the input is an equation or not
        if "=" in unsanitizedString:
            self.myMessage("Invalid Input, input must be a function not an equation")
            validInput = False

        #checks whether the input is empty or not
        if len(unsanitizedString) == 0:
            self.myMessage("Input can't be empty")
            validInput = False

        #otherwise proceed
        else:
            try:
                #try to convert input sting to a sympy expression
                functionSympified = sympify(unsanitizedString)
                #stores the variables in the expression
                numberOfSymbols = functionSympified.free_symbols

                #checks if input contains more than 2 variables 
                if len(numberOfSymbols) > 2:
                    self.myMessage("functions can't be drawn on a 2D plane")
                    validInput = False
            except Exception:
                #catches exceptions if sympy failed to convert the string 
                self.myMessage("Input may contain a typo or unsupported operations\n make sure all brackets are closed")
                validInput = False    
        return functionSympified, validInput

    # === grabbing the points for plotting ===
    def obtainFunctionPoints(self):
        """
        this function takes the sanitized input
        and the sympy expression and calculates the points
        to be drawn by substitution
        the function calculates 2051 equally spaced points
        within range for single variable
        and 101 equally spaced points within range
        for 2 variables
        WARNING: single variable functions
        are much slower but more accurate
        """
        x_values = []
        y_values = []
        function, validInput = self.inputSanitizing()
        validRange = True
        start = self.minBox.value()
        end = self.maxBox.value()

        #checks if minimum range is less than maximum range
        if start > end:
            self.myMessage("Invalid Range")
            validRange = False

        #checks if input and range are valid to proceed to calculate points
        if validInput and validRange:
            #handling single variable equations
            if len(function.free_symbols) < 2:
                #handling inputs containing only constants
                if len(function.free_symbols) == 0:
                    x_values = [self.minBox.value(), self.maxBox.value()]

                    #handling known constant
                    if self.functionBox.text() != "pi" and self.functionBox.text() != "E": 
                        y_values = [float(self.functionBox.text()), float(self.functionBox.text())]

                    #handling pi
                    elif self.functionBox.text() == "pi":
                        y_values = [np.pi, np.pi]

                    #handling euler's constant
                    elif self.functionBox.text() == "E":
                        y_values = [np.e, np.e]

                #if input is not a constant then calculate point arrays 
                else:
                    for i in range(0, 2051):
                        x_values.append(start + ((end - start)/2051)*i )

                        #handling complex numbers
                        if "I" not in str(function.subs(list(function.free_symbols)[0], x_values[i]).evalf()):
                            y_values.append(function.subs(list(function.free_symbols)[0], x_values[i]).evalf())
                        #if result contains complex numbers then add (not a number) in their respective y value
                        else:
                            y_values.append(np.nan)

            #handling multivariable input, treated as an equation = 0 (x+y=0) and not f(x,y)
            if len(function.free_symbols) == 2:
                #loop to obtain values
                for i in range(0, 101):
                    #obtain 100 equally spaced values in specified range
                    new_x = start + ((end - start)/100)*i
                    x_values.append(new_x)

                    #store roots of the equation
                    roots = solve(function.subs(list(function.free_symbols)[0], x_values[i]).evalf(), list(function.free_symbols)[1])
                    
                    #check if input fails the vertical line test which means a single x values has 2 possible solutions
                    if len(roots) >= 2:
                        self.myMessage("this is not a function, check if the input passes the vertical line test")
                        validInput = False
                        break

                    else:
                        #check if roots has complex results and ignoring them
                        if "I" in str(roots[0]):
                            y_values.append(np.nan)

                        else: 
                            y_values.append(roots[0])

        return x_values, y_values, validInput, validRange, function           

    # plotting function
    def plot(self):
        x_values, y_values, validInput, validRange, function = self.obtainFunctionPoints()

        if validInput and validRange:
            #checking if input contained symbols to be sorted
            if len(function.free_symbols) != 0:
                symbols = list(function.free_symbols)
                str_symbol = []

                for symbol in symbols:
                    str_symbol.append(str(symbol))

                #sorting symbols list for consistancy
                str_symbol.sort()


            # clearing old figure
            self.figure.clear()

            # create a centered axis
            ax = self.figure.add_subplot(111)
            ax.spines['left'].set_position('zero')
            ax.spines['bottom'].set_position('zero')
            ax.spines['right'].set_color('none')
            ax.spines['top'].set_color('none')

            ax.xaxis.set_ticks_position('bottom')
            ax.yaxis.set_ticks_position('left')

            #setting the axis range to -10 to 10 on both axis if the chosen range is within this range
            if self.minBox.value() > -10 or self.maxBox.value() < 10:
                ax.set_xlim([-10, 10])
                ax.set_ylim([-10, 10])

            #handeling different scenarios for axis labels
            if len(list(function.free_symbols)) == 2:
                ax.set_xlabel(str_symbol[0], loc='right')
                ax.set_ylabel(str_symbol[1], loc='top', rotation = 0)
            
            elif len(list(function.free_symbols)) == 1:
                ax.set_xlabel(str_symbol[0], loc='right')
                ax.set_ylabel('y', loc = 'top', rotation = 0)
            
            else:
                ax.set_xlabel('x', loc='right')
                ax.set_ylabel('y', loc = 'top', rotation = 0)


            # plot data
            ax.plot(x_values, y_values)
  
            # refresh canvas
            self.canvas.draw()

    #function to be called on help button press
    def helpDialog(self):
        self.myMessage("Supported operands\n"+
            "1. + and -\n"+
            "2. * and /\n"+
            "3. ^\n"+
            "Trignometric Functions\n"+
            "Examples:\n x\nx^2\nsin(x) where x is in radians\n"+
            "x+y\n"+
            "a+b\n"+
            "Note: in case of multivariable input the input is going to be treated as an equation = 0 for example\n"+
            "x+y as x+y=0\n"+
            "Invalid Input Examples\n"+
            "asdgasdg\n"+
            "empty inputs\n"+
            "sin(x\n"+
            "sinx", "Help Dialog", QMessageBox.Information)
  
# driver code
if __name__ == '__main__':
      
    # creating apyqt5 application
    app = QApplication(sys.argv)
  
    #setting app icon
    app_icon = QtGui.QIcon()
    app_icon.addFile('Icon16x16.jpg', QtCore.QSize(16,16))
    app_icon.addFile('Icon24x24.jpg', QtCore.QSize(24,24))
    app_icon.addFile('Icon32x32.jpg', QtCore.QSize(32,32))
    app_icon.addFile('Icon48x48.jpg', QtCore.QSize(48,48))
    app_icon.addFile('Icon256x256.jpg', QtCore.QSize(256,256))
    app.setWindowIcon(app_icon)

    # creating a window object
    main = Window()
      
    # showing the window
    main.show()
  
    # loop
    sys.exit(app.exec_())