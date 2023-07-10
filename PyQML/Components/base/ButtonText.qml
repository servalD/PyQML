import QtQuick 2.12
import QtQuick.Controls 1.4

Rectangle{
    id: _root

    property var text: ""
    property bool checked: false
    property bool checkEnabled: false
    property var textSize: 5
    property var textColor: "white"
    property var textColorH: "yellow"
    signal clicked()

    width: _rootText.width 
    height: _rootText.height
    color:"#00000000"

    Text{
        id: _rootText
        font.pointSize: _root.textSize
        color: _rootMouse.containsMouse ? _root.textColorH : _root.checked ? _root.textColorH : _root.textColor
        text: _root.text
    }
    MouseArea {
        id: _rootMouse
        anchors.fill: parent
        hoverEnabled: true
        onClicked:{ 
            if (_root.checkEnabled){
                _root.checked = !_root.checked
            }
            _root.clicked()
        }
    }
}