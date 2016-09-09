from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
driver=None

ELEMENT_USERNAME_ID='username' #username field id (css selector)
ELEMENT_PASSWORD_ID='password' #password inuput field id (css selector)
ELEMENT_LOGIN_BTN_ID='loginBtn' #login button id (css selector) not used

FRAME_TAG='frame' #frame or iframe
FRAME_NAME='main' #frame or iframe name attribute value

CONNECTION_NAME='Somnath' #Wifi connection ssid

ROUTER_URL='http://192.168.2.1'

CHROME_DRIVER_RELATIVE_PATH="./drivers/chromedriver.exe"
URL_TO_CHECK_INTERNET='https://www.google.co.in'

IP_MAC_FILE_LIST_RELATIVE_PATH='ip_macs.txt'
def init():
    global driver
    global initialized
    driver=webdriver.Chrome(CHROME_DRIVER_RELATIVE_PATH)
    driver.get(ROUTER_URL)
    initialized=True

def login(username,password):
    global driver
    ele_username=driver.find_element_by_id(ELEMENT_USERNAME_ID)
    ele_password=driver.find_element_by_id(ELEMENT_PASSWORD_ID)
    ele_loginBtn=driver.find_element_by_id(ELEMENT_LOGIN_BTN_ID)
    ele_username.clear()
    ele_password.clear()
    ele_username.send_keys(username)
    ele_password.send_keys(password)
    ele_password.send_keys(Keys.RETURN)

def switchFrame():
    frame=None
    for f in driver.find_elements_by_tag_name(FRAME_TAG):
        if f.get_attribute('name')==FRAME_NAME:
            frame=f
            break;
    if frame==None:
        print 'aborting no frame with name',FRAME_NAME,'exists'
        return False
    driver.switch_to_frame(frame)

def navigateToInternetSetup():
    global driver
    for element in driver.find_elements_by_tag_name('a'):
        if element.get_attribute('innerHTML')=='Setup':
            element.send_keys(Keys.RETURN)
            break;
    for element in driver.find_elements_by_tag_name('a'):
        if element.get_attribute('innerHTML')=='Internet Setup':
            element.send_keys(Keys.RETURN)
            break;

def setIpMac(ip,mac):
    global driver
    for element in driver.find_elements_by_tag_name('input'):
        if element.get_attribute('name')=='mac_clone' and element.get_attribute('value')=='2':
            element.click()
            break;

    ele_ip=None
    ele_mac=None

    for element in driver.find_elements_by_tag_name('input'):
        if element.get_attribute('name')=='staip_ipaddr':
            ele_ip=element
        elif element.get_attribute('name')=='mac_clone_value':
            ele_mac=element
        if ele_ip and ele_mac:
            break;
    if ele_ip.get_attribute("value")==ip:
        print 'already using this combination'
        return False
    ele_ip.clear()
    ele_ip.send_keys(ip)
    ele_mac.clear()
    ele_mac.send_keys(mac)
    ele_ip=None
    ele_mac=None
    for element in driver.find_elements_by_tag_name('input'):
        if element.get_attribute('type')=='submit' and element.get_attribute('name')=='save':
            element.send_keys(Keys.RETURN)
            return True

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
isLoggedIn=False
skip=False
progress=['|','/','-','\\']
pi=0
for x in ls:
    if skip or not isInternetConnected():
        skip=False #skipped now need to reset skip counter
        if not initialized:
            init()
        if x:
            if not isLoggedIn:
                login('Admin','@dmin')
                switchFrame()
                driver.implicitly_wait(10);
                navigateToInternetSetup()
            ip,mac=x.split()
            mac=mac[0:2]+':'+mac[2:4]+':'+mac[4:6]+':'+mac[6:8]+':'+mac[8:10]+':'+mac[10:12]
            print 'checking',ip,mac
            if not setIpMac(ip,mac):
                print 'cannot set ip mac, try again later'
                isLoggedIn=True
            else:
                isLoggedIn=False # logged out login again
                print 'waiting for router to reboot'
                for t in range(35):
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
            print 'okay! trying others'
