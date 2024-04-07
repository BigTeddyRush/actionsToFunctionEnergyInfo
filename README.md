# actionsToFunctionEnergyInfo

## Managed Identities

- Activate system assigned identity in the function app
- add user to the admin of the SQL Server
- add user to the database

```
CREATE USER [user@domain] FROM EXTERNAL PROVIDER;
ALTER ROLE db_datareader ADD MEMBER [user@domain];
ALTER ROLE db_datawriter ADD MEMBER [user@domain];
ALTER ROLE db_ddladmin ADD MEMBER [user@domain];
GO
```

- see following link: https://hedihargam.medium.com/python-sql-database-access-with-managed-identity-from-azure-web-app-functions-14566e5a0f1a
