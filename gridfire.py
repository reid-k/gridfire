#!/usr/bin/env python

program_name = "Gridfire"
program_version = "v0.5"

#Gridfire is inspired by gpggrid, a security tool included in
#Tinfoil Hat Linux, intended to resist shoulder-surfing and keylogging.
#For more information on the project, see the README file distributed
#with Gridfire.

#Gridfire is named after a fictional superweapon in Iain M Banks'
#Culture novels.  See http://everything2.com/title/Gridfire for more.
# RIP Iain M Banks (1954-02-16 to 2013-06-09)

#Learn more about Tinfoil Hat Linux:
#Homepage:  http://tinfoilhat.shmoo.com/
#Wikipedia: https://en.wikipedia.org/wiki/Tinfoil_Hat_Linux

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

#TODO: Decide whether or not implement method 4
#TODO: Fix row index for non-default charsets

#import os
import sys
import curses
import locale
import string
import random
import argparse

#Helps curses play nice
locale.setlocale(locale.LC_ALL, '')
code = locale.getpreferredencoding()

##### Defaults & Initial variables #####
charsets = ''
min_x, min_y = 55, 17
upperchar, lowerchar, out = '','',''
hide_out = 0

def spaceout(s):
	i=len(s)-1 #number of spaces to be inserted
	while i >= 1:
		s = s[:-i]+" "+s[-i:]
		i -= 1
	return s

newline = 0

##### Argument parsing #####
parser = argparse.ArgumentParser()
parser.add_argument('-c', help="Force concealment of entered text.", action="store_true")
parser.add_argument('-g', '--grid', help="Ignore other options and behave like gpggrid.", action="store_true")
#~ parser.add_argument('-u', dest='char_u', action='store_true')
parser.add_argument('-u', help="Allow uppercase letters [A-Z].", action="store_true")
parser.add_argument('-l', help="Allow lowercase letters [a-z].", action="store_true")
parser.add_argument('-b', help="Allow binary numbers [0-1].", action="store_true")
parser.add_argument('-o', help="Allow octal numbers [0-7].", action="store_true")
parser.add_argument('-d', help="Allow decimal numbers [0-9].", action="store_true")
parser.add_argument('-f', help="Allow hexadecimal numbers [0-9][a-f][A-F].", action="store_true")
parser.add_argument('-p', help="Allow punctuation.", action="store_true")
parser.add_argument('-w', help="Allow whitespace.", action="store_true")
parser.add_argument('-m', '--method', help='Specify indexing method (0-3, higher is more secure)', dest='method')
parser.add_argument('-n', help="Append a newline on output.", action="store_true", dest='newline')
parser.add_argument('-0', help="Use indexing method 0.", dest="method", action="store_true")
parser.add_argument('-1', help="Use indexing method 1.", dest="method", action="store_true")
parser.add_argument('-2', help="Use indexing method 2.", dest="method", action="store_true")
parser.add_argument('-3', help="Use indexing method 3.", dest="method", action="store_true")
parser.add_argument('-t', help="Run in training mode (no output).", dest="training", action="store_true")
args = vars(parser.parse_args())

#Define character sets
punct	   = spaceout(string.punctuation)
punct2	   = punct[52:]
punct	   = punct[:52]
whitespace = spaceout(string.whitespace)

#Select character sets
#TODO: Can this be simplified? args['u'+'l'] or whatnot?
#use_uppercases = (-1 != charsets.find("u"))
use_uppercases = args['u']
use_lowercases = args['l']
use_bindigits  = args['b']
use_octdigits  = args['o']
use_decdigits  = args['d']
use_hexdigits  = args['f']
use_punct      = args['p']
use_whitespace = args['w']
setcount = args['u']+args['l']+args['b']+args['o']+args['d']+args['f']+args['p']+args['w']

#if use_uppercases+use_lowercases+use_bindigits+use_octdigits+use_decdigits+use_hexdigits+use_punct+use_whitespace == 0:
if setcount == 0:
	use_uppercases = 1
	use_lowercases = 1
	use_decdigits  = 1
	use_punct      = 1
	use_whitespace = 1

use_numbers    = 0
numbers = ''
if use_bindigits+use_octdigits+use_decdigits+use_hexdigits: use_numbers = 1
if use_bindigits: numbers = '0 1'
if use_octdigits: numbers = spaceout(string.octdigits)
if use_decdigits: numbers = spaceout(string.digits)
if use_hexdigits: numbers = spaceout(string.hexdigits)

##### Build static grid #####
grid = []
if use_uppercases: grid.append(spaceout(string.uppercase))
if use_lowercases: grid.append(spaceout(string.lowercase))
if use_numbers: grid.append(numbers)
if use_punct:
	grid.append(punct)
	grid.append(punct2)

