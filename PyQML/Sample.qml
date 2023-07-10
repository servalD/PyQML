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
}
