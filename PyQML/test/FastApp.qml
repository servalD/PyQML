import QtQuick 2.12
import QtQuick.Window 2.12
import QtQuick.Controls 2.12

ApplicationWindow {
    id: _root
    objectName: "_root"
    title: pyData.title
    width: pyData.width
    height: pyData.height
    onClosing: dumpPydata()
    function dumpPydata(){
        pyData.title = title
        pyData.width = width
        pyData.height = height
    }
    MouseArea{
        id: _m
        anchors.fill: parent
        hoverEnabled: true
        onClicked: { test.Dre(test.tic+1); console.log(test.tic)}
    }
    Connections {
        target: test
        onOnDre: {
            console.log(arg)
        }
    }
    Text{
        id: _txt
        // function getTxt(txt){_txt.text = txt; console.log("ok "+txt[0])}
        anchors.fill: parent
        text: test.tic
        color: _m.pressed ? "grey" : "lightblue"
    }
}
