import QtQuick 2.13
import QtQuick.Controls 1.4
import QtQuick.Layouts 1.4
import Backend 1.0
// source: https://github.com/fcollonval/matplotlib_qtquick_playground/tree/master/backend/backend_qtquick5
// TextEdit{
//     id: _text
//     text: "<font color=\"#0000FF\">Blue</font> <font color=\"#FF0000\">Red</font>"
//     textFormat: TextEdit.RichText
// }
Item{
    id: _root
    FigureCanvas {
        id: _mplView
        objectName : "figure"
        anchors.fill: parent        
    }
}