##### Build user interface #####
#usagebanner = "Type pairs of letters for row and column, e.g. eF, Dg"
usagebanner = "Choose from grid by typing letter pairs like eF or Dg"
shortcuts = "8:Selection  9:Output  0:Quit"

stdscr = curses.initscr()
curses.noecho()
curses.start_color()
curses.use_default_colors()
stdscr.keypad(1)

def quit(leave_message = "", exit_status= 0):
	curses.nocbreak()
	stdscr.keypad(0)
	curses.echo()
	curses.endwin()
	print leave_message
	sys.exit(exit_status)

# Check for required size before continuing
(size_y,size_x) = stdscr.getmaxyx()
if ((size_x < min_x)|(size_y < min_y)):
	print program_name+" needs a "+str(min_x)+"x"+str(min_y)+" character area to function.\n"
	print "please adjust your terminal size and restart "+program_name+"."
	sys.exit(1)

def total_rows(): return use_lowercases+use_uppercases+use_decdigits+use_whitespace+use_punct+use_punct+1

def cycle_index(cyclemethod=3): #Argument specifies method, default is 3
	global col_index, row_index
	#Method 0: Ordered letters and numbers, no randomization
	#This method has 1 possible state and provides no security.
	#Included to allow gridfire's use to limit possible symbols entered.
	#For example, hex digits only when entering a WEP key.
	if cyclemethod==0:
		col_index = string.uppercase
		row_index = string.lowercase
	
	#Method 1: Ordered letters, random offset (as with gpggrid)
	#The math might differ from gpggrid
	#This method has 676 or 26^2 possible states
	if cyclemethod==1:
		offset = random.randint(0,25)
		col_index = string.uppercase[offset:]+string.uppercase[:offset]
		offset = random.randint(0,25)
		row_index = string.lowercase[offset:]+string.lowercase[:offset]

	#Method 2: use random.shuffle() to shuffle one index in place
	#This might not work very well, see module documentation on
	#issues with small len(x) exceeding period of RNGs
	# http://docs.python.org/2/library/random.html
	##This method has:
	##403,291,461,126,605,635,584,000,000
	##or 26! possible states (403.3 septillion)
	if cyclemethod==2:
		col_index = string.uppercase
		colcycle = list(string.uppercase)
		random.shuffle(colcycle)
		col_index = ''.join(colcycle)
		row_index = col_index.lower()

	#Method 3: use random.shuffle() to shuffle indices in place
	#This might not work very well, see module documentation on
	#issues with small len(x) exceeding period of RNGs
	# http://docs.python.org/2/library/random.html
	#This method has:
	#162,644,002,617,632,464,507,038,883,409,628,607,021,056,000,000,000,000
	##or 26!^2 possible states (162.6 sexdecillion).
	if cyclemethod==3:
		col_index = string.uppercase
		colcycle = list(string.uppercase)
		random.shuffle(colcycle)
		col_index = ''.join(colcycle)
		
		row_index = string.lowercase
		rowcycle = list(string.lowercase)
		random.shuffle(rowcycle)
		row_index = ''.join(rowcycle)
	
	#TODO: Implement method 4 (mixed cases in row/column indexes)
        # (This would require redoing input handling to recognize same-case pairs)
	#Method 4 would have:
	#80,658,175,170,943,878,571,660,636,856,403,766,975,289,505,440,883,277,824,000,000,000,000
	#or 52! possible states (80.6 Unvigintillion).

# Draw
pad = curses.newpad(100,100)
padpos = 0

