# EHR DREAM Challenge Data Preparation Scripts

## Requirements
```
python >= 3.5
```

### Mortality Prediction OMOP preparation script

#### Running the python script
```
python Mortality-Prediction.py -f /path/to/omop/data/folder -p projectName
```

In case your server doesn't have python > 3.5, use the docker setup

Build and run the Docker container (This may take a while)
```
docker build -t ehr_dream_curation:v1 .
docker run -d -v /path/to/output/folder:/app/data:z -v /path/to/synthetic/data:/data:z,ro ehr_dream_curation:v1 python ./Mortality-Prediction.py -f /data -p projectName
```
