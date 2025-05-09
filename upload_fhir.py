import argparse
import json
import os
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
    if len(fhir_files) == 0:
        raise Exception("No examples files found", example_folder_path)
    return fhir_files


def upload_fhir_files(fhir_files, server_url, separate_bundles=True):
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

            if resourcetype == "Bundle" and separate_bundles:
                for inner_resource in resource["entry"]:
                    inner_resource_id = inner_resource["resource"]["id"]
                    inner_resource_type = inner_resource["resource"]["resourceType"]
                    response = requests.put(
                        f"{server_url}/{inner_resource_type}/{inner_resource_id}",
                        json=inner_resource["resource"],
                    )
                    if response.status_code in (200, 201):
                        print(
                            f"Uploaded {os.path.basename(file_path)}: INNER RESOURCE: {inner_resource_type}-{inner_resource_id}: Success ({response.status_code})"
                        )
                    else:
                        print(
                            f"Failed {os.path.basename(file_path)}: INNER RESOURCE: {inner_resource_type}-{inner_resource_id}: ({response.status_code}) - {response.text}"
                        )
                        failed_files.append(
                            {
                                "file": file_path,
                                "status": response.status_code,
                                "message": response.text,
                            }
                        )
            else:
                response = requests.put(
                    f"{server_url}/{resourcetype}/{_id}", json=resource
                )

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
    parser = argparse.ArgumentParser(
        description="Upload FHIR resources from a tgz file."
    )
    parser.add_argument("tgz_file_url", help="URL of the .tgz package")
    parser.add_argument("server_url", help="FHIR server base URL")
    parser.add_argument(
        "--separate_bundles",
        default=True,
        help="Split bundles into individual resources to post",
    )

    args = parser.parse_args()

    tgz_file_url = args.tgz_file_url
    server_url = args.server_url
    separate_bundles = args.separate_bundles

    print(f"TGZ URL: {tgz_file_url}")
    print(f"Server URL: {server_url}")
    print(f"Optional Param: {separate_bundles}")

    with tempfile.TemporaryDirectory() as temp_dir:
        tgz_path = os.path.join(temp_dir, "package.tgz")
        download_tgz(tgz_file_url, tgz_path)
        extract_tgz(tgz_path, temp_dir)

        example_folder_path = os.path.join(temp_dir, "package", "example")
        fhir_files = collect_fhir_files(example_folder_path)

        max_attempts = 4
        attempt = 1
        failed_files = [{"file": f} for f in fhir_files]
        # print(bool(failed_files))
        while attempt <= max_attempts and failed_files:
            print(f"\nAttempt {attempt} - Uploading {len(failed_files)} files...")
            failed_paths = [f["file"] for f in failed_files]
            failed_files = upload_fhir_files(failed_paths, server_url, separate_bundles)
            attempt += 1

        if failed_files:
            error_report = {"failed_uploads": failed_files, "attempts": attempt - 1}

            # Define the output directory
            output_dir = os.path.join(os.getcwd(), "output")
            os.makedirs(
                output_dir, exist_ok=True
            )  # Create the directory if it doesn't exist

            # Define the error file path inside the output directory
            error_file_path = os.path.join(output_dir, "upload_errors.json")

            # Write the error report
            with open(error_file_path, "w") as ef:
                json.dump(error_report, ef, indent=2)

            print(f"\n❌ Upload finished with errors. See details in {error_file_path}")
        else:
            print("\n✅ All files uploaded successfully.")


if __name__ == "__main__":
    main()
