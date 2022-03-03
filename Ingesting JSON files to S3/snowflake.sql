--CREATE STORAGE INTEGRATION
CREATE OR REPLACE STORAGE INTEGRATION s3int
  TYPE = EXTERNAL_STAGE
  STORAGE_PROVIDER = S3
  ENABLED = TRUE
  STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::997648566872:role/rolesnowflake'
  STORAGE_ALLOWED_LOCATIONS = ('s3://andreyempresa');
                               
DESC INTEGRATION s3int;

--CREATE DATABASE
CREATE OR REPLACE DATABASE andrey_db;

--CREATE A STAGE
CREATE OR REPLACE STAGE andrey_db.public.temp_stage
  URL = 's3://andreyempresa'
  storage_integration = s3int;

SHOW stages;

--CREATE TARGET TABLE FOR JSON DATA WITH SCHEMA
CREATE OR REPLACE TABLE andrey_db.public.LANDING_TABLE(
    id varchar(100),
    name varchar(100), 
    idade varchar(100), 
    credito_solicitado varchar(100), 
    data_solicitacao varchar(100))

select system$get_aws_sns_iam_policy('arn:aws:sns:us-east-1:997648566872:snowflak');

--CREATE A PIPE TO INGEST DATA
CREATE OR REPLACE PIPE andrey_db.public.mypipe auto_ingest=true as
    COPY INTO andrey_db.public.LANDING_TABLE
    FROM @andrey_db.public.temp_stage
    file_format = (type = 'JSON' strip_outer_array = true);    

 
 --json_extract_path_text(jsondata, 'clientes'))
   
SHOW pipes;

--CHECK PIPE STATUS
SELECT SYSTEM$PIPE_STATUS('snowpipe.public.LANDING_TABLE');

--SHOW TABLE
SELECT * FROM snowpipe.public.LANDING_TABLE;

--VIEW TABLE SIZE
SELECT array_size(jsontext:clientes) FROM snowpipe.public.LANDING_TABLE

/*
SELECT 
    cl.value:id::string as id,
    cl.value:name::string as name, 
    cl.value:idade::string as idade, 
    cl.value:credito_solicitado::string as credito_solicitado, 
    cl.value:data_solicitacao::string as data_solicitacao 
FROM snowpipe.public.LANDING_TABLE,
    table(flatten(jsontext:clientes)) cl;
*/

