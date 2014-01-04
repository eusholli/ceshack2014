var fs = require('fs');
var mqtt = require('mqtt');
var dns = require('dns');
var mqtt_client = undefined;
var io = require('socket.io').listen(3000);
io.set('log level', 1);
var httpget = require('http-get');

var device_list = {};

var topics_to_sockets = {};
var sockets_to_topics = {};
var socket_clients = {};
var socket_user_count = {};

// var MQTT_SERVER = 'pubsub.public.unity.tfoundry.com';
var MQTT_SERVER = 'pubsub.ceshack2014.att.io';

function connect_to_broker(address) {
  mqtt_client = mqtt.createClient(address.port, address.name);

  mqtt_client.subscribe('devices/sensor/#');

  mqtt_client.on('message', function(topic, message) {
    console.log(topic+' : '+message);
    // console.log('\n\n');
    var found=false;
    if(topic.indexOf("devices/sensor") >= 0) {
      device_state = {};
      device_state.name = topic;
      device_state.state = message;
      // console.log('device '+JSON.stringify(device_state));
      device_list[topic] = device_state;
      io.sockets.emit('presence', device_state);
    } else if(topic.indexOf("action/response") > 0) {
      // console.log(message);
      message = JSON.parse(message);
      // image_key = message.filename.split('/')[2];
    	if(message.requested_action.indexOf('take_picture') == 0) {

        var device_name = message.device;
        var request_id = message.request_id;
        var timestamp = message.timestamp;

        var topic = device_name + '/action/response/' + request_id + '/' + timestamp;

        if(message.status == "success") {

          var url = message.url;
          var filename = '/tmp/' + url.substring(url.lastIndexOf("/") + 1);
          httpget.get(message.url, filename, function(error, result) {
            if(error) {
              console.error(error);
            } else {
              fs.readFile(filename, function (err, original_data) {
                if (err) {
                  console.error("Error reading file: " + filename);
                } else {
                  var base64Image = original_data.toString('base64');
                  console.log("sending take_picture_image");
                  socket_clients[request_id].emit('take_picture_image', JSON.stringify({"timestamp" : timestamp, "image" :base64Image}));
                  fs.unlink(filename, function (err) {
                    if (err) throw err;
                    console.log('successfully deleted: ' + filename);
                  });
                }
              });
            }
          });
        }
      }
      send_to_sockets(topic, 'actionresponse', message);
      topics_to_sockets_delete(socket_clients[request_id], topic);
   
    } else if(topic.search(/.*\/readings$/) == 0) {
        var message_to_send = {};
        message_to_send['topic'] = topic;
        message_to_send['payload'] = message;
        send_to_sockets(topic, 'devicedata', message_to_send);

        var parsedMessage = JSON.parse(message);
        if(parsedMessage.sensor_type == "door_sensor") {
          var url = parsedMessage.image;
          var filename = '/tmp/' + url.substring(url.lastIndexOf("/") + 1);
          httpget.get(url, filename, function(error, result) {
            if(error) {
              console.error(error);
            } else {
              fs.readFile(filename, function (err, original_data) {
                if (err) {
                  console.error("Error reading file: " + filename);
                } else {
                  var base64Image = original_data.toString('base64');
                  console.log("sending take_picture_image");
                  send_to_sockets('take_picture_image', 'take_picture_image', {"timestamp" : "motion", "image" :base64Image});
                  fs.unlink(filename, function (err) {
                    if (err) throw err;
                    console.log('successfully deleted: ' + filename);
                  });
                }
              });
            }
          });
        }

    } else if(topic.search(/^SOTA\/.*\/response$/) == 0) {
      console.log("topic %s : %s ", topic, message);

       var topic = device_name + '/action/response/' + request_id + '/' + timestamp;
       send_to_sockets(topic, 'upgraderesponse', message);
       topics_to_sockets_delete(socket_clients[request_id], topic);
    } else {
      //console.log('ELSE topic = '+topic+'; message = '+message);
    }
    
  }); //end client on message
} //end connect to borker

