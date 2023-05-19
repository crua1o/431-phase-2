import csv
import hashlib


def hash_password(password):
    """
    Hashes a password using the SHA256 algorithm.

    Args:
        password (str): The password to be hashed.

    Returns:
        str: The hashed password.
    """
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


# Define the input and output file paths
input_file = 'Users.csv'
output_file = 'hashed-output.csv'

# Open the input and output files
with open(input_file, 'r', newline='') as in_file, open(output_file, 'w', newline='') as out_file:
    # Create a CSV reader and writer
    reader = csv.DictReader(in_file)
    writer = csv.DictWriter(out_file, fieldnames=['email', 'password_hash'])
    
    # Write the header row to the output file
    writer.writeheader()
    
    # Process each row in the input file
    for row in reader:
        # Hash the password using SHA256
        password_hash = hash_password(row['password'])
        
        # Get the email address from the input file
        # \ufeff prefix was found when printing the row information
        user_email = row['\ufeffemail']
        
        # Write the email and hashed password to the output file
        writer.writerow({'email': user_email, 'password_hash': password_hash})

"""

The hashed passwords will be written to a new .csv file called output.csv in the same directory as the script.
Note: This script assumes that the input file has columns named "email" and "password". 

"""