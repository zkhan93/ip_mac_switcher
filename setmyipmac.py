from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import sys

skipTopRecords=0
if len(sys.argv)>1:
    skipTopRecords=int(sys.argv[1])
recordProcessed=skipTopRecords

driver=None

ELEMENT_USERNAME_ID='username' #username field id (css selector)
ELEMENT_PASSWORD_ID='password' #password inuput field id (css selector)
ELEMENT_LOGIN_BTN_ID='loginBtn' #login button id (css selector) not used

FRAME_TAG='frame' #frame or iframe
NAV_FRAME_NAME='bottomLeftFrame' #frame or iframe name attribute value
MAIN_FRAME_NAME='mainFrame'

CONNECTION_NAME='Khan\'s AP' #Wifi connection ssid

ROUTER_IP='192.168.2.1'
ROUTER_REBOOT_TIME=20 #in seconds
CHROME_DRIVER_RELATIVE_PATH="./drivers/chromedriver"
URL_TO_CHECK_INTERNET='https://www.google.co.in'

IP_MAC_FILE_LIST_RELATIVE_PATH='ip_macs - Copy.txt'

username='admin'
password='admin'

def init():
    global driver
    global initialized
    options = webdriver.ChromeOptions();
    options.add_argument("test-type");
    options.add_argument("--start-maximized");
    options.add_argument("--disable-web-security");
    options.add_argument("--allow-running-insecure-content");
    driver=webdriver.Chrome(CHROME_DRIVER_RELATIVE_PATH,chrome_options=options)
    driver.get('http://'+username+':'+password+'@'+ROUTER_IP)
    initialized=True

'''
Not used for my router anymore
'''
def login():
    global driver
    ele_username=driver.find_element_by_id(ELEMENT_USERNAME_ID)
    ele_password=driver.find_element_by_id(ELEMENT_PASSWORD_ID)
    ele_loginBtn=driver.find_element_by_id(ELEMENT_LOGIN_BTN_ID)
    ele_username.clear()
    ele_password.clear()
    ele_username.send_keys(username)
    ele_password.send_keys(password)
    ele_password.send_keys(Keys.RETURN)

def switchFrame(name):
    global driver
    driver.switch_to_default_content()
    frame=None
    for f in driver.find_elements_by_tag_name(FRAME_TAG):
        if f.get_attribute('name')==name:
            frame=f
            break;
    if frame==None:
        print 'no frame with name',name,'exists\n refreshed and trying'
        driver.refresh()
        time.sleep(3)
        switchFrame(name)
        return False
    driver.switch_to_frame(frame)

def navigateTo(path):
    global driver
    switchFrame(NAV_FRAME_NAME)
    found=False
    for seg in path:
        found=False
        for element in driver.find_elements_by_tag_name('a'):
            if element.get_attribute('innerHTML')==seg:
                element.click()
                print seg,'->',
                found=True
                break;
        if not found:
            print seg,'not found'
            break
    if not found:
        print 'trying after refresh'
        switchFrame(MAIN_FRAME_NAME)
        driver.refresh()
        time.sleep(1)
        navigateTo(path)
    switchFrame(MAIN_FRAME_NAME)
    return found

def setMac(mac):
    navigateTo(['Network','MAC Clone'])
    ele_mac=None
    for element in driver.find_elements_by_tag_name('input'):
        if element.get_attribute('name')=='mac1':
            ele_mac=element
            break;
    if ele_mac.get_attribute("value")==mac:
        print 'already using this MAC address'
        return False
    ele_mac.clear()
    ele_mac.send_keys(mac.upper())
    for element in driver.find_elements_by_tag_name('input'):
        if element.get_attribute('type')=='submit' and element.get_attribute('name')=='Save':
            element.send_keys(Keys.RETURN)
            return True
    print 'coudn\'t save MAC'
    return False

def setIp(ip):
    navigateTo(['Network','WAN'])
    ele_ip=None
    for element in driver.find_elements_by_tag_name('input'):
        if element.get_attribute('name')=='ip':
            ele_ip=element
            break;
    if ele_ip.get_attribute("value")==ip:
        print 'already using this IP'
        return False
    ele_ip.clear()
    ele_ip.send_keys(ip)
    for element in driver.find_elements_by_tag_name('input'):
        if element.get_attribute('type')=='submit' and element.get_attribute('name')=='Save':
            element.send_keys(Keys.RETURN)
            return True
    print 'coudn\'t save ip'
    return False

def setIpMac(ip,mac):
    if setIp(ip):
        if setMac(mac):
            return True
        else:
            print 'cannot set MAC, might already using this'
    else:
        print 'cannot set ip, might already using this'
    return False

def isConnectedToDesiredNetwork():
    import subprocess
    return CONNECTION_NAME in subprocess.check_output("netsh wlan show interfaces")

def isInternetConnected():
    import urllib2
    try:
        response=urllib2.urlopen(URL_TO_CHECK_INTERNET,timeout=1)
        if response.code in (300, 301, 302, 303, 307):
            return False
        return True
    except Exception as e:
        print '\b'+str(e)
        return False

file=open(IP_MAC_FILE_LIST_RELATIVE_PATH)
ls=file.read().split('\n')
file.close()
ip=None
mac=None
initialized=False
skip=False
progress=['|','/','-','\\']
pi=0

for x in ls[skipTopRecords:]:
    if skip or not isInternetConnected():
        skip=False #skipped now need to reset skip counter
        if not initialized:
            init()
        if x:
            ip,mac=x.split()
            splitter='-'
            mac=mac[0:2]+splitter+mac[2:4]+splitter+mac[4:6]+splitter+mac[6:8]+splitter+mac[8:10]+splitter+mac[10:12]
            print 'checking',ip,mac,recordProcessed
            if not setIpMac(ip,mac):
                print 'cannot set ip mac, try again later'
            else:
                print 'waiting for router to reboot'
                for t in range(ROUTER_REBOOT_TIME):
                    print '\b'+progress[pi%4],'\b\b',
                    pi+=1
                    time.sleep(1);
            print '\bwaiting for network',CONNECTION_NAME,'to connect'

            while not isConnectedToDesiredNetwork():
                print '\b'+progress[pi%4],'\b\b',
                pi+=1
                time.sleep(1);

    else:
        print 'Connected to internet.'
        print 'let me know if you need to try other set of ip and mac [y/N]:',
        option=raw_input()
        if option not in ['y','Y','yes','YES']:
            print 'enjoy then!'
            if driver:
                driver.close()
            break;
        else:
            skip=True
            print 'okay! trying others position:',recordProcessed
    recordProcessed+=1
