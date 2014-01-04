package com.tfoundry.pi.pir;

import java.io.DataInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Date;

import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttPersistenceException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.basho.riak.client.IRiakObject;
import com.basho.riak.client.builders.RiakObjectBuilder;
import com.basho.riak.client.cap.UnresolvedConflictException;
import com.basho.riak.client.convert.ConversionException;

import com.pi4j.io.gpio.GpioPinDigitalInput;
import com.pi4j.io.gpio.GpioPinDigitalOutput;
import com.pi4j.io.gpio.PinState;
import com.pi4j.io.gpio.event.GpioPinDigitalStateChangeEvent;
import com.pi4j.io.gpio.event.GpioPinListenerDigital;

public class GpioSensorEventListener implements GpioPinListenerDigital {
	private GpioPinDigitalOutput[] distSensors;
	private GpioPinDigitalInput[] distEchos;
	private long timer;
	private long counter = 0;
	private static String[] sensorName = {"high","mid","low"};
	private static Logger log = LoggerFactory.getLogger(GpioSensorEventListener.class);
	
    SimpleDateFormat ft = new SimpleDateFormat ("yyyy-MM-dd HH:mm:ss zzz");

	public GpioSensorEventListener(GpioPinDigitalOutput[] output,
			GpioPinDigitalInput[] input) {
		distSensors = output;
		distEchos = input;
	}

	// @Override
	public void handleGpioPinDigitalStateChangeEvent(
			GpioPinDigitalStateChangeEvent event) {
		// display pin state on console
		log.trace(" --> GPIO PIN STATE CHANGE: {} = {}", event.getPin(),
				event.getState());
		if (event.getPin().getPin().getAddress() == 2) {
			if (event.getState().isHigh() && timer == 0 ) {
				log.trace("Starting timer 1 ...");
				timer = System.nanoTime();
			} else {
				long delta = (System.nanoTime() - timer)/1000;
				System.out.println("Delta 1 = " + delta);
				System.out.println("Len 1 = " + delta / 58.0);
				timer =  0;
			}
		}
		if (event.getPin().getPin().getAddress() == 4) {
			if (event.getState().isHigh() && timer == 0 ) {
				log.trace("Starting timer 2 ...");
				timer = System.nanoTime();
			} else {
				long delta = (System.nanoTime() - timer)/1000;
				System.out.println("Delta 2 = " + delta);
				System.out.println("Len 2 = " + delta / 58.0);
				timer =  0;
			}
		}
		else if (event.getPin().getPin().getAddress() == 1) {
			if (event.getState().isHigh()) {
				//distSensor.pulse(1, PinState.HIGH);
				int i = 0;
				
				Date now = new Date( );
				StringBuilder message = new StringBuilder();
				
				message.append('{');
				message.append("\"timestamp\": \"").append(ft.format(now)).append("\", ");
				message.append("\"sensor_type\": \"door_sensor\", ");
				message.append("\"counter\": \"").append(++counter).append("\", ");
				
				for( GpioPinDigitalOutput distSensor : distSensors ) {
					System.out.println("Trig - " + distSensor+ " Echo - "+distEchos[i]+" = "+distEchos[i].getState());
					distSensor.setState(PinState.HIGH);
					try {
						Thread.sleep(0, 10000);
					} catch (InterruptedException ignore) {
					}
					distSensor.setState(PinState.LOW);
					long diff = blockingPulse(distEchos[i]);
					message.append('\"').append(sensorName[i]).append("\": \"").append(diff).append("\", ");
					log.info("Delta = {}", diff);
					log.info("Len = {}", diff/ 58.0);
					i++;
				}
				String photo = "image_"+now.getTime()+".jpeg";
				
				if( capturePhoto( photo ) ) {
					try { Thread.sleep(3000); } catch(InterruptedException ignore){}
					File file = new File("/tmp/"+photo);
				    byte[] fileData = new byte[(int) file.length()];
				    DataInputStream dis;
					try {
						dis = new DataInputStream(new FileInputStream(file));
						dis.readFully(fileData);
					    dis.close();
					    
					    IRiakObject obj = RiakObjectBuilder.newBuilder(PirAppMain.host, photo).withContentType("image/jpeg").withValue(fileData).build();
					    PirAppMain.adapter.store(obj);
					    
					} catch (FileNotFoundException e) {
						e.printStackTrace();
					} catch (IOException e) {
						e.printStackTrace();
					} catch (UnresolvedConflictException e) {
						e.printStackTrace();
					} catch (ConversionException e) {
						e.printStackTrace();
					}
					
					 file.delete();
				}
				
				message.append("\"image\": \"").append("http://").append(PirAppMain.riak)
					.append(":8098/buckets/").append(PirAppMain.host).append("/keys/")
					.append(photo).append("\"");
				message.append('}');
				log.info("Publishing to mqtt -> {}", message.toString());
				try {
					PirAppMain.mqtt.publish(PirAppMain.host+"/readings",message.toString().getBytes(),0,false);
				} catch (MqttPersistenceException e) {
					log.error("Failed to publish.",e);
				} catch (MqttException e) {
					log.error("Failed to publish.",e);
				}
			}
		}
	}

	private long blockingPulse(GpioPinDigitalInput distEcho) {
		long diff = 0;
		
		long max = 500; //0.5 sec

		long start = 0;
		long guard = System.currentTimeMillis();
		log.debug("Echo - {}", distEcho);
		while (distEcho.isLow()) {
			start = System.nanoTime();
			if( (System.currentTimeMillis()-guard) > max ) return 0;
		}
		log.debug("Start - {}", start);
		guard = System.currentTimeMillis();
		while (distEcho.isHigh()) {
			if( (System.currentTimeMillis()-guard) > max ) return 0;
		}
		diff = (System.nanoTime() - start)/1000;

		return diff;
	}

	public static boolean capturePhoto(String name) {
		boolean ok = false;
		try {
			// Execute a command without arguments
			//String command = "raspistill -w 640 -h 480 -o /tmp/"+name;
			String command = "raspistill "+PirAppMain.flip+"-t 1 -w 640 -h 480 -o /tmp/"+name;
			Process child = Runtime.getRuntime().exec(command);
			log.info("Start = {}", System.currentTimeMillis());
			//child.waitFor(5, TimeUnit.SECONDS); //Java 8
			child.waitFor();
			log.info("End   = {}", System.currentTimeMillis());
			log.info("Camera called - {} pic -> /tmp/{}",name,name);
			ok = true;

		} catch (IOException e) {
			log.error("Camera could not start");
		} catch (InterruptedException e) {
			log.error("Camera could not start");
		}
		return ok;
	}
}
