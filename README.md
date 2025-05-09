# yafhiruploader

Yet Another FHIR IG Uploader
Clearly inspired by the top notch ones:
1. [https://github.com/jkiddo/ember](https://github.com/jkiddo/ember)
2. [https://github.com/brianpos/UploadFIG](https://github.com/brianpos/UploadFIG)

### How to

```bash
docker run --rm \
    -e TGZ_FILE_URL=https://example.com/package.tgz \
    -e SERVER_URL=https://fhirserver.com/fhir \
    jfcal/yafhiriguploader
```

or 
```python upload_fhir.py https://example.com/file.tgz https://server.com --separate_bundles False```

