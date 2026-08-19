from zenodo_get import download

# Download the PickleBall dataset
download(
    record_or_doi="16974645",
    output_dir="./models/benign/pickleball",
    file_glob="benign.tar.gz.part*",
)

download(
    record_or_doi="16974645",
    output_dir="./models/malicious/pickleball",
    file_glob="malicious.tar.gz",
)