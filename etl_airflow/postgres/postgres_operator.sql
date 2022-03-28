CREATE TABLE raw_data_postgresql(
        id SERIAL PRIMARY KEY,
        year_month DATE NOT NULL,
        uf VARCHAR(20) NOT NULL,
        product VARCHAR(40) NOT NULL,
        unit CHAR(2) NOT NULL,
        volume DOUBLE PRECISION NOT NULL,
        created_at TIMESTAMP NOT NULL);

SELECT COUNT(*) FROM raw_data_postgresql;        
		
SELECT * FROM raw_data_postgresql;

DROP TABLE raw_data_postgresql;

COPY raw_data_postgresql (id, year_month, uf, product, unit, volume, created_at) 
FROM '/home/andreolv/airflow/dags/raw_data/raw_data.xlsx'
DELIMITER ',' 
CSV HEADER;

/*
ERROR:  could not open file "/home/andreolv/airflow/dags/raw_data/raw_data.xlsx" for reading: Permission denied
HINT:  COPY FROM instructs the PostgreSQL server process to read a file. You may want a client-side facility such as psql's \copy.
SQL state: 42501

Tentativas que não deram certo:
GRANT ALL PRIVILEGES ON TABLE raw_data_postgresql TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
*/