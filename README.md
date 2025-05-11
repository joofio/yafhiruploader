# yafhiruploader

Yet Another FHIR IG Uploader
Clearly inspired by the top notch ones:
1. [https://github.com/jkiddo/ember](https://github.com/jkiddo/ember)
2. [https://github.com/brianpos/UploadFIG](https://github.com/brianpos/UploadFIG)

### How to

#### docker 
```bash
docker run --rm \
    -e TGZ_FILE_URL=https://example.com/package.tgz \
    -e SERVER_URL=https://fhirserver.com/fhir \
    jfcal/yafhiriguploader
```
 or for different container only on localhost:
 ```bash
docker run --rm \
    -e TGZ_FILE_URL=https://build.fhir.org/ig/hl7-eu/gravitate-health/package.tgz \
    -e SERVER_URL=http://host.docker.internal:8787/fhir -e WAITTIME=0 \
    jfcal/yafhiriguploader
```

or mapping the volumes:
 ```bash
docker run --rm \
    -e TGZ_FILE_URL=https://build.fhir.org/ig/hl7-eu/gravitate-health/package.tgz \
    -e SERVER_URL=http://host.docker.internal:8787/fhir -e WAITTIME=0 -v ./fhir-output:/app/output \
    jfcal/yafhiriguploader
```


#### directly from the python
or 
```python upload_fhir.py https://example.com/file.tgz https://server.com --separate_bundles False```

