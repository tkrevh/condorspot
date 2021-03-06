/*
 @description:
 this script was written for condorspot.com
 @version:   0.1
 @uri:   http://condorspot.com/
 @copyright: Gregor Ambrozic
 @author:    Gregor Ambrozic
 @author-uri:    http://insane.si
 */

var REPOSITORY = "/media/condorspot/";
var mandatory = "- field IS mandatory";
var notmandatory = "- field IS NOT mandatory";
var viletters = "- valid input: aA-zZ (only letters!)";
var vinumbers = "- valid input: 0-9 (only numbers!)";

var formFields = [
    ["firstname", "- your real firstname<br/>" + mandatory + "<br/>" + viletters],
    ["lastname", "- your real lastname<br/>" + mandatory + "<br/>" + viletters],
    ["gender", "- pick your gender<br/>" + mandatory],
    ["email", "- your email<br/>" + mandatory + "<br/>- email will be used to login"],
    ["password", "- password<br/>" + mandatory + "<br/>- password will be used to login"],
    ["retypepassword", "- retype password<br/>" + mandatory],
    ["country", "- pick your country<br/>" + mandatory],
    ["rlh", "- hours you have flown in real-life gliders<br/>" + notmandatory + "<br/>" + vinumbers],
    ["rlk", "- sum of distance you have flown in real-life gliders (km)<br/>" + notmandatory + "<br/>" + vinumbers],
    ["cn", "- competition number for cup<br/>" + mandatory + "<br/>- will be used for evaluating your flights"],
    ["rn", "- registration number for cup<br/>" + mandatory + "<br/>- will be used for evaluating your flights"],
    ["tz", "- UTC timezone used during races<br/>" + mandatory + "<br/>- can be changed only on non race days<br/>"],
    ["filter", "- type into field terms you wish to keep displayed in results table<br>- works on position, cn, name, country, glider<br>- for multiple terms filter use +"]
];

var buttons = [
    ["register",""],
    ["change",""],
    ["clear",""],
    ["browse",""],
    ["upload",""]
];

function $import(path) {
    var scripts = $("script");
    for (var i = 0; i < scripts.length; i++) {
        if (!scripts[i].src.match(path)) {
            document.write("<" + "script src=\"" + path + "\" type=\"text/javascript\"></" + "script>");
            break;
        }
    }
}

if (document.getElementById("fsr")) $import(REPOSITORY + "js/jquery.uitablefilter.js");
if (document.getElementById("fsr")) $import(REPOSITORY + "js/jquery.tablesorter.js");
if (document.getElementById("fst")) $import("http://maps.google.com/maps?file=api&amp;v=2&amp;sensor=false&amp;key=ABQIAAAABysKYn2hZOMLHboGbWO6fRRaKkdOTKtWusOT9IlHAYrXtGiTSRTxfYHWKcSbEsNtzTtJdZ7HBb818w");


function setCookie(key, value, expiredays) {
    var exdate = new Date();
    exdate.setTime(exdate.getTime() + (1000 * 60 * 60 * 24 * expiredays));
    document.cookie = key + "=" + escape(value) + ((expiredays === null) ? "" : ";expires=" + exdate.toGMTString());
}

function getCookie(key) {
    if (document.cookie.length > 0) {
        var start = document.cookie.indexOf(key + "=");
        if (start != -1) {
            start = start + key.length + 1;
            var end = document.cookie.indexOf(";", start);
            if (end == -1) {
                end = document.cookie.length;
            }
            return unescape(document.cookie.substring(start, end));
        }
    }
    return undefined;
}


