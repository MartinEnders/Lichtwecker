#!/usr/bin/python3

import cherrypy
import time
import pigpio
import os
import datetime
import json
import schedule
import threading

LED_PIN = 24
SSR_PIN = 23
TESTING = True



def sched_test():
    print("--- TEST ---")

class WeckerWeb(object):
    def __init__(self):
        # Wecker parameter
        self.weckzeit = None          
        self.wecker_startzeit = None
        self.wecken_p = False
        
        self.dimm_dauer = 8 #sekunden
        self.nachleuchten = 1 #sekunden

        self.config_file = os.path.abspath(os.getcwd()) + "/config.json"
        self.daemon_thread = None
        self.daemon_run = True
        
        # PWM Configuration
        self.pwm_start = 1000
        self.pwm_ende  = 2550

        self.pi = pigpio.pi()
        # setup pin as an output
        self.pi.set_mode(LED_PIN, pigpio.OUTPUT)
        # pi set frequency
        self.pi.set_PWM_frequency(LED_PIN, 1200)

        self.load_config()
        self.start_daemon()

        if(self.weckzeit):
            self.init_scheduler()

    @cherrypy.expose
    def start_dimming(self):
        if(not self.wecken_p):
            print("Wecker ist aus")
            return "Wecker ist aus"
        
        if(TESTING):
            dimm_dauer = 8 #sekunden
            nachleuchten = 1 #sekunden
            pwm_start = 1000
            pwm_ende  = 2550
        else:
            pwm_start = 1200
            pwm_ende  = 2550
            dimm_dauer = 1800 #sekunden
            nachleuchten = 1800 #sekunden

        try:
            self.pi.write(SSR_PIN,1)
            print("start dimming")
            time.sleep(0.2)
            for i in range(pwm_start,pwm_ende):
                self.pi.set_PWM_dutycycle(LED_PIN,i/10)
                time.sleep(dimm_dauer / (pwm_ende - pwm_start))

            time.sleep(nachleuchten)
        finally:
            self.pi.write(SSR_PIN,0)
            time.sleep(0.5)
            self.pi.set_PWM_dutycycle(LED_PIN,0)
            self.pi.stop()
            print( "fertig")

    def init_scheduler(self):
        print("init_scheduler")
        # self.stop_daemon()
        # if(self.daemon_thread):
        #     self.daemon_thread.join()
        schedule.clear()
        schedule.every().day.at(self.weckzeit).do(self.start_dimming)
        #self.start_daemon()

    def start_daemon(self):
        print("-- START DAEMON --")
        self.daemon_run = True
        self.daemon_thread = threading.Thread(target=self.scheduler_daemon, name='scheduler_thread')
        self.daemon_thread.daemon = True
        self.daemon_thread.start()

    def stop_daemon(self):
        self.daemon_run = False
        
    def scheduler_daemon(self):
        while self.daemon_run:
            schedule.run_pending()
            time.sleep(1)
        print("-- DAEMON ENDE --")
        
        
    def save_config(self):
        # Daten in JSON-File raussschreiben
        config = {'weckzeit' : self.weckzeit,
                  'wecker_startzeit' : self.wecker_startzeit,
                  'wecken_p' : self.wecken_p}

        with open(self.config_file, 'w') as fp:
            json.dump(config, fp)

    def load_config(self):
        # Daten aus JSON-File einlesen
        with open(self.config_file, 'r') as fp:
            config = json.load(fp)
            self.weckzeit = config['weckzeit']
            self.wecker_startzeit = config['wecker_startzeit']
            self.wecken_p = config['wecken_p']

        
        
    @cherrypy.expose
    def get_wecken_p(self):
        if(self.wecken_p):
            return "on"
        else:
            return "off"

    @cherrypy.expose
    def set_wecken_p(self, wecken_p):
        result = ''
        if(wecken_p == "on"):
            self.wecken_p = True
            result = "on"
        elif(wecken_p == "off"):
            self.wecken_p = False
            result = "off"
        else:
            result = "error"
        self.save_config()
        return result

        
    @cherrypy.expose
    def light_on(self):
        try:
            self.pi.write(SSR_PIN,1)
            self.pi.set_PWM_dutycycle(LED_PIN,255)
            return "ok"
        except:
            return "ko"

    @cherrypy.expose
    def light_off(self):
        try:
            self.pi.set_PWM_dutycycle(LED_PIN,0)
            self.pi.write(SSR_PIN,0)
            return "ok"
        except:
            return "ko"

    @cherrypy.expose
    def set_time(self,weckzeit):
        try:
            t1 = datetime.datetime.strptime(weckzeit,'%H:%M')
            t2 = datetime.timedelta(seconds=self.dimm_dauer, minutes=12)
            self.wecker_startzeit = (t1-t2).strftime("%H:%M")
            print("STARTZEIT: " + str(self.wecker_startzeit))
            
            self.weckzeit = weckzeit
            print("WECKZEIT: " + str(self.weckzeit))
            self.save_config()

            self.init_scheduler()
            
            return self.weckzeit
        except:
            return "Weckzeit konnte nicht gesetzt werden."

    @cherrypy.expose
    def get_time(self):
        if(self.weckzeit):
            return self.weckzeit
        else:
            return "06:30"
        
    def index(self):
        output = """<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <title>Lichtwecker</title>
    <script type="text/javascript" src='/static/jquery-2.1.4.min.js' ></script>
    <script type="text/javascript" src='/static/main.js' ></script>
  </head>

  <body>
    <div id='content'></div>
  </body>

</html>"""
        return output
    index.exposed = True


if __name__ == '__main__':
    conf = {
        '/' : {
            'tools.sessions.on' : True,
            'tools.staticdir.root' : os.path.abspath(os.getcwd())
        },
        '/static' : {
            'tools.staticdir.on' : True,
            'tools.staticdir.dir' : './static'
        },
    }
    cherrypy.config.update({'server.socket_host' : '0.0.0.0',
                            'server.socket_port' : 10000, })
    cherrypy.quickstart(WeckerWeb(), '/', conf)
    
