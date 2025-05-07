import json
import os
import sys
import tarfile
import tempfile

import requests


def download_tgz(tgz_url, dest_path):
    print(f"Downloading {tgz_url}...")
    response = requests.get(tgz_url)
    response.raise_for_status()
    with open(dest_path, "wb") as f:
        f.write(response.content)
    print(f"Downloaded to {dest_path}")


def extract_tgz(tgz_path, extract_to):
    print(f"Extracting {tgz_path} to {extract_to}...")
    with tarfile.open(tgz_path, "r:gz") as tar:
        tar.extractall(path=extract_to)
    print("Extraction complete.")


def collect_fhir_files(example_folder_path):
    fhir_files = []
    for root, _, files in os.walk(example_folder_path):
        for file in files:
            if file.endswith(".json"):
                print(file)
                fhir_files.append(os.path.join(root, file))
    return fhir_files


def upload_fhir_files(fhir_files, server_url):
    failed_files = []

    for file_path in fhir_files:
        with open(file_path, "r") as f:
            try:
                resource = json.load(f)
                resourcetype = resource["resourceType"]
                _id = resource["id"]
            except (json.JSONDecodeError, KeyError):
                print(f"Skipping invalid or incomplete JSON: {file_path}")
                continue

            response = requests.put(f"{server_url}/{resourcetype}/{_id}", json=resource)
            if response.status_code in (200, 201):
                print(
                    f"Uploaded {os.path.basename(file_path)}: Success ({response.status_code})"
                )
            else:
                print(
                    f"Failed {os.path.basename(file_path)}: ({response.status_code}) - {response.text}"
                )
                failed_files.append(
                    {
                        "file": file_path,
                        "status": response.status_code,
                        "message": response.text,
                    }
                )

    return failed_files


def main():
    if len(sys.argv) != 3:
        print("Usage: python upload_fhir.py <tgz_file_url> <server_url>")
        sys.exit(1)

    tgz_file_url = sys.argv[1]
    server_url = sys.argv[2]

    with tempfile.TemporaryDirectory() as temp_dir:
        tgz_path = os.path.join(temp_dir, "package.tgz")
        download_tgz(tgz_file_url, tgz_path)
        extract_tgz(tgz_path, temp_dir)

        example_folder_path = os.path.join(temp_dir, "Package", "example")
        fhir_files = collect_fhir_files(example_folder_path)

        max_attempts = 4
        attempt = 1
        failed_files = [{"file": f} for f in fhir_files]

        while attempt <= max_attempts and failed_files:
            print(f"\nAttempt {attempt} - Uploading {len(failed_files)} files...")
            failed_paths = [f["file"] for f in failed_files]
            failed_files = upload_fhir_files(failed_paths, server_url)
            attempt += 1

        if failed_files:
            error_report = {"failed_uploads": failed_files, "attempts": attempt - 1}
            error_file_path = os.path.join(os.getcwd(), "upload_errors.json")
            with open(error_file_path, "w") as ef:
                json.dump(error_report, ef, indent=2)
            print(f"\n❌ Upload finished with errors. See details in {error_file_path}")
        else:
            print("\n✅ All files uploaded successfully.")


if __name__ == "__main__":
    main()

    # ▓▒░ ~   13:12  docker run jkiddo/ember
    # --location=https://hl7-eu.github.io/unicom-ig/package.tgz
    # --serverBase=https://sandbox.hl7europe.eu/unicom/fhir --docsAndLists=true