function appendFieldsetEvents() {
    $("#lt").bind("click", function() {
        if ($("#st").css("display") == "block") {
            $("#fst").css("height", "26px");
            $("#st").css("display", "none");
            $("#lt").css("background", "url('" + REPOSITORY + "img/tasc.gif') no-repeat  0 12px");
        } else {
            $("#fst").css("height", "auto");
            $("#st").css("display", "block");
            $("#st").css("height", "510px");
            $("#lt").css("background", "url('" + REPOSITORY + "img/tdesc.gif') no-repeat  0 10px");
        }
    });
    $("#lr").bind("click", function() {
        if ($("#sr").css("display") == "block") {
            $("#fsr").css("height", "26px");
            $("#sr").css("display", "none");
            $("#lr").css("background", "url('" + REPOSITORY + "img/tasc.gif') no-repeat  0 12px");
        } else {
            $("#fsr").css("height", "auto");
            $("#sr").css("display", "block");
            $("#lr").css("background", "url('" + REPOSITORY + "img/tdesc.gif') no-repeat  0 10px");
        }
    });

    $("#ll").bind("click", function() {
        if ($("#sl").css("display") == "block") {
            $("#fsl").css("height", "26px");
            $("#sl").css("display", "none");
            $("#ll").css("background", "url('" + REPOSITORY + "img/tasc.gif') no-repeat  0 12px");
        } else {
            $("#fsl").css("height", "auto");
            $("#sl").css("display", "block");
            $("#ll").css("background", "url('" + REPOSITORY + "img/tdesc.gif') no-repeat  0 10px");
        }
    });

    var x = document.URL.toLowerCase().match(/x\d{1,3}/);
    if (x) {
        while (x.length < 4) x += 0;
        x = x.toString().split("");
        //only shows task, hide results
        if (x[1] == 1)$("#lt").click();//task, default (in css) hidden
        if (x[2] == 0)$("#lr").click();//results, default (in css) visible
        if (x[3] == 1)$("#ll").click();//task, default (in css) hidden
    }
}

function appendTableEvents() {
    var rows = $("tr.t0, tr.t1");
    for (var i = 0; i < rows.length; i++) {
        $(rows[i]).bind("click", function(e) {
            $(".taskpic").remove();
            var pic = $("<div/>").attr("id", "pic-" + i).append("<img src=\"_delete/flight_01.png\"/>");
            pic.bind("click", function(e) {
                $(".taskpic").remove();
            });
            $(pic).addClass("taskpic");
            $(this).after(pic);
        });
    }
}

function appendFieldEvents() {
    for (var u = 0; u < formFields.length; u++) {
        function at(i) {
            //FORM FIELDS FOCUS
            $("#" + formFields[i][0]).bind("focus", function(e) {
                var info = $("<div/>").attr("id", this.id + "info");
                $(info).addClass("forminfo").css("opacity", "0.1").css("margin-top", -15 - (15 * formFields[i][1].split("<br/>").length)).html(formFields[i][1]);
                $(this).after(info);

                $(info).animate({
                    opacity: "1.0"
                }, 200);
            });
            //FORM FIELDS BLUR
            $("#" + formFields[i][0]).bind("blur", function(e) {
                $("#" + this.id + "info").remove();
            });

            //FILTER FIELD KEYUP
            if (formFields[i][0].toLowerCase() == "filter") {
                $("#" + formFields[i][0]).bind("keyup", function() {
                    $.uiTableFilter($("#results"), this.value);
                });
            }
        }

        at(u);
    }
}

function appendButtonEvents() {
    for (var i = 0; i < buttons.length; i++) {
        //DISABLE SUBMIT BUTTONS AFTER CLICK

        //BUTTON CLEAR CLICK
        if (buttons[i][0].toLowerCase() == "clear") {
            $("#" + buttons[i][0]).bind("click", function() {
                $("form")[0].reset();
            });
        }
    }
}

