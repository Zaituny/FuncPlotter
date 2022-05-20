import pytest
import FuncPlotter

from sympy import symbols
from PyQt5 import QtGui, QtCore


@pytest.fixture
def app(qtbot):
	test_func_plotter_app = FuncPlotter.Window()
	qtbot.addWidget(test_func_plotter_app)

	return test_func_plotter_app

def test_empty_input(app, qtbot):
	app.maxBox.setValue(1)
	qtbot.mouseClick(app.plotButton, QtCore.Qt.LeftButton)
	assert app.obtainFunctionPoints() == ([],[],False,True,0)

def test_input_equal_x(app, qtbot):
	app.functionBox.setText("x")
	app.maxBox.setValue(1)
	qtbot.mouseClick(app.plotButton, QtCore.Qt.LeftButton)
	x_values, y_values, validInput, validRange, function = app.obtainFunctionPoints()
	assert len(x_values) == 2051
	assert len(y_values) == 2051
	assert validInput == True
	assert validRange == True
	assert x_values == y_values

def test_input_equal_xplusy(app, qtbot):
	app.functionBox.setText("x+y")
	app.maxBox.setValue(1)
	qtbot.mouseClick(app.plotButton, QtCore.Qt.LeftButton)
	x_values, y_values, validInput, validRange, function = app.obtainFunctionPoints()
	assert len(x_values) == 101
	assert len(y_values) == 101
	assert validInput == True
	assert validRange == True

def test_inputSanitizing_with_empty_input(app, qtbot):
	app.maxBox.setValue(1)
	qtbot.mouseClick(app.plotButton, QtCore.Qt.LeftButton)
	assert app.inputSanitizing() == (0,False)

def test_inputSanitizing_with_input_x(app, qtbot):
	app.functionBox.setText("x")
	app.maxBox.setValue(1)
	qtbot.mouseClick(app.plotButton, QtCore.Qt.LeftButton)
	x = symbols('x')
	assert app.inputSanitizing() == (x,True)


def test_invalid_range(app, qtbot):
	app.functionBox.setText("x")
	app.maxBox.setValue(-1)
	qtbot.mouseClick(app.plotButton, QtCore.Qt.LeftButton)
	x = symbols('x')
	assert app.inputSanitizing() == (x, True)
	assert app.obtainFunctionPoints() == ([],[],True, False, x)

def test_invalid_input(app, qtbot):
	app.functionBox.setText("sin(x")
	qtbot.mouseClick(app.plotButton, QtCore.Qt.LeftButton)
	assert app.inputSanitizing() == (0, False)
	assert app.obtainFunctionPoints() == ([],[],False, True, 0)
