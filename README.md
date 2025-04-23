# Star_Wars_Chatbot
An API that allows users to ask questions to the OpenAI API, and will recieve an answer in the form of a character from Star Wars.

### How to run the code

In order to run this code, you will first need an API key. It is recommended to set the API key as an environment variable. This can be done as follows

```sh

$ export SUPER_SECRET_TOKEN=INSERT TOKEN HERE!
```

Once this has been done, the relevant docker containers can be set up as follows

```sh

$ docker compose build
$ docker compose up
```

Once this has been done, the API can be queried. To insert a new prompt, use the following command

```sh

curl -X POST http://localhost:8000/insert_prompt -H "Content-Type: application/json" -H "Authorization: Bearer $SUPER_SECRET_TOKEN" -d '{"prompt": "SOME_TEXT", "weight": 1}'
```

To chat with the LLM, use the following command

```sh

curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -H "Authorization: Bearer $SUPER_SECRET_TOKEN" -d '{"message": "Hey, I'\''ve been feeling really low today."}'
```

If the user did not set the API key as an environment variable, or chose a different name for their environment variable, they will need to modify the above commands accordingly.

### How to access the database

Once the docker containers are running, it is possible to access the database to view and edit the data stored there. In order to access the psql interactive shell, run the following command


```sh

docker exec -it postgres psql -U postgres -d db
```

From here, the user can run SQL queries as normal in order to view or edit the data in the database.
