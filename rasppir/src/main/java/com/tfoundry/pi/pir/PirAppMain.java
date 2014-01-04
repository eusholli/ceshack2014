package com.tfoundry.pi.pir;

import java.io.IOException;

import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken;
import org.eclipse.paho.client.mqttv3.MqttCallback;
import org.eclipse.paho.client.mqttv3.MqttClient;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.eclipse.paho.client.mqttv3.persist.MemoryPersistence;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.basho.riak.client.RiakRetryFailedException;
import com.basho.riak.client.raw.pbc.PBClientAdapter;
import com.basho.riak.pbc.RiakClient;
import com.pi4j.io.gpio.GpioController;
import com.pi4j.io.gpio.GpioFactory;
import com.pi4j.io.gpio.GpioPinDigitalInput;
import com.pi4j.io.gpio.GpioPinDigitalOutput;
import com.pi4j.io.gpio.PinPullResistance;
import com.pi4j.io.gpio.PinState;
import com.pi4j.io.gpio.RaspiPin;

public class PirAppMain {
	private static Logger log = LoggerFactory.getLogger(PirAppMain.class);

	final static GpioController gpio = GpioFactory.getInstance();
	static MqttClient mqtt = null;
	static PBClientAdapter adapter = null;
	static String host = "ceshack-pir.ceshack.unity.tfoundry.com";
	static String riak = "db.ceshack2014.att.io";
	static String flip = "";

	public static void main(String[] args) throws InterruptedException,
			IOException, RiakRetryFailedException, MqttException {
		try {
			
			log.info("Host is : {} , {}", java.net.InetAddress.getLocalHost().getHostName(),
					com.pi4j.system.NetworkInfo.getFQDN());
			
			for(String arg : args) {
				if("flip".equalsIgnoreCase(arg)) flip = "-hf ";
			}
			
			adapter = new PBClientAdapter(new RiakClient(riak));
						
			mqtt = connectToMQTT();

			GpioPinDigitalOutput distTrig = gpio.provisionDigitalOutputPin(
					RaspiPin.GPIO_05, // PIN NUMBER
					"Distance Trigger", // PIN FRIENDLY NAME (optional)
					PinState.LOW); // PIN STARTUP STATE (optional)
			GpioPinDigitalOutput distTrig2 = gpio.provisionDigitalOutputPin(
					RaspiPin.GPIO_00, // PIN NUMBER
					"Distance Trigger2", // PIN FRIENDLY NAME (optional)
					PinState.LOW); // PIN STARTUP STATE (optional)
			GpioPinDigitalOutput distTrig3 = gpio.provisionDigitalOutputPin(
					RaspiPin.GPIO_06, // PIN NUMBER
					"Distance Trigger3", // PIN FRIENDLY NAME (optional)
					PinState.LOW); // PIN STARTUP STATE (optional)

			GpioPinDigitalInput echo = gpio.provisionDigitalInputPin(
					RaspiPin.GPIO_04, // PIN NUMBER
					"Distance Echo", // PIN FRIENDLY NAME (optional)
					PinPullResistance.OFF); // PIN RESISTANCE (optional)
			
			//echo.addListener(new GpioUsageEventListener(null, null));
			
			GpioPinDigitalInput echo2 = gpio.provisionDigitalInputPin(
					RaspiPin.GPIO_02, // PIN NUMBER
					"Distance Echo2", // PIN FRIENDLY NAME (optional)
					PinPullResistance.OFF); // PIN RESISTANCE (optional)
			
			//echo2.addListener(new GpioUsageEventListener(null, null));
			
			GpioPinDigitalInput echo3 = gpio.provisionDigitalInputPin(
					RaspiPin.GPIO_03, // PIN NUMBER
					"Distance Echo3", // PIN FRIENDLY NAME (optional)
					PinPullResistance.OFF); // PIN RESISTANCE (optional)
			
			//echo3.addListener(new GpioUsageEventListener(null, null));

			GpioPinDigitalInput pir = gpio.provisionDigitalInputPin(
					RaspiPin.GPIO_01, // PIN NUMBER
					"PIR", // PIN FRIENDLY NAME (optional)
					PinPullResistance.OFF); // PIN RESISTANCE (optional)
			
			GpioPinDigitalOutput[] trigs = {distTrig, distTrig2, distTrig3};
			GpioPinDigitalInput[] echos = {echo, echo2, echo3};

			pir.addListener(new GpioSensorEventListener(trigs, echos));

			while (true) {
				// System.out.println("Monitoring ---");
				Thread.sleep(1);
			}
		} catch (MqttException e) {
			log.error("Could not connect to MQTT broker",e);
		}

		finally {
			gpio.shutdown();
			if( adapter != null ) adapter.shutdown();
			if( mqtt != null ) {
				mqtt.disconnect();
				mqtt.close();
			}
		}
	}
	
	private static MqttClient connectToMQTT() throws MqttException {
		MqttClient mqtt = null;
		
		MemoryPersistence persistence = new MemoryPersistence();
//		MqttDefaultFilePersistence persistence = new MqttDefaultFilePersistence(
//                dir);
    	//mqtt = new MqttClient("tcp://pubsub.public.unity.tfoundry.com:1883","WingmanClient",persistence);
    	mqtt = new MqttClient("tcp://pubsub.ceshack2014.att.io:1883","PirCtrl",persistence);
    	mqtt.connect();
    	
    	mqtt.setCallback( new MqttCallback(){

			public void connectionLost(Throwable cause) {
				log.debug("PirCtrl","connectionLost : {}",cause.getLocalizedMessage());
				cause.printStackTrace();
				//Log.d("WingMan", );
			}

			public void messageArrived(String topic, final MqttMessage message)
					throws Exception {
				log.debug("PirCtrl","Got message = {} in topic - {}",message,topic);
			}

			public void deliveryComplete(IMqttDeliveryToken token) {
				log.debug("PirCtrl","deliveryComplete() : {}",token);
			}} );
    	mqtt.subscribe("temppi.att.slyfox.tfoundry.com/#");
    	return mqtt;
    }
}
