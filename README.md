# CS4390-ServerBasedChat

## Current status
UDP socket creation and connection is working. When connected, The client will automatically send the HELLO message to the server.

**How to run:**
1. Open two terminal and locate the folder
2. `python server.py` first, check that server runs
3. `python client.py` on the other terminal.

## Upcoming Questions
1. Do we not need a case for initial subscription? (assigning clients IDs)
  - Currently the client IDs are hard coded into the client and the server.
  - Do we just need to test client A and B, or more cases of clients? (do we need a db?)
2. How is the server supposed to retrieve the client's secret key?
