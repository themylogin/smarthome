function drawLine(x1, y1, x2, y2){
    if(y1 < y2)
    {
        var pom = y1;
        y1 = y2;
        y2 = pom;
        pom = x1;
        x1 = x2;
        x2 = pom;
    }

    var a = Math.abs(x1 - x2);
    var b = Math.abs(y1 - y2);
    var c;
    var sx = (x1 + x2) / 2;
    var sy = (y1 + y2) / 2;
    var width = Math.sqrt(a * a + b * b);
    var x = sx - width / 2;
    var y = sy;

    a = width / 2;

    c = Math.abs(sx - x);

    b = Math.sqrt(Math.abs(x1 - x) * Math.abs(x1 - x) + Math.abs(y1 - y) * Math.abs(y1 - y));

    var cosb = (b * b - a * a - c * c) / (2 * a * c);
    var rad = Math.acos(cosb);
    var deg = (rad * 180)/Math.PI

    htmlns = "http://www.w3.org/1999/xhtml";
    div = document.createElementNS(htmlns, "div");
    div.setAttribute('style','width: ' + width + 'px; height: 0px; -moz-transform: rotate(' + deg + 'deg); -webkit-transform: rotate(' + deg + 'deg); position: absolute; top:' + y + 'px; left:' + x + 'px;');   
    return div;
}

//

function Backend(location)
{
    this.location = location;
}

Backend.prototype.infiniteWebsocket = function(url, onmessage)
{
    url = "ws://" + this.location + url;
    function connect()
    {
        var socket = new WebSocket(url);
        socket.onmessage = function(msg){
            var response = JSON.parse(msg.data);
            onmessage(response);
        }
        socket.onclose = function(){
            setTimeout(connect, 1000);
        };
    }
    connect();
}

Backend.prototype.post = function(url, data)
{
    $.ajax({
        "method": "POST",
        "url": "http://" + this.location + url,
        "data": JSON.stringify(data)
    });
}

Backend.prototype.control = function(command, args)
{
    this.post("/control", {"command": command, "args": args});
}

Backend.prototype.setProperty = function(object, property, value)
{
    this.control("set_property", {"object": object,
                                  "property": property,
                                  "value": value});
}

Backend.prototype.connectPad = function(src_object, src_pad, dst_object, dst_pad)
{
    this.control("connect_pad", {"src_object": src_object,
                                 "src_pad": src_pad,
                                 "dst_object": dst_object,
                                 "dst_pad": dst_pad});
}

Backend.prototype.disconnectPad = function(src_object, src_pad, dst_object, dst_pad)
{
    this.control("disconnect_pad", {"src_object": src_object,
                                    "src_pad": src_pad,
                                     "dst_object": dst_object,
                                     "dst_pad": dst_pad});
}

//

function ObjectPainter(defaultPainter)
{
    this.painters = {};
    this.defaultPainter = defaultPainter;
}

ObjectPainter.prototype.registerPainter = function(className, painter)
{
    this.painters[className] = painters;
}

ObjectPainter.prototype.paint = function($object, objectData)
{
    var painter = this.painters[objectData["inspection"]["class"]];
    if (painter === undefined)
    {
        painter = this.defaultPainter;
    }

    painter($object, objectData);
}

//

function defaultPainter($object, objectData)
{
    if (typeof defaultPainter.zIndex == "undefined")
    {
        defaultPainter.zIndex = 0;
    }

    if (!$object.hasClass("GenericObject"))
    {
        $object.addClass("GenericObject");
        $object.html("");

        $object.on("click", function(event){
            $object.css("zIndex", ++defaultPainter.zIndex);
        });
        $object.on("contextmenu", function(event){
            $object.css("zIndex", 0);
            event.preventDefault();
        });

        $object.append("<h1>" + $object.data("name") + "</h1>");

        var $propertiesTable = $("<table/>").addClass("properties");
        objectData["inspection"]["properties"].sort();
        $.each(objectData["inspection"]["properties"], function(i, propertyName){
            var $tr = $("<tr/>").addClass("property").addClass(propertyName).data("name", propertyName);
            $tr.append($("<td/>").addClass("name").text(propertyName));
            $tr.append($("<td/>").addClass("currentValue"));
            $tr.append($("<td/>").addClass("newValue").append($("<input/>").attr("type", "text")));
            $propertiesTable.append($tr);
        })
        $object.append($propertiesTable);

        $.each(objectData["inspection"]["input_pads"], function(pad, desc){
            var $pad = $("<div/>").addClass("pad input").addClass("interface-" + desc["interface"]).addClass("name-" + pad);
            $pad.data("name", pad);
            $pad.data("interface", desc["interface"]);
            $pad.text(pad);
            $object.append($pad);
        });
        $.each(objectData["inspection"]["output_pads"], function(pad, desc){
            var $pad = $("<div/>").addClass("pad output").addClass("interface-" + desc["interface"]).addClass("name-" + pad);
            $pad.data("name", pad);
            $pad.data("interface", desc["interface"]);
            $pad.text(pad);
            $object.append($pad);
        });

        $object.append($("<ul/>").addClass("errors").on("click contextmenu", "li h6", function(){
            $(this).next().toggle();
        }));
    }

    $.each(objectData["properties_values"], function(name, value){
        var $tr = $object.find(".properties .property." + name);

        $tr.find(".currentValue").data("value", value).html(JSON.stringify(value));

        if (value === true || value === false)
        {
            $tr.find(".currentValue").addClass("boolean");
        }
        else
        {
            $tr.find(".currentValue").removeClass("boolean");
        }
    });

    if ($.isEmptyObject(objectData["errors"]))
    {
        $object.removeClass("hasErrors");
        $object.find(".errors").html("");
    }
    else
    {
        $object.addClass("hasErrors");
        $object.find(".errors").html("");
        $.each(objectData["errors"], function(k ,v){
            $object.find(".errors").append($("<li/>").append($("<h6/>").text(k)).append($("<pre/>").text(v)));
        });
    }
}