function appendTaskPreviewButtons() {
    var img = $("#taskimg");
    if (!getCookie("cs_cookie_taskmap")) {
        setCookie("cs_cookie_taskmap", "img", 5);
    }
    //IMAGE EVENTS
    $("#pmvi").bind("click", function(e) {
        $("#pmvc").empty();
        $("#pmvc").append("<img id=" + img.attr('id') + " src=" + img.attr('src') + "></img>");
        $("#pmvgm").removeClass("pmvsc");
        $("#pmvi").addClass("pmvsc");
        setCookie("cs_cookie_taskmap", "img", 5);
    });
    //GOOGLEMAPS EVENTS
    $("#pmvgm").bind("click", function(e) {
        $("#pmvgm").addClass("pmvsc");
        $("#pmvi").removeClass("pmvsc");
        initializeGoogleMaps();
        setCookie("cs_cookie_taskmap", "gm", 5);
    });
    if (getCookie("cs_cookie_taskmap") == "img")
        $("#pmvi").click();
    else
        $("#pmvgm").click();
}

function initializeGoogleMaps() {
    if (GBrowserIsCompatible()) {
        var map = new GMap2(document.getElementById("pmvc"));

        var polyOptions = {geodesic:true};
        var values = $("#pmvv").attr("value").split(";").reverse();
        var points = [];
        for (var i = 0; i < values.length; i++) {
            points.push(new GLatLng(values[i].split(",")[0], values[i].split(",")[1]));
            if (i > 0 && i < values.length - 1)map.addOverlay(new GPolygon(doCircle(values[i].split(",")[0], values[i].split(",")[1], 0.5), '#ff0000', 1, 1, '#ff0000', 0.25, {clickable:false}));

            //START SECTOR
            if (i == 0) {
                map.addOverlay(new GPolygon(
                        doHalfCircle(values[i].split(",")[0],
                                values[i].split(",")[1],
                                3,
                                getHeading(
                                        values[i].split(",")[0], values[i].split(",")[1],
                                        values[i + 1].split(",")[0], values[i + 1].split(",")[1])
                                ),
                        '#ff0000', 1, 1, '#ff0000', 0.25, {clickable:false}));
            }
            //FINISH SECTOR
            if (i == values.length - 1) {
                map.addOverlay(new GPolygon(
                        doHalfCircle(values[i].split(",")[0],
                                values[i].split(",")[1],
                                1,
                                getHeading(
                                        values[i].split(",")[0], values[i].split(",")[1],
                                        values[i - 1].split(",")[0], values[i - 1].split(",")[1])
                                ),
                        '#ff0000', 1, 1, '#ff0000', 0.25, {clickable:false}));
            }
        }
        var polyline = new GPolyline(points, "#ff0000", 2, 0.6, polyOptions);

        map.setCenter(new GLatLng(values[0].split(",")[0], values[0].split(",")[1]), 10);
        map.setUIToDefault();
        map.setMapType(G_PHYSICAL_MAP);
        map.addOverlay(polyline);
    }
    doCircle(46.6136093140, 7.6777777672, 0.5);
}

function doCircle(lat, lon, radius) {
    var points = [];
    with (Math) {
        radius = radius / 6378.8;	// radians
        lat = (PI / 180) * lat; // radians
        lon = (PI / 180) * lon; // radians
        for (var a = 0; a < 361; a = a + 3) {
            var tc = (PI / 180) * a;
            var y = asin(sin(lat) * cos(radius) + cos(lat) * sin(radius) * cos(tc));
            var dlng = atan2(sin(tc) * sin(radius) * cos(lat), cos(radius) - sin(lat) * sin(y));
            var x = ((lon - dlng + PI) % (2 * PI)) - PI ; // MOD function
            var point = new GLatLng(parseFloat(y * (180 / PI)), parseFloat(x * (180 / PI)));
            points.push(point);
        }
        return points;
    }
}

function doHalfCircle(lat, lon, radius, heading) {
    var points = [];
    with (Math) {
        radius = radius / 6378.8;	// radians (kilometers)
        lat = (PI / 180) * lat; // radians
        lon = (PI / 180) * lon; // radians
        for (var a = heading - 90; a < heading + 90; a = a + 3) {
            points.push(getPoint(lat, lon, radius, a));
        }
        points.push(getPoint(lat, lon, radius, (heading - 90)));
        return points;
    }
}

