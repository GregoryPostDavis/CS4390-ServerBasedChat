# CS4390-ServerBasedChat

**How to run:**
1. Open two or more terminals and locate the project folder.
2. Run code with command  python server.py in one terminal.
3. Run code with command python client.py in all other terminals.
4. Enter username and secret key.
5. Observe as the TCP connections are made. From the client terminals, type in commands. Following are available commands:
    - chat client-id: start a chat session with client-id.
    - end chat: end the current chat session.
    - history client-id: display the history of past messages with client-id. 
    - log off: tear down TCP connection and end connection.

Following are some aspects of the program to be aware of when testing:
- The program doesn’t consist of the subscription step as it is out of the scope of the project. Therefore, there is a list of pre-‘subscribed’ users and their secret key, implemented for simplicity of the verification process. They are (clientA, 100), (clientB, 200), (clientC, 300), and so on up to clientJ, counting up to 10 clients for clear validation. Use these to test.
- Server.py doesn’t terminate on its own. The UDP welcoming socket stays open so clients can create a TCP connection or tear it down at any time. In order to force the UDP socket closure, use ctrl+C.
- Although in a real-world setting, each client would have their inherent client-ID assigned by the server at subscription time, it wouldn’t be efficient to have ten different client.py files. Therefore, we designed a single client.py file that allows the user to input their client-ID (username) and the secret key (password) that can demonstrate various users logging onto the server.