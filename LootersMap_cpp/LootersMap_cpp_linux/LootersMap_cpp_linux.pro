TEMPLATE = app
CONFIG += console c++11
CONFIG -= app_bundle
CONFIG -= qt

INCLUDEPATH += /usr/local/include/opencv4

LIBS += `pkg-config opencv4 --libs`
QMAKE_LFLAGS += -pthread

SOURCES += main.cpp
