import fs from "fs";
import PocketBase from "pocketbase";
import {
    ADMIN_EMAIL, ADMIN_PASSWORD
} from "./secret.js"

export const pb = new PocketBase("http://127.0.0.1:8090");

const authData = await pb.admins
  .authWithPassword(ADMIN_EMAIL, ADMIN_PASSWORD)

if (!pb.authStore.isValid) {
    console.error("Authentication to PocketBase failed");
    process.exit(1);
}

// Function to read JSON file synchronously
export function readJSONFile(filename) {
  try {
    const data = fs.readFileSync(filename, "utf8");
    const jsonData = JSON.parse(data);
    return jsonData;
  } catch (error) {
    console.error("Error reading JSON file:", error.message);
    return undefined;
  }
}

export function processString(inputString) {
  if (inputString.length > 15) {
    throw new Error(
      "Id " + inputString + " is too long (more than 15 characters)"
    );
  } else {
    while (inputString.length < 15) {
      inputString += "_";
    }
    return inputString;
  }
}

// Replace 'example.json' with the path to your JSON file
const jsonFilename = "../../../results/animalia_tree.json";

// Read JSON file
export const jsonData = readJSONFile(jsonFilename);

export const getTaxonFilter = (parent) =>
`rank.name = "species" && image_path=true && path ~ "${parent}"`;