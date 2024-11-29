cd src/etl
zip -r etl.zip ./*
aws s3 cp etl.zip s3://your-etl-bucket/