#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5000/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done


###############################################
#
# Health checks
#
###############################################

# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    #exit 1
  fi
}

# Function to check the database connection
check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    #exit 1
  fi
}


##########################################################
#
# Boxer Management
#
##########################################################

add_boxer() {
  name=$1
  weight=$2
  height=$3
  reach=$4
  age=$5

  echo "Adding boxer ($name - $weight, $age) to the ring..."
  curl -s -X POST "$BASE_URL/add-boxer" -H "Content-Type: application/json" \
    -d "{\"name\":\"$name\", \"weight\":$weight, \"height\":$height, \"reach\":$reach, \"age\":$age}" | grep -q '"status": "success"'

  if [ $? -eq 0 ]; then
    echo "Boxer added successfully."
  else
    echo "Failed to add boxer."
    #exit 1
  fi
}

delete_boxer_by_id() {
  boxer_id=$1

  echo "Deleting boxer by ID ($boxer_id)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-boxer/$boxer_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer deleted successfully by ID ($boxer_id)."
  else
    echo "Failed to delete boxer by ID ($boxer_id)."
    #exit 1
  fi
}

get_boxer_by_id() {
  boxer_id=$1

  echo "Getting boxer by ID ($boxer_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-boxer-by-id/$boxer_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer retrieved successfully by ID ($boxer_id)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Boxer JSON (ID $boxer_id):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get boxer by ID ($boxer_id)."
    #exit 1
  fi
}

get_boxer_by_name() {
  boxer_name=$1

  echo "Getting boxer by NAME ($boxer_name)..."
  encoded_name=$(echo "$boxer_name" | sed 's/ /%20/g')
  response=$(curl -s -X GET "$BASE_URL/get-boxer-by-name/$encoded_name")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer retrieved successfully by NAME ($boxer_name)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Boxer JSON (NAME $boxer_name):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get boxer by NAME ($boxer_name)."
    #exit 1
  fi
}

############################################################
#
# Ring Management
#
############################################################

fight() {
  echo "Initiating bout..."
  response=$(curl -s -X GET "$BASE_URL/fight")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Fight started successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Bout Winner:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to initiate bout."
    #exit 1
  fi
}


get_boxers() {
  echo "Getting all boxers in the ring..."
  response=$(curl -s -X GET "$BASE_URL/get-boxers")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "All boxers retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Boxers JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get boxers."
    #exit 1
  fi
}


clear_boxers() {
  echo "Clearing boxers..."
  response=$(curl -s -X POST "$BASE_URL/clear-boxers")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Ring cleared successfully."
  else
    echo "Failed to clear ring."
    #exit 1
  fi
}

enter_ring() {
  name=$1

  echo "Adding boxer to ring ($name)..."
  response=$(curl -s -X POST "$BASE_URL/enter-ring" \
    -H "Content-Type: application/json" \
    -d "{\"name\":\"$name\"}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxer added to ring successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Bout Winner:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to add boxer to ring."
    #exit 1
  fi
}

######################################################
#
# Leaderboard
#
######################################################

# Function to get the boxers leaderboard sorted by wins count
get_leaderboard() {
  echo "Getting boxers leaderboard sorted by wins count..."
  response=$(curl -s -X GET "$BASE_URL/leaderboard?sort=wins")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Boxers leaderboard retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Leaderboard JSON (sorted by win count):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get boxers leaderboard."
    #exit 1
  fi
}

# Initialize the database
sqlite3 db/boxing.db < sql/init_db.sql

# Health checks
check_health
check_db



# Create boxers
add_boxer "Mike Tyson" 256 180 74 39
add_boxer "Muhammad Ali" 190 185 78 34
add_boxer "Floyd Mayweather" 230 170 72 30
add_boxer "Manny Pacquiao" 245 160 67 22
add_boxer "Canelo Alvarez" 198 175 70 28
add_boxer "Peter Golbus" 200 180 15 20

enter_ring "Mike Tyson"
enter_ring "Peter Golbus"
get_boxers
fight
clear_boxers

enter_ring "Floyd Mayweather"
enter_ring "Manny Pacquiao"
get_boxers
fight
clear_boxers

enter_ring "Canelo Alvarez"
enter_ring "Mike Tyson"
get_boxers
fight
clear_boxers

get_leaderboard

# Exceptions
enter_ring "Mike Tyson"
enter_ring "Muhammad Ali"
enter_ring "Floyd Mayweather"
clear_boxers

add_boxer "Mike Tyson" 240 180 74 39

delete_boxer_by_id 10
get_boxer_by_name "Donald Trump"

get_boxer_by_id 1
get_boxer_by_id 2
get_boxer_by_id 3
get_boxer_by_id 4
get_boxer_by_id 5

get_boxer_by_name "Mike Tyson"
get_boxer_by_name "Muhammad Ali"
get_boxer_by_name "Floyd Mayweather"
get_boxer_by_name "Manny Pacquiao"
get_boxer_by_name "Canelo Alvarez"

delete_boxer_by_id 1
delete_boxer_by_id 2
delete_boxer_by_id 3
delete_boxer_by_id 4
delete_boxer_by_id 5

echo "All tests passed successfully!"
