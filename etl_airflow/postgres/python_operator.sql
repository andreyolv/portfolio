CREATE TABLE raw_data_sqlalchemy(
        id SERIAL PRIMARY KEY,
        year_month DATE NOT NULL,
        uf VARCHAR(20) NOT NULL,
        product VARCHAR(40) NOT NULL,
        unit CHAR(2) NOT NULL,
        volume DOUBLE PRECISION NOT NULL,
        created_at TIMESTAMP NOT NULL);

SELECT COUNT(*) FROM raw_data_sqlalchemy;        
		
SELECT * FROM raw_data_sqlalchemy;

DROP TABLE raw_data_sqlalchemy;