//

function UserData(backend)
{
    this.backend = backend;

    try
    {
        // this.data = JSON.parse(localStorage.userData);
        this.data = database;
    }
    catch (err)
    {
        this.data = {};
    }
}

UserData.prototype.get = function()
{
    var data = this.data;
    $.each(arguments, function(i, path){
        data = data[path];
        if (data === undefined)
        {
            return false;
        }
    });
    return data;
}

UserData.prototype.set = function()
{
    var data = this.data;
    var args = arguments;
    $.each(arguments, function(i, path){
        if (i < args.length - 2)
        {
            if (data[path] === undefined)
            {
                data[path] = {};
            }
            data = data[path];
        }
        else
        {
            data[args[args.length - 2]] = args[args.length - 1];
            return false;
        }
    });

    // localStorage.userData = JSON.stringify(this.data);
    this.backend.post("/write_frontend_database", this.data);
}

//

$(function(){
    var backend = new Backend(document.location.host);
    var userData = new UserData(backend);

    $("body").on("click", ".pad-connection", function(){
        backend.disconnectPad($(this).data("srcObject"),
                              $(this).data("srcPad"),
                              $(this).data("dstObject"),
                              $(this).data("dstPad"));
    });

    $("body").on("click", ".GenericObject .properties .currentValue.boolean", function(){
        backend.setProperty($(this).parents(".smarthome-object").data("name"),
                            $(this).parents(".property").data("name"),
                            !$(this).data("value"));
    });
    $("body").on("keydown", ".GenericObject .properties .newValue input", function(event){
        if (event.keyCode == 13)
        {
            backend.setProperty($(this).parents(".smarthome-object").data("name"),
                                $(this).parents(".property").data("name"),
                                JSON.parse($(this).val()));
            event.preventDefault();
        }
    });

    var painter = new ObjectPainter(defaultPainter);
    backend.infiniteWebsocket("/objects", function(objects){
        $(".pad-connection").remove();

        $.each(objects, function(objectName, objectData){
            var domObjectId = "object_" + objectName;
            var $object = $("#" + domObjectId);
            if ($object.length == 0)
            {
                var $object = $("<div/>");
                $object.attr("id", domObjectId);
                $object.data("name", objectName);
                $object.addClass("smarthome-object");
                $object.addClass(objectData["inspection"]["class"]);

                var position;
                if (position = userData.get("objects", objectName, "position"))
                {
                    $object.css("top", position["x"]);
                    $object.css("left", position["y"]);
                }

                $object.appendTo("body");

                $object.draggable({
                    stop: function()
                    {
                        userData.set("objects", objectName, "position", {
                            "x": $object.css("top"),
                            "y": $object.css("left")
                        });
                    }
                });
            }

            painter.paint($object, objectData);

            $object.find(".pad.output:not(.draggable)").addClass("draggable").each(function(){
                $(this).draggable({
                    revert: true,
                    revertDuration: 0,
                });
            });
            $object.find(".pad.input:not(.droppable)").addClass("droppable").each(function(){
                $(this).droppable({
                    accept: ".pad.output.interface-" + $(this).data("interface"),
                    drop: function(event, ui)
                    {
                        var $that = $(this);
                        setTimeout(function(){
                            backend.connectPad($(ui.draggable).parents(".smarthome-object").data("name"),
                                               $(ui.draggable).data("name"),
                                               $that.parents(".smarthome-object").data("name"),
                                               $that.data("name"));
                        }, 100);
                    },
                });
            });
        });

        $.each(objects, function(objectName, objectData){
            $.each(objectData["incoming_pad_connections"], function(pad, connections){
                $.each(connections, function(i, connection){
                    var $from = $("#object_" + connection[0]).find(".pad.name-" + connection[1]);
                    var $to = $("#object_" + objectName).find(".pad.name-" + pad);
                    var $connection = $(drawLine($from.offset().left + $from.outerWidth() / 2,
                                                 $from.offset().top + $from.outerHeight() / 2,
                                                 $to.offset().left + $to.outerWidth() / 2,
                                                 $to.offset().top + $to.outerHeight() / 2));
                    $connection.addClass("pad-connection");
                    $connection.data("srcObject", connection[0]);
                    $connection.data("srcPad", connection[1]);
                    $connection.data("dstObject", objectName);
                    $connection.data("dstPad", pad);
                    $connection.appendTo("body");
                });
            });
        });
    });
});
