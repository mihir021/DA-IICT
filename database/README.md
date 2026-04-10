# Database

This module owns MongoDB Atlas connectivity, collection constants, and seed helpers.

- Use `database.connection.get_database()` for all DB access
- Import collection names from `database.collections`
- Do not create Mongo clients anywhere else