dns.resolveSrv('_m2mcontroller._tcp.ceshack.unity.tfoundry.com', function (err, addresses) {
  var address = undefined;
  if(err) {
      // TODO remove this when we get APN for 3GPP
      // use public
      console.log("using public MQTT_SERVER: " + MQTT_SERVER);
      address = {name : MQTT_SERVER, port : 1883};
  } else {
    var lowest_priority = 0;
    for(var i in addresses) {
      address = addresses[i];

      //console.log(address);

      var name = address.name;
      var port = address.port;
      var priority = address.priority;
      var weight = address.weight;

      //implement weight check
      if (priority <= lowest_priority) {
        break;
      }
    }
  }
  connect_to_broker(address);
}); //end dns.resolvSrv


function socket_user_add(socket) {
  if (!(socket.id in socket_clients)) {
    socket_clients[socket.id] = socket;
    socket_user_count[socket.id] = 1;
  } else {
    socket_user_count[socket.id]++;
  }
  console.log("socket: %s users %s", socket.id, socket_user_count[socket.id]);      
}

function socket_user_delete(socket_id) {
  if(socket_user_count == 1) { // last user being removed
    if (socket_id in socket_clients) {
      delete socket_clients[socket_id];
    } else {
      socket_user_count[socket.id]--;
    }
    console.log("socket: %s users %s", socket.id, socket_user_count[socket_id]);      
  } 
}

function topics_to_sockets_add(socket, topic) {

  var socket_id = socket.id;

  if(topics_to_sockets[topic] == undefined || topics_to_sockets[topic] == null) {
    topics_to_sockets[topic] = new Array();
  }

  var index = topics_to_sockets[topic].indexOf(socket_id);
  if (index == -1) {
    topics_to_sockets[topic].push(socket_id);
  } else {
    console.log("socket: " + socket.id + " already subscribed to " + topic);      
  }

  socket_user_add(socket);
}

function topics_to_sockets_delete(socket, topic) {

  var socket_id = socket.id;

  if((topics_to_sockets[topic] == undefined) || (topics_to_sockets[topic] == null)) {
    console.error("should not be unsubscribing when socket: " + socket_id + " not subscribed");
    return;
  }

  var index = topics_to_sockets[topic].indexOf(socket_id);
  if(index != -1) {
    topics_to_sockets[topic].splice(index,1);
  } else {
    console.error("socket: " + socket.id + " not subscribed to " + topic);
  }

  if(topics_to_sockets[topic].length == 0) {
    console.log("empty list delete topics_to_sockets for: " + topic);
    delete topics_to_sockets[topic];
  } 
  socket_user_delete(socket_id);
}

function sockets_to_topics_add(socket, topic) {

  var socket_id = socket.id;

  if(sockets_to_topics[socket_id] == undefined || sockets_to_topics[socket_id] == null) {
    sockets_to_topics[socket_id] = new Array();
  }

  var index = sockets_to_topics[socket_id].indexOf(topic);
  if (index == -1) {
    sockets_to_topics[socket_id].push(topic);
  } else {
    console.log("topic: " + topic + " already listened to by " + socket.id);      
  }

  socket_user_add(socket);
}

function sockets_to_topics_delete(socket, topic) {

  var socket_id = socket.id;

  if((sockets_to_topics[socket_id] == undefined) || (sockets_to_topics[socket_id] == null)) {
    console.error("should not be unsubscribing when socket: " + socket_id + " not subscribed");
    return;
  }

  var index = sockets_to_topics[socket_id].indexOf(topic);
  if(index != -1) {
    sockets_to_topics[socket_id].splice(index,1);
  } else {
    console.error("topic: " + topic + " not listened to by " + socket.id);
  }

  if(sockets_to_topics[socket_id].length == 0) {
    console.log("empty list delete sockets_to_topics for: " + socket_id);
    delete sockets_to_topics[socket_id];
  } 

  socket_user_delete(socket_id);
}

function subscribe(socket, topic) {
  console.log('socket id %s, subscribe %s ' , socket.id, topic);
  // var socket_id = socket.id;
 
  topics_to_sockets_add(socket, topic);

  if(topics_to_sockets[topic].length == 1) {
     mqtt_client.subscribe(topic);
    console.log("mqtt subscribe: " + topic);
  }

  sockets_to_topics_add(socket, topic);

  console.log("topics_to_sockets");
  console.log(topics_to_sockets);
  console.log("sockets_to_topics");
  console.log(sockets_to_topics);
};//end subscribe

