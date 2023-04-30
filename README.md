# CS4390-ServerBasedChat

## Current status
Client-to-server connection established.
Coming up: accepting multiple clients with the server.

**How to run:**
1. Open two or three terminal and locate the folder
2. Run `python server.py` in one terminal.
3. Run `python client.py` on the other terminals.
4. Enter username and secret key. Following are available usernames and secret key pairs: (clientA, 100), (clientB, 200), (clientC, 300).
5. Connection is made. Type commands from the provided options. (Log off, chat, end chat, history)
6. Type 'log off' to end session.

**In process:**
- Log off error check
- History

**Note:**
The `curses` module is not supported on Windows machines. While `curses` is most widely used in the Unix environment, versions are available for DOS, OS/2, and possibly other systems as well. This extension module is designed to match the API of `ncurses`, an open-source curses library hosted on Linux and the BSD variants of Unix.

To use `curses` module on Windows machines, simply install the library by:
```
pip install windows-curses
```
