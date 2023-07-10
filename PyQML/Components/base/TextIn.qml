import QtQuick 2.12
import QtQuick.Controls 2.12

Rectangle{
    id: _root
    radius: 4
    width: _rootText.width + 4
    height: _rootText.height

    property alias text: _rootText.text
    property var textColor: "white"
    property var maxWidth
    signal validate(var text)
    TextInput{
        id: _rootText
        anchors.horizontalCenter: _root.horizontalCenter
        width: _root.maxWidth
        color: _root.textColor
        clip: true
        selectByMouse: true
        onAccepted: _root.validate(text)
    }
}