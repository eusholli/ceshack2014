var dns = require('dns');
var m2x = require('m2x');
var mqtt = require('mqtt');
var mqtt_client = undefined;
// var MQTT_SERVER = 'pubsub.public.unity.tfoundry.com';
var MQTT_SERVER = 'pubsub.ceshack2014.att.io';

var API_KEY = "07baf689333ab1a0d228a87368c7b16b";  //m2x master key
var m2x_client = new m2x(API_KEY);

var m2x_feed_ids = {
  "ceshack-pir" : "c282edf50dbf0d26c0573ed80755a205",
  "ceshack-pi00" : "9d5d59a2e0297abea1b333592c4f0dd3",
  "ceshack-pi01" : "54ced6e4e0788f41168eb167b16b8d8a",
  "ceshack-pi02" : "80e79d294233359b1a8ebc969735a82f",
  "ceshack-pi03" : "459cb7b4d388fac70b926e23d4cc51db",
  "ceshack-pi04" : "6a3fab1850ab258ab8b15d82ee10f3ab",
  "ceshack-pi05" : "4ab4d9a315ea74cca41d9ecb34acc94b",
  "ceshack-pi06" : "28d0ed6a2e50477bfe309d4c9dbb5925",
  "ceshack-pi07" : "a4340c8e78f62af36a36fe9a9ec47f26",
  "ceshack-pi08" : "ccea2b192a0385f9b8b3d8a18a7e4987",
  "ceshack-pi09" : "9edc619c3a451a996991ba4bfa2184cf"
}

var readings = [
  "lux",
  "CO",
  "Alcohol",
  "temperature",
  "altitude",
  "pressure",
  "humidity",
  "low",
  "mid",
  "high",
  "image"
];

// STUPID HACK since cannot rename streams in M2X despite being able to edit!!!
var readings_to_m2x_names = {
  "lux" : "tsl2561-light",
  "CO" : "mq7-co",
  "Alcohol" : "mq3-alcohol",
  "temperature" : "temperature",
  "altitude" : "bmp085-altitude",
  "pressure" : "bmp085-pressure",
  "humidity" : "dht22-humidity",
  "low" : "low",
  "mid" : "mid",
  "high" : "high",
  "image" : "image"
};

function connect_to_broker(address) {
  mqtt_client = mqtt.createClient(address.port, address.name);

  // mqtt_client.subscribe('#/readings');
  mqtt_client.subscribe('#');

  mqtt_client.on('message', function(topic, message) {
    console.log(topic+' : '+message);
    // console.log('\n\n');

    if(topic.search(/.*\/readings$/) != 0) {
      return;
    }

    var fqdn = topic.split('/')[0];
    var device_name = fqdn.split('.')[0];

    var feed_id = m2x_feed_ids[device_name];
    if(!feed_id) {
      console.error("Device not configured in M2X: " + device_name);
      return;
    }

    var parsedData = JSON.parse(message);
    console.log(parsedData);

    for (var i=0; i < readings.length; i++) {
      var reading = readings[i];
      if((parsedData[reading] != undefined) && (parsedData[reading] != null)){
        var new_value = parsedData[reading];
        var m2x_stream_name = readings_to_m2x_names[reading];
        m2x_client.feeds.updateStream(feed_id, m2x_stream_name, { value: new_value }, function(what_is_this, data, error, response){
          console.log("%s %s %s %s", feed_id, m2x_stream_name, new_value, error.body);
        });
      }
    }

    if(parsedData["magnetometer"]){
      var x = parsedData["magnetometer"]["x"];
      var y = parsedData["magnetometer"]["y"];
      var z = parsedData["magnetometer"]["z"];
      m2x_client.feeds.updateStream(feed_id, "lsm303-magnetometer-x", { value: x });
      m2x_client.feeds.updateStream(feed_id, "lsm303-magnetometer-y", { value: y });
      m2x_client.feeds.updateStream(feed_id, "lsm303-magnetometer-z", { value: z });
    }
    
    if(parsedData["accelerometer"]){
      var x = parsedData["accelerometer"]["x"];
      var y = parsedData["accelerometer"]["y"];
      var z = parsedData["accelerometer"]["z"];
      m2x_client.feeds.updateStream(feed_id, "lsm303-accelerometer-x", { value: x });
      m2x_client.feeds.updateStream(feed_id, "lsm303-accelerometer-y", { value: y });
      m2x_client.feeds.updateStream(feed_id, "lsm303-accelerometer-z", { value: z });
     }
   });
}
    
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
  