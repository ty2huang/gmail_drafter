# Gmail Drafter

Before getting started, you need to create a GCP (Google Cloud Platform) project and enable the Gmail API. See instructions here: https://developers.google.com/workspace/guides/create-project

After that create credentials using instructions here: https://developers.google.com/workspace/guides/create-credentials#create_a_oauth_client_id_credential

FOLLOW THE SECTION THAT SAYS `Create a OAuth client ID credential` and `Create Desktop application credentials`. This is VERY IMPORTANT as creating credentials under any other section will not work.

After you created the credentials, download the file and save it under the root folder of the repo as `credentials.json`.

If you are still getting "access denied" errors, you can add your email as a "Test User" in the "APIs and services > OAuth consent screen" page.

DO NOT UPLOAD THIS FILE TO THE REPO! This is included in .gitignore so you just need to verify the json file is named correctly.

