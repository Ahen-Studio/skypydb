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
git clone https://github.com/Ahen-Studio/skypy-db.git # python client
```

```bash
cd skypy-db
```

```bash
pip install -r requirements.txt # install dependencies
```

## Features

- Simple: Fully-typed, fully-tested, fully-documented

- Accessible: Dashboard to visualize real-time data

- Customization: Create custom schemas to visualize data in the dashboard

- Free & Open Source: MIT Licensed

## API

The API is only 4 functions:

```python
import skypydb
from datetime import datetime

client = skypydb.Client(path="./data/skypy.db")

collection = client.create_collection("all-my-documents")

collection.add(
    documents=[
        {
            "user_id": None,
            "message": "this is a document",
            "details": None,
            "creationtime": datetime.now().isoformat()
        }
    ]
)

results = collection.query(
    query_texts=["This is a document"],
    n_results=1,
)
```

Learn more on our [Docs](https://ahen.mintlify.app/)

## Use case

For example, you can use Skypy-db to log information from your Python application.

1. Create a custom schema and add the logic to your code.
2. view your logs in real time on the dashboard.

## License

[MIT](./LICENSE)