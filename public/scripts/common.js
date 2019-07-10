var concertNumber;
var showKingFM;
var showSmile;

function getConfig() {
    var today = new Date();
    if (window.XMLHttpRequest) {
        xhttp = new XMLHttpRequest();
    } else {    // IE 5/6
        xhttp = new ActiveXObject("Microsoft.XMLHTTP");
    }
    xhttp.open("GET", "content_config.xml", false);
    xhttp.send();
    xmlDoc = xhttp.responseXML;

    var concerts = xmlDoc.getElementsByTagName("concert");
    for (i = 0; i < concerts.length; i++) {
        var begin = new Date(concerts[i].getAttribute("begin"));
        var end = new Date(concerts[i].getAttribute("end"));
        if (today >= begin && today <= end) {
            concertNumber = concerts[i].getAttribute("number");
        }
    }
    showKingFM = xmlDoc.getElementsByTagName("radio")[0].getAttribute("show");
    showSmile = "0";
    var smileEnd = new Date(xmlDoc.getElementsByTagName("smile")[0].getAttribute("end"));
    if (today <= smileEnd) {
        showSmile = xmlDoc.getElementsByTagName("smile")[0].getAttribute("show");
    }
}
