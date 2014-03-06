library(RSQLite)

##
# Load data from database
##
DBFILE = "../db.sqlite3"

django_db <- dbConnect(dbDriver("SQLite"), DBFILE)

dbListTables(django_db)

farms_field <- dbGetQuery(django_db, "select * from farms_field")
farms_probe <- dbGetQuery(django_db, "select * from farms_probe")
farms_probereading <- dbGetQuery(django_db, "select * from farms_probereading")
