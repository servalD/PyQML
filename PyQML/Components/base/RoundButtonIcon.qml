import QtQuick 2.12
import QtQuick.Controls 2.12

Rectangle{
            id: _root
            width: radius*2
            height: radius*2
            color: "#332222"
            border.width: 1
            border.color: _rootMouse.containsMouse ? _rootMouse.pressed ? "yellow" : "white" : checked ? "white" : "#00000000"

            signal clicked()
            signal checkChanged(bool stats)
            property var source: ""
            property bool checked: false
            property int myMarg: 6
            property bool checkEnabled: false

            Image{ 
                id: _rootIm
                anchors.centerIn: _root
                width: _root.width - _root.myMarg
                height: _root.height - _root.myMarg
                source: _root.source
            }
            MouseArea {
                id: _rootMouse
                anchors.fill: _root
                hoverEnabled: true
                onClicked:{ 
                    if (_root.checkEnabled){
                        _root.checked = !_root.checked
                         _root.checkChanged(_root.checked)
                    }
                    _root.clicked()
                }
            }
        }