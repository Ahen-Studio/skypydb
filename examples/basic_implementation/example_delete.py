import skypydb

# Create a client
client = skypydb.Client()

# Create tables from the schema
# This reads the schema from skypydb/schema.py and creates all tables
tables = client.create_table()

# Access your tables
success_table = tables["success"]
warning_table = tables["warning"]
error_table = tables["error"]

# delete data on the table assuming they are already data in the table.
success_table.delete(
    component="AuthService",
    user_id="user123"
)