function getPoint(lat, lon, radius, a) {
    with (Math) {
        var tc = (PI / 180) * a;
        var y = asin(sin(lat) * cos(radius) + cos(lat) * sin(radius) * cos(tc));
        var dlng = atan2(sin(tc) * sin(radius) * cos(lat), cos(radius) - sin(lat) * sin(y));
        var x = ((lon - dlng + PI) % (2 * PI)) - PI ; // MOD function
        return new GLatLng(parseFloat(y * (180 / PI)), parseFloat(x * (180 / PI)));
    }
}

function getHeading(lat1, lon1, lat2, lon2) {
    with (Math) {
        radians = Math.atan2(lat2 - lat1, lon2 - lon1);
        return radians * 180 / Math.PI + 90;
    }
}

function setResultsTable() {
    $.tablesorter.defaults.widgets = ['zebra'];
    $("#results").tablesorter({
        cssHeader: "header",
        cssAsc: "asc",
        cssDesc: "desc",
        widgetZebra: {css: ["t0","t1"]}
    });
}
function setServersListTable() {
    var table = $("<table/>").addClass("tw").addClass("twb");
    //$.getJSON("http://condorspot.com/x/servers/", function(servers) {
    $.getJSON("/x/servers/", function(servers) {
        if (servers[0].name) {
            for (var i = 0; i < servers.length; i++) {

                var servername = "";
                if (servers[i].status == "Race in Progress") {
                    servername = "<em class=\"red\">&nbsp;" + servers[i].name + "</em>";
                } else if (servers[i].status == "Waiting for Race Start") {
                    servername = "<em class=\"darkorange\">&nbsp;" + servers[i].name + "</em>";
                } else if (servers[i].status == "Joining Enabled") {
                    servername = "<a href=\"" + servers[i].url + "\" class=\"green\" title=\"Click to join server\">" + servers[i].name + "</a>";
                } else {
                    servername = "&nbsp;";
                }

                var serverstatus = "";
                if (servers[i].status == "Race in Progress") {
                    serverstatus = "<em class=\"red\">&nbsp;" + servers[i].status + "</em>";
                } else if (servers[i].status == "Waiting for Race Start") {
                    serverstatus = "<em class=\"darkorange\">&nbsp;" + servers[i].status + "</em>";
                } else if (servers[i].status == "Joining Enabled") {
                    serverstatus = "<a href=\"" + servers[i].url + "\" class=\"green\" title=\"Click to join server\">" + servers[i].status + "</a>";
                } else {
                    serverstatus = "&nbsp;";
                }

                var serverjoin = "";
                if (servers[i].status == "Race in Progress") {
                    serverjoin = "<em class=\"red\">&nbsp;Can't join server</em>";
                } else if (servers[i].status == "Waiting for Race Start") {
                    serverjoin = "<em class=\"darkorange\">&nbsp;Can't join server</em>";
                } else if (servers[i].status == "Joining Enabled") {
                    serverjoin = "<a href=\"" + servers[i].url + "\" class=\"green\" title=\"Click to join server\">Join server</a>";
                } else {
                    serverjoin = "&nbsp;";
                }
                table.append("<tr class=\"t" + ((i + 1) % 2) + "\">" +
                             "<td>" + servername + "</td>" +
                             "<td>" + servers[i].scenery + "</td>" +
                             "<td>" + serverstatus + "</td>" +
                             "<td>" + servers[i].players + "</td>" +
                             "<td>" + servers[i].uptime + "</td>" +
                             "<td>" + servers[i].flown + "/" + servers[i].distance + "</td>" +
                             "<td>" + servers[i].leader + "</td>" +
                             "<td>" + serverjoin + "</td>" +
                             "</tr>");
            }
            thead = $("<thead/>").append("<tr class=\"t0\"><td style=\"width:140px;\"><strong>Server</strong></td><td><strong>Scenery</strong></td><td><strong>Status</strong></td><td><strong>Players</strong></td><td><strong>Uptime</strong></td><td><strong>Flown</strong></td><td><strong>Leader</strong></td><td style=\"width:100px;\">&nbsp;<strong>Join</strong></td></tr>");
            table.append(thead)
            $("#dss").empty();
            $("#dss").append(table)
        } else {
            $("#dss").empty();
            $("#dss").append("<p>" + servers + "</p>");
        }
    });
}

