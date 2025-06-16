# Backend Interview Project

Messaging API using Flask and Postgres

## Running The App

0. Install Docker Desktop
1. Add required creds/fields to `.env` file (copy structure from `.env.sample`)
2. Run `make up` to build and start the app
3. Run `make down` bring the app down and remove the containers
4. Run `make stop`  or ctrl-C to halt the app
5. Run `make start` resume a stopped app (must use `make up` if import/package changes)
6. Run `python test_reqs.py` to hit the endpoints with examples (while api is up)
7. Run `python test_client_handling.py` to run provider client unit tests

## Using the API

*Full Example Requests found in `test_reqs.py`

Request the following to send mesasges via the cooresponding provider client API:
- `POST /api/messages/sms`
- `POST /api/messages/email`

(Saves messages to DB, sends them via provider client, tries to update id)



Request the following to simulate webhooks listening to inbound messages:
- `POST /api/messages/sms`
- `POST /api/messages/email`

(This simply records them in the DB)



Request the following to Query the DB:
- `GET /api/conversations`
- `GET /api/conversations/<uuid:conversation_id>/messages`

(Read Only)


## Requirements (from original ReadMe)

The service should implement:

- **Unified Messaging API**: HTTP endpoints to send and receive messages from both SMS/MMS and Email providers
  - Support sending messages through the appropriate provider based on message type
  - Handle incoming webhook messages from both providers
- **Conversation Management**: Messages should be automatically grouped into conversations based on participants (from/to addresses)
- **Data Persistence**: All conversations and messages must be stored in a relational database with proper relationships and indexing