# This is not actual dockerfile content, just commands to run
# to set up the environment for the Flask app.
pip3 install Flask Flask-PyMongo
python3 app.py
docker run -d \ \
    --name mongo_dev \
    -p 27017:27017 \
    -e MONGO_INITDB_ROOT_USERNAME=admin \
    -e MONGO_INITDB_ROOT_PASSWORD=password \
    mongo