function unsubscribe(socket, topic) {
  console.log('socket id %s, unsubscribe %s' , socket.id, topic);

  topics_to_sockets_delete(socket, topic);
  sockets_to_topics_delete(socket, topic);

if((topics_to_sockets[topic] == undefined) || (topics_to_sockets[topic] == null)) {
    console.log("mqtt unsubscribing topic: " + topic);
    mqtt_client.unsubscribe(topic);
    delete topics_to_sockets[topic];
  } 

  console.log("topics_to_sockets");
  console.log(topics_to_sockets);
  console.log("sockets_to_topics");
  console.log(sockets_to_topics);
}; //end unsubscribe

function send_to_sockets(topic, socket_event, message_to_send) {
  var listening_socket_ids = topics_to_sockets[topic];
  if(listening_socket_ids != undefined && listening_socket_ids != null) {
    for(var i=0; i<listening_socket_ids.length; i++) {
      //console.log("\t"+socks[i]);
       socket_clients[listening_socket_ids[i]].emit(socket_event, JSON.stringify(message_to_send));
    }
  }
} // end send_to_sockets

io.sockets.on('connection', function (socket) {
  var socket_id = socket.id;
  console.log(socket.handshake.headers.host);
  socket.on('devicelist', function (data) {
    //console.log(device_list.length);
    console.log('devicelist ' + JSON.stringify(data));
    for(var d in device_list) {
      //io.sockets.emit('presence', device_list[d]);
      socket.emit('presence', device_list[d]);
    }
  }); //socket on subscribe

  socket.on('upgrade', function (data) {
    console.log(data);
    console.log('socket id = '+socket.id);

    var command = {}
    command.action = data.action
    command.command = data.command
    command.component = data.component
    command.request_id = socket.id;
    command.timestamp = new Date().getTime();

    var SOTA_PREFIX="SOTA/";
    var request_topic = SOTA_PREFIX + data.device_name+'/request';
    var response_topic = SOTA_PREFIX + data.device_name+'/response';
    mqtt_client.subscribe(response_topic);

    topics_to_sockets_add(socket, response_topic + '/' + command.request_id + '/' + command.timestamp);

    console.log('sending upgrade request to '+SOTA_REQUEST+' data '+data_json);
    mqtt_client.publish(request_topic, JSON.stringify(command));
  });
  socket.on('subscribe_to_take_picture_image', function () {
    topics_to_sockets_add(socket, 'take_picture_image');
   });
  socket.on('unsubscribe_to_take_picture_image', function () {
    topics_to_sockets_delete(socket, "take_picture_image");
  }); 

  socket.on('subscribe', function (data) {
    var topic = data.topic;
    subscribe(socket, topic);
   });//end subscribe

  socket.on('unsubscribe', function (data) {
    var topic = data.topic;
    unsubscribe(socket, topic);
  }); //end unsubscribe

  socket.on('disconnected', function() {
    console.log('socket %s disconnected', socket.id);
    var socket_id = socket.id;
    if((sockets_to_topics[socket_id] == undefined) || (sockets_to_topics[socket_id] == null)) {
      console.log("socket not subscribed to any topics: " + socket_id);
      return;
    }
    var topics = sockets_to_topics[socket_id];
    for(var i in topics) {
      unsubscribe(socket, topics[i]);
    }
  });

  socket.on('action_request', function(data) {
    console.log('action_request' + JSON.stringify(data));
    // action_request(data);

    var command = {}
    command.request_id = socket.id;
    command.timestamp = new Date().getTime();

    for(var key in data) {
      command[key] = data[key];
    }

    var response_topic = data.device_name+'/action/response';
    mqtt_client.subscribe(response_topic);

    topics_to_sockets_add(socket, response_topic + '/' + command.request_id + '/' + command.timestamp);

    var request_topic = data.device_name+'/action/request';
    mqtt_client.publish(request_topic, JSON.stringify(command));
  });
    
}); //end io.sockets.on connection
