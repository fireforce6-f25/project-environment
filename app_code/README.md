# Get Dependencies Script

This script fetches the dependencies from the .settings.yaml file of each repo in the fireforce6-f25 organization using the GitHub API and GitHub app that was installed to the organization. Follow the steps below to set it up and run.

## Setup python virtual environment 

First, create the virtual environment.

```bash
python3 -m venv venv
source venv/bin/activate
```

Then, `pip install` the requirements.

```bash
pip3 install -r requirements.txt
```

## Create a `.env` file

These values will be read by the python script. The below values are the only ones needed, so use the following as a base stub for your `.env` file.

```bash
PEM=
CLIENT_ID=
INSTALLATION_ID=
```

 - `PEM`: The path to the `.pem` file of the private key associated with the github app.
 - `CLIENT_ID`: Can be found in the github UI, the client id of the github app itself.
 - `INSTALLATION_ID`: The installation id of the specific install instance to the organization.

## Run the script

```bash
python3 get-dependencies.py
```
