#!/usr/bin/python3

import cherrypy
import time
import pigpio
import os
import datetime
import time
import json
import schedule
import threading

LED_PIN = 24
SSR_PIN = 23
TESTING = True

SCRIPT_PATH = os.path.realpath(__file__)
SCRIPT_DIR  = "/".join(SCRIPT_PATH.split("/")[0:-1])

# Starting Scheduling Daemon
print("-- START DAEMON --")
SCHEDULER_RUN = True
def scheduler_daemon():
    while SCHEDULER_RUN:
        schedule.run_pending()
        time.sleep(1)

daemon_thread = threading.Thread(target=scheduler_daemon, name='scheduler_thread')
daemon_thread.daemon = True
daemon_thread.start()


def time_difference(t1):
    FMT = '%H:%M'
    t2 = datetime.datetime.strftime(datetime.datetime.now(), FMT)
    s1 = datetime.datetime.strptime(t2, FMT)
    s2 = datetime.datetime.strptime(t1, FMT)
    tdelta = s2 - s1
    return time.strftime("%H:%M", time.gmtime(tdelta.seconds))

def sched_test():
    print("--- TEST ---")

class WeckerWeb(object):
    def __init__(self):
        # Wecker parameter
        self.weckzeit = None          
        self.wecker_startzeit = None
        self.wecken_p = False
        
        self.dimm_dauer = 120 #sekunden
        self.nachleuchten = 1 #sekunden

        self.config_file = SCRIPT_DIR + "/config.json"
        
        # PWM Configuration
        self.pwm_start = 1000
        self.pwm_ende  = 2550

        self.pi = pigpio.pi()
        # setup pin as an output
        self.pi.set_mode(LED_PIN, pigpio.OUTPUT)
        # pi set frequency
        self.pi.set_PWM_frequency(LED_PIN, 1200)

        self.load_config()

        if(self.weckzeit):
            self.init_scheduler()

    @cherrypy.expose
    def start_dimming(self):
        if(not self.wecken_p):
            print("Wecker ist aus")
            return "Wecker ist aus"
        
        try:
            self.pi.write(SSR_PIN,1)
            print("start dimming")
            time.sleep(0.2)
            for i in range(self.pwm_start,self.pwm_ende):
                self.pi.set_PWM_dutycycle(LED_PIN,i/10)
                time.sleep(self.dimm_dauer / (self.pwm_ende - self.pwm_start))

            time.sleep(self.nachleuchten)
        finally:
            self.pi.write(SSR_PIN,0)
            self.pi.set_PWM_dutycycle(LED_PIN,0)
            print( "fertig")

    def init_scheduler(self):
        print("init_scheduler")
        schedule.clear()
        schedule.every().day.at(self.wecker_startzeit).do(self.start_dimming)
        
    def save_config(self):
        # Daten in JSON-File raussschreiben
        config = {'weckzeit' : self.weckzeit,
                  'wecker_startzeit' : self.wecker_startzeit,
                  'wecken_p' : self.wecken_p,
                  'dimm_dauer' : self.dimm_dauer,
                  'nachleuchten' : self.nachleuchten}

        with open(self.config_file, 'w') as fp:
            json.dump(config, fp)

    def load_config(self):
        # Daten aus JSON-File einlesen
        with open(self.config_file, 'r') as fp:
            config = json.load(fp)
            self.weckzeit = config['weckzeit']
            self.wecker_startzeit = config['wecker_startzeit']
            self.wecken_p = config['wecken_p']
            self.dimm_dauer = config['dimm_dauer']
            self.nachleuchten = config['nachleuchten']


    @cherrypy.expose            
    def get_dimmdauer(self):
        return str(int(self.dimm_dauer  / 60))

    def set_startzeit(self):
        t1 = datetime.datetime.strptime(self.weckzeit,'%H:%M')
        t2 = datetime.timedelta(seconds=self.dimm_dauer)
        self.wecker_startzeit = (t1-t2).strftime("%H:%M")

    
    @cherrypy.expose
    def set_dimmdauer(self, dimmdauer):
        output  = ''
        try:
            self.dimm_dauer = int( int(dimmdauer) * 60 )
            output = int(self.dimm_dauer / 60)
        except:
            standard_dimmdauer = 10 * 60
            self.dimm_dauer = int(standard_dimmdauer)
            output = int(standard_dimmdauer / 60)
        finally:
            self.set_startzeit()
            self.save_config()
            return str(output) + ";" + self.wecker_startzeit

    @cherrypy.expose
    def get_nachleuchten(self):
        return str(int(self.nachleuchten / 60))

    @cherrypy.expose
    def set_nachleuchten(self, nachleuchten):
        output = ''
        try:
            self.nachleuchten = int( int(nachleuchten) * 60)
            output = str(int(self.nachleuchten / 60))
        except:
            standard_nachleuchten = 10 * 60
            self.nachleuchten = int(standard_nachleuchten)
            output = str(int(standard_nachleuchten / 60))
        finally:
            self.save_config()
            return str(output)
            
        
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
            self.weckzeit = weckzeit
            self.set_startzeit() # vorher weckzeit setzen
            print("STARTZEIT: " + str(self.wecker_startzeit))
            

            print("WECKZEIT: " + str(self.weckzeit))
            self.save_config()

            self.init_scheduler()
            
            return self.weckzeit + ";" + time_difference(self.weckzeit) + ";" + time_difference(self.wecker_startzeit)
        except:
            return "Weckzeit konnte nicht gesetzt werden."

    @cherrypy.expose
    def get_time(self):
        if(self.weckzeit):
            return self.weckzeit + ";" + time_difference(self.weckzeit) + ";" + time_difference(self.wecker_startzeit)
        else:
            return "06:30" + ";" + time_difference(self.weckzeit) + ";" + time_difference(self.wecker_startzeit)

    @cherrypy.expose
    def get_lichtstart(self):
        return time_difference(self.wecker_startzeit)
        
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
            'tools.staticdir.root' : SCRIPT_DIR
        },
        '/static' : {
            'tools.staticdir.on' : True,
            'tools.staticdir.dir' : './static'
        },
    }
    cherrypy.config.update({'server.socket_host' : '0.0.0.0',
                            'server.socket_port' : 10000, })

    cherrypy.quickstart(WeckerWeb(), '/', conf)

    # Beenden von Scheduler Thread
    SCHEDULER_RUN = False    
    daemon_thread.join()


    print("ENDE")