function setServerListTask() {
    var cid = document.URL.split("/")[5];
    //$.getJSON("http://condorspot.com/x/servers/" + cid + "/", function(servers) {
    $.getJSON("/x/servers/" + cid + "/", function(servers) {
        if (servers[0].name) {
            for (var i = 0; i < servers.length; i++) {

                var servername = "";
                if (servers[i].status == "Race in Progress") {
                    servername = "<em class=\"red\">&nbsp;" + servers[i].name + "</em>";
                } else if (servers[i].status == "Waiting for Race Start") {
                    servername = "<em class=\"darkorange\">&nbsp;" + servers[i].name + "</em>";
                } else if (servers[i].status == "Joining Enabled") {
                    servername = "<a href=\"" + servers[i].url + "\" class=\"green\" title=\"Click to join server\">" + servers[i].name + "</a>";
                } else {
                    servername = "&nbsp;";
                }

                var serverstatus = "";
                if (servers[i].status == "Race in Progress") {
                    serverstatus = "<em class=\"red\">&nbsp;" + servers[i].status + "</em>";
                } else if (servers[i].status == "Waiting for Race Start") {
                    serverstatus = "<em class=\"darkorange\">&nbsp;" + servers[i].status + "</em>";
                } else if (servers[i].status == "Joining Enabled") {
                    serverstatus = "<a href=\"" + servers[i].url + "\" class=\"green\" title=\"Click to join server\">" + servers[i].status + "</a>";
                } else {
                    serverstatus = "&nbsp;";
                }

                var serverjoin = "";
                if (servers[i].status == "Race in Progress") {
                    serverjoin = "<em class=\"red\">&nbsp;Can't join server</em>";
                } else if (servers[i].status == "Waiting for Race Start") {
                    serverjoin = "<em class=\"darkorange\">&nbsp;Can't join server</em>";
                } else if (servers[i].status == "Joining Enabled") {
                    serverjoin = "<a href=\"" + servers[i].url + "\" class=\"green\" title=\"Click to join server\">Join server</a>";
                } else {
                    serverjoin = "&nbsp;";
                }
                $("#std li:last-child").remove();
                $("#std").append("<li><span>Server</span>&nbsp;</li>" +
                                 "<li><span>Name</span>" + servername + "</li>" +
                                 "<li><span>Uptime</span>&nbsp;" + servers[i].uptime + "</li>" +
                                 "<li><span>Players</span>&nbsp;" + servers[i].players + " / " + servers[i].leader + "</li>" +
                                 "<li><span>Flown</span>&nbsp;" + servers[i].flown + "/" + servers[i].distance + "</li>" +
                                 "<li><span>Status</span>" + serverstatus + "</li>" +
                                 "<li><span>Join</span>" + serverjoin + "</li>");
            }
        } else {
            $("#std li:last-child").remove();
            $("#std").append("<li><span>Server</span>" + servers + "</li>");
        }
    });
}

$(document).ready(function() {
    if ($("#dss"))setServersListTable();
    if ($("#st")) {
        setServerListTask();
        appendTaskPreviewButtons();
    }
    if ($("#results")) {
        setResultsTable();
        //appendTableEvents();
    }
    appendFieldsetEvents();
    appendFieldEvents();
    appendButtonEvents();
});