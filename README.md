# Packages

Flask  
datetime 
Flask-SQLAlchemy
PyJWT

# Endpoints

/register -- For signup methods GET, POST
/login -- For login methods GET, POST
/records/<string:bookname> -- For fetching reviews methods GET
/records/delete/<int:id> -- For deleting reviews methods DELETE
/records/add -- For adding reviews methods POST
/records/update/<int:id> -- For updating reviews methods PUT