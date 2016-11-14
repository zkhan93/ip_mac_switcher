# IP MAC Switcher

It is a Python script to change IP and MAC address of your router, 
since I use selenium to navigate through the admin section of router it highly depend on the webpage hosted by router.

This project currently work for two router models

  * DLink - DIR-600M
  * TPLink - 
  
##Requirements
You need to have Python2.7 installed
you also need to install following pip packages
  * selenium
  * subprocess
  * urllib2
you can install these by

linux `pip install selenium subprocess urllib2`

windows `python -m pip install selenium subprocess urllib2`

##Configuration
Before running this script you need to configure some variable in the script
 *  `ELEMENT_USERNAME_ID` - CSS selector id from the login page's username input field
 *  `ELEMENT_PASSWORD_ID` - CSS selector id from the login page's password input field
 *  `ELEMENT_LOGIN_BTN_ID` - CSS selector id from the login page's login button
 *  `FRAME_TAG` - router uses frame or iframe
 *  `NAV_FRAME_NAME` - Navigation frame name 
 *  `MAIN_FRAME_NAME` - Main frame's name
 *  `CONNECTION_NAME` - Wifi SSID script will wait until he this SSID is connected
 *  `ROUTER_IP` - Router's IP address 
 *  `ROUTER_REBOOT_TIME` - Time in seconds that router takes to reboot - MAC change need reboot
 *  `CHROME_DRIVER_RELATIVE_PATH` - you need to download [cromedriver](https://sites.google.com/a/chromium.org/chromedriver/) and provide a relative path from the script
 *  `URL_TO_CHECK_INTERNET` - A URL to check internet connectivity
 *  `IP_MAC_FILE_LIST_RELATIVE_PATH` - Relative path of file containing IP address and MAC(no seperator) seperated by a tab
 *  `username` - Username of router - usually admin
 *  `password` - Password of router
 
###Execution
With all set you just need to run the script
`python setip.py <no_of_records_to_skip_from_top>`
for example
`python setip.py 5` - this will start from the 5th record in IP MAC file

Todo
  * Generalize the core code
  * Add more router support
  * Seperate configuration variable from code
