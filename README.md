gridfire
========

Keylogger-resistant text entry system

## About Gridfire

Gridfire was inspired by gpggrid, a program included in [Tinfoil Hat Linux](http://en.wikipedia.org/wiki/Tinfoil_Hat_Linux).  Both programs are intended to allow for users to enter sensitive information (mainly passwords) in untrusted situations, by obscuring the entered text.  This is accomplished by presenting a grid of characters to the user, who then selects from it by entering pairs of randomized upper- and lowercase letters to specify the column and row of the desired character.

For example, this allows a user to enter their password of `s3cr37` while a keylogger or shoulder-surfing busybody might only see grid coordinates, such as `eFyYqRbAjEiT`.  Since both programs randomize which letters correspond to which row/column between each entered character, this makes it difficult for such an attacker to reconstruct what was entered.  

### What Gridfire does

By itself, gridfire presents a grid of characters (from specified sets, see section **Using Gridfire: Character Sets** below) to the user, builds a string of characters chosen by the user, and returns the string when finished.  It is intended for gridfire to be used by other scripts and programs to secure input against keystroke-monitoring attacks.  

## Using Gridfire

## Options

### Indexing methods
* `-0`, Method 0 (Not shuffled or offset - A is first column, B is second, etc)
* `-1`, Method 1 (In order but randomly offset after each entry)
* `-2`, Method 2 (One set of randomly shuffled letters used for columns and rows)
* `-3`, Method 3 (Two sets of randomly shuffled letters used for columns and rows)

If no method is specified, gridfire uses 3 by default.  

### Character Sets
* `-u`, Uppercase latin letters (A-Z)
* `-l`, Lowercase latin letters (a-z)
* `-p`, Punctuation
* `-w`, Whitespace characters (Space, tab, etc)
* `-b`, Binary digits (0 and 1)
* `-o`, Octal digits (0-7)
* `-d`, Decimal digits (0-9)
* `-f`, Hexadecimal digits (0-9 + a-f + A-F)

If no character sets are specified, gridfire displays the uppercase, lowercase, decimal digits, punctuation, and whitespace sets.  If multiple digit sets are specified, gridfire displays the largest chosen set.

### Behavior options

* `-c`, Forces hiding of entered text.
* `-g` or `--grid`, Ignores other options and attempts to behave like gpggrid.  Not yet implemented.
* `-n`, Appends a newline to returned text when finished.
* `-t`, Training mode - does not return entered text when finished.  Not yet implemented.

## License
Gridfire is distributed under the GNU Affero General Public License version 3.  See included `LICENSE` file for details.