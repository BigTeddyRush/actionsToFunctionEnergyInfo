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

## Azure Function
The Function used is a HTTP Trigger. When the Trigger is set, it will automaticly pull Data from Energy Charts Info and store it in a SQL Database. The connection is made via Managed Identities. The Data is also stored in the File data.py in this Repo, connected via Github Token. Also the Trigger runs the Github Action Workflow that deploys the Streamlit App on Dockerhub.

## Github Action
I used two Action Files. One to deploy the Function on Azure and one to Build and Deploy the Dockerfile

## Difficulties
I'm not quit sure how to connect to the SQL Server within the Container, so needed to add the data.py File. I know that this aint the best way...
