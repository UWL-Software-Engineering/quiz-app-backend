docker exec -it quiz-app-mongo mongo -u admin -p
# Enter the MongoDB root password when prompted

use admin;
db.createUser({
  user: "user",
  pwd: "password",
  roles: [
    { role: "readWrite", db: "quiz-app" }
  ]
});

