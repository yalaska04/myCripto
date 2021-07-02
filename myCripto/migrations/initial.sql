CREATE TABLE "movimientos" (
	"id"	INTEGER,
	"date"	TEXT NOT NULL,
	"time"	TEXT,
	"moneda_from"	TEXT NOT NULL,
	"cantidad_from"	REAL NOT NULL,
	"moneda_to"	TEXT NOT NULL,
	"cantidad_to"	REAL,
	PRIMARY KEY("id" AUTOINCREMENT)
)