def pad_draw(ly,lx,hy,hx):
	pad.addstr(0,0," "*(hx+1),curses.A_REVERSE)
	pad.addstr(0,2,program_name +" "+ program_version,curses.A_REVERSE)
	pad.addstr(1,0," "*min_x)
	#~ pad.addstr(0,40,"	")
	pad.addstr(0,40,lowerchar,curses.A_REVERSE)
	pad.addstr(0,41,upperchar,curses.A_REVERSE)
	pad.addstr(0,43,"SHOW")
	if hide_out: pad.addstr(0,43,"HIDE")
	pad.addstr(2,0,">>")
	pad.addstr(2,4," "*(len(out)+1))
	disp_out = out
	if hide_out: disp_out = len(out)*"*"
	pad.addstr(2,4,disp_out)
	
	##Draw the grid
	global gridrow
	gridrow = 6
	gridoffset = 4
	
	#Grid Indexes
	pad.addstr(gridrow-2,gridoffset,spaceout(col_index))
	for t in range(0,total_rows()):
		pad.addstr(gridrow+t,1,row_index[t])
		t += 1
	
	#Index selection highlighting
	if len(upperchar): stdscr.addstr(gridrow-2,4+spaceout(col_index).find(upperchar),upperchar,curses.A_REVERSE)
	if len(lowerchar): stdscr.addstr(gridrow+row_index.find(lowerchar),1,lowerchar,curses.A_REVERSE)
	
	#Static grid elements
	### New grid draw method ###
	r = 0
	for s in grid:
		pad.addstr(gridrow,gridoffset,grid[r])
		r += 1
		gridrow += 1
	
	if use_whitespace:
		#Draw the whitespace row
		pad.addstr(gridrow,gridoffset," :Space  :Tab  :Enter")
		pad.addstr(gridrow,gridoffset,col_index[0])
		pad.addstr(gridrow,8+gridoffset,col_index[1])
		pad.addstr(gridrow,14+gridoffset,col_index[2])
		#If the corresponding columns are selected, highlight them
		if len(upperchar)&(upperchar==col_index[0]): stdscr.addstr(gridrow,4+col_index.find(upperchar),upperchar,curses.A_REVERSE)
		if len(upperchar)&(upperchar==col_index[1]): stdscr.addstr(gridrow,11+col_index.find(upperchar),upperchar,curses.A_REVERSE)
		if len(upperchar)&(upperchar==col_index[2]): stdscr.addstr(gridrow,16+col_index.find(upperchar),upperchar,curses.A_REVERSE)
		gridrow += 1

	#Draw the 'done' line, and highlight column if selected
	pad.addstr(gridrow,gridoffset," :Done  :Cancel")
	pad.addstr(gridrow,gridoffset,col_index[0])
	pad.addstr(gridrow,7+gridoffset,col_index[1])
	if len(upperchar)&(upperchar==col_index[0]): stdscr.addstr(gridrow,4+spaceout(col_index).find(upperchar),upperchar,curses.A_REVERSE)
	if len(upperchar)&(upperchar==col_index[1]): stdscr.addstr(gridrow,9+spaceout(col_index).find(upperchar),upperchar,curses.A_REVERSE)
	
	#Help banners
	pad.addstr(15,0,usagebanner)
	pad.addstr(16,0,(1+hx-len(shortcuts))*' '+shortcuts,curses.A_REVERSE)
	
	pad.refresh(padpos,0,ly,lx,hy,hx)

def main_draw():
	(max_y,max_x) = stdscr.getmaxyx()
	pad_draw(0,0,(max_y-2),(max_x-1))
	stdscr.move(max_y-1,0)
	curses.curs_set(0)
	stdscr.refresh()

##### MAIN LOOP: draw the interface and handle user input #####
cycle_index() #Don't start the program with unrandomized indexes
main_draw() # If this isn't done, the program initially shows nothing
while True:
	main_draw()
	c = stdscr.getkey()
	if c == '': quit()
	if c == '0': quit()
	if c == '9':
		hide_out -= hide_out+hide_out
		hide_out += 1
	#~ if ((c == '8')&(len(out)>=1)): out = out[:len(out)-1]
	if ((c == 'KEY_BACKSPACE')&(len(out)>=1)): out = out[:len(out)-1]
		
	#handle row/column selections
	if (string.uppercase.find(c)+1): upperchar = c
	if (row_index[:total_rows()].find(c)+1): lowerchar = c
	
	#if selection completes a pair, find choice, add to output, reset selection
	if len(upperchar)&len(lowerchar):
		#if selected pair chooses 'Done' or 'Cancel'
		if((upperchar==col_index[0])&(lowerchar==row_index[len(grid)+1])):
			quit(out+("\n"*newline)) #on 'Done', write output and exit
		if((upperchar==col_index[1])&(lowerchar==row_index[len(grid)+1])):
			quit() #on 'Cancel', exit without writing output
		
		
		rowchoice = row_index.find(lowerchar)
		if rowchoice < len(grid):
			if (grid[rowchoice].find("A") == 0):
				out += string.uppercase[col_index.find(upperchar)]
			if (grid[rowchoice].find("a") == 0):
				out += string.lowercase[col_index.find(upperchar)]
			if (grid[rowchoice].find("0") == 0)&(spaceout(col_index).find(upperchar) < len(numbers)):
				out += numbers[spaceout(col_index).find(upperchar)]
			if (grid[rowchoice].find("!") == 0):
				out += punct[spaceout(col_index).find(upperchar)]
			if (grid[rowchoice].find("_") == 0)&(spaceout(col_index).find(upperchar) < len(punct2)):
				out += punct2[spaceout(col_index).find(upperchar)]
		
		upperchar , lowerchar = '' , ''
		cycle_index()
