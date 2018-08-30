#!/usr/bin/python2
import curses
import os
import os.path
import subprocess
import re
import cups
import json
def saveToFile():
    with open('settings.json','w') as file:
        json.dump(allSettings,file)
    
def setPrinter(printer):
    global currentPrinter
    currentPrinter = printer
    allSettings['printer'] = printer
    winprinters.addstr(8, 13, "                                                                       ")
    winprinters.addstr(8, 13, printer)
    winprinters.refresh()
    saveToFile()
    
def setScanner(scan,display):
    global currentScanner
    currentScanner = scan
    allSettings['scanner'] = scan
    winscanners.addstr(7, 13, "                                                                           ")
    winscanners.addstr(7, 13, display)
    winscanners.refresh()
    saveToFile()

#Read Settings
if os.path.isfile('settings.json'):
    with open('settings.json') as json_data:
        try:
            allSettings = json.load(json_data)
        except:
            allSettings = {'printer': '', 'scanner': ''}     
else:
    allSettings = {'printer': '', 'scanner': ''}

stdscr = curses.initscr()
curses.cbreak()
curses.noecho()
stdscr.keypad(1)

curses.start_color()
curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
stdscr.bkgd(curses.color_pair(1))
stdscr.refresh()

#Read existing printers
conn = cups.Connection ()
printers = conn.getPrinters ()

welcome = curses.newwin(3, 25, 1, 40)
welcome.bkgd(curses.color_pair(2))
welcome.box()
welcome.addstr(1, 2, "     Raspi-Copy      ", curses.A_STANDOUT)
welcome.refresh()

key = ''
copies = 1
lastkey = 0
ColorMode = "Color"
currentScanner = ""

wincopy = curses.newwin(5, 30, 5, 1)
wincopy.bkgd(curses.color_pair(2))
wincopy.box()
wincopy.addstr(2, 2, "Anzahl der Kopien:")
wincopy.addstr(2, 21, str(copies), curses.A_BOLD)
wincopy.refresh()

wincolor = curses.newwin(5, 30, 5, 32)
wincolor.bkgd(curses.color_pair(2))
wincolor.box()
wincolor.addstr(2, 2, "Farbe:")
wincolor.addstr(2, 15, ColorMode, curses.A_BOLD)
wincolor.refresh()


winprinters= curses.newwin(10, 100, 21, 1)
winprinters.bkgd(curses.color_pair(2))
winprinters.box()
winprinters.addstr(1, 2, "Drucker:", curses.A_STANDOUT)
winprinters.addstr(8, 2, "Druck auf: ")
line = 2
fkey = 5;
listPrinters = {}
for printer in printers:
    if line <6:
        winprinters.addstr(line, 2, "F"+str(fkey)+": "+printer)
        listPrinters[fkey] = printer
        line = line+1
        fkey = fkey+1
winprinters.refresh()

winscanners= curses.newwin(9, 100, 11, 1)
winscanners.bkgd(curses.color_pair(2))
winscanners.box()
winscanners.addstr(1, 2, "Scanner:", curses.A_STANDOUT)
winscanners.addstr(7, 2, "Scan von: ")
winscanners.refresh()

output = subprocess.check_output("scanimage -L", shell=True).decode('utf-8')
results = output.strip().split("\n")
sline = 2
sfkey = 1
listScanners = {}

for i, s in enumerate(results):
    m = re.match("^device `(.*)' is a (.*)" ,s.strip() )
    if m is not None:
        winscanners.addstr(sline, 2, "F"+str(sfkey)+": "+m.groups()[1])
        listScanners[sfkey] = {}
        listScanners[sfkey]['name'] = m.groups()[0]
        listScanners[sfkey]['display'] = m.groups()[1]
        sline = sline+1
        sfkey = sfkey+1
    
winscanners.refresh()

setPrinter(allSettings['printer'])
setScanner(allSettings['scanner'],allSettings['scanner'])

while key != ord('q'):
    key = stdscr.getch()
    
    if key >264 and key <269:
        scanner = key-264
        if scanner in listScanners:
            setScanner(listScanners[scanner]['name'], listScanners[scanner]['display'] )
    
    if key == 47:
        ColorMode = "Color"
        wincolor.addstr(2, 15, ColorMode+"     ", curses.A_BOLD)
        wincolor.refresh()
        
    if key == 42:
        ColorMode = "Gray"
        wincolor.addstr(2, 15, ColorMode+"     ", curses.A_BOLD)
        wincolor.refresh()
    
    if key >268 and key <273:
        pri = key-264
        if pri in listPrinters:
            setPrinter(listPrinters[pri])
            winprinters.refresh()
    

    if key >47 and key <58:
     if lastkey == 0:
         copies = 0
     key = key-48
     if len(str(copies)) < 3:
         if copies == 0:
             copiestring = str(key)
         else:
            copiestring = str(copies)+str(key)
         copies = int(copiestring);
         wincopy.addstr(2, 21, copiestring+"     ", curses.A_BOLD)
     lastkey = 1


    elif key == 10:
        lastkey = 0
        
        if str(copies) == "999":
            # add some scan magic here...
            print("scan")
        else:
            #copy the file
            if len(currentScanner) and len(currentPrinter):
                os.popen("sudo scanimage -d "+currentScanner+" -x 210 -y 297 --resolution 300 --mode "+ColorMode+" --format jpg  > copy.jpg")
                os.popen("lpr -P "+currentPrinter+" -# "+str(copies)+" copy.jpg")
    
    elif key == 44  or key== 263:
        lastkey = 0
        copies = 1
        wincopy.addstr(2, 21, str(copies)+"     ", curses.A_BOLD)
    elif key == 43:
        lastkey = 0
        if copies < 999:
            copies = copies+1
            wincopy.addstr(2, 21, str(copies)+"     ", curses.A_BOLD)
    elif key == 45:
        lastkey = 0
        if copies > 1:
            copies = copies-1
            wincopy.addstr(2, 21, str(copies)+"     ", curses.A_BOLD)
    wincopy.refresh()
         
# End
curses.nocbreak()
stdscr.keypad(0)
curses.echo()
curses.endwin()