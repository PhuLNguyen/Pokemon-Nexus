// Switch to the target database. MongoDB will create it on first use (first insertion/collection creation).
// NOTE: If you define MONGO_INITDB_DATABASE in docker-compose.yml, this line is optional 
// as the script will default to that DB, but it's good practice.
db = db.getSiblingDB('PokemonNexusDB'); 

// 1. Create a User for the Application (optional, but highly recommended for security)
db.createUser(
  {
    user: "pythonFlaskApp", // Application username
    pwd: "securePassword123",
    roles: [
      { role: "readWrite", db: "PokemonNexusDB" } // Grant read/write access to the new database
    ]
  }
);

// 2. Create a Collection (Optional, MongoDB is schema-less and creates collections on first insert)
// db.createCollection('users');

print("Initialization script finished successfully.");