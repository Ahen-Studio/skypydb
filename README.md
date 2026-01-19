<h1><div align="center">
 <img alt="Skypy" width="auto" height="auto" src="https://github.com/amichyrpi/skypy-db/blob/main/docs/logo/dark.svg#gh-light-mode-only">
 <img alt="Skypy" width="auto" height="auto" src="https://github.com/amichyrpi/skypy-db/blob/main/docs/logo/dark.svg#gh-dark-mode-only">
</div></h1>

<p align="center">
    <b>Skypy - open-source reactive database</b>. <br />
    The better way to build Python logging system!
</p>

<p align="center">
  <a href="https://github.com/Ahen-Studio/skypy-db/blob/main/LICENSE" target="_blank">
      <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  </a> |
  <a>
        <img src="https://img.shields.io/github/downloads/Ahen-Studio/skypy-db/total" alt=Download>
  </a> |
  <a href="https://ahen.mintlify.app/" target="_blank">
      Docs
  </a>
</p>

```bash
pip install skypydb # python client
# or download from the source
# git clone https://github.com/Ahen-Studio/skypy-db.git
# cd skypy-db
# pip install -r requirements.txt
```

## Features

- Simple: Fully-typed, fully-tested, fully-documented

- Observable: Dashboard with real-time data, metrics, and query inspection

- Vector embeddings: Built-in embeddings and vector search

- Free & Open Source: MIT Licensed

## TODO

- [ ] code the database backend
- [ ] code the CLI tool to interact with the database without initializing it in code
- [ ] Create the dashboard using Reflex

## API

The API is only 4 functions:

- example without vector embeddings

```python
import skypydb

# setup skypydb client.
client = skypydb.Client(path="./data/skypy.db")

# Create table. get_table, delete_table are also available.
table = client.create_table("all-my-documents")

# Add docs to the table.
table.add(
    documents=[
        {
            "user_id": "user123",
            "message": "this is a document",
            "details": None,
            "ids": "auto"
        }
    ]
)

# Query results. You can also .get by the id of the document
results = table.query(
    query_texts=["This is a document"]# find the perfect match table 
)
```

- example with vector embeddings

```python
import skypydb

# setup skypydb client.
client = skypydb.Client(path="./data/skypy.db")

# Create table. get_table, delete_table are also available.
table = client.create_table("all-my-documents")

# setup the vector embeddings model.
vector = skypydb.Vector("all-MiniLM-L6-v2")

# Add docs to the table.
table.add(
    documents=[
        {
            "user_id": "user123",
            "message": "this is a document",
            "details": None,
            "ids": "auto",
            "vector": True
        }
    ]
)

# Search results. You can also .get by the id of the document
results = table.query(
    query_texts=["This is a document"],
    n_results=1,# finds the table with an embedding model
)
```

Learn more on our [Docs](https://ahen.mintlify.app/)

## Use case

For example, you can use Skypy-db to log information from your Python application.

1. Create a custom schema and add the logic to your code.
2. view your logs in real time on the dashboard.

## License

[MIT](./LICENSE)