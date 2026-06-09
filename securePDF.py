"""
=======================================================
  SECURE PDF GENERATOR — Production Level
  Har user ko alag password wala PDF milega
  Copy / Print / Modify — sab BLOCKED
=======================================================

Usage:
    python secure_pdf_generator.py

Input:
    - source_document.pdf  (jo PDF distribute karni hai)
    - users.csv            (naam aur email list)

Output:
    - output/ folder mein har user ka encrypted PDF
    - output/password_log.csv  (passwords ki log — safely rakho!)
"""

import csv
import os
import random
import string
from datetime import datetime
from pypdf import PdfReader, PdfWriter


# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────
SOURCE_PDF       = "source_document.pdf"   # Original PDF
OUTPUT_FOLDER    = "output"                # Output folder
PASSWORD_LOG     = "output/password_log.csv"
PASSWORD_LENGTH  = 12                      # Password kitna lamba ho


def generate_password(length=PASSWORD_LENGTH):
    """Strong random password generate karo"""
    chars = string.ascii_letters + string.digits + "!@#$%"
    # Ensure at least one of each type
    password = [
        random.choice(string.ascii_uppercase),
        random.choice(string.ascii_lowercase),
        random.choice(string.digits),
        random.choice("!@#$%"),
    ]
    password += random.choices(chars, k=length - 4)
    random.shuffle(password)
    return "".join(password)


def create_encrypted_pdf(source_path, output_path, user_password):
    """
    PDF encrypt karo with:
      - User password (sirf open karne ke liye)
      - Owner password (modify/copy/print ke liye — RANDOM, kisi ko nahi dena)
      - Print: BLOCKED
      - Copy: BLOCKED
      - Modify: BLOCKED
      - Annotations: BLOCKED
    """
    reader = PdfReader(source_path)
    writer = PdfWriter()

    # Saare pages copy karo
    for page in reader.pages:
        writer.add_page(page)

    # Owner password = random strong password (koi nahi jaanta)
    # Isse copy/print restrictions actually enforce hoti hain
    owner_password = generate_password(20)

    # Encryption with restrictions
    writer.encrypt(
        user_password=user_password,
        owner_password=owner_password,
        use_128bit=True,
        permissions_flag=0  # 0 = SARE permissions BLOCKED
        # permissions_flag breakdown:
        # Bit 3 = Print          -> 0 = blocked
        # Bit 4 = Modify         -> 0 = blocked
        # Bit 5 = Copy           -> 0 = blocked
        # Bit 6 = Annotations    -> 0 = blocked
        # All 0 = maximum restriction
    )

    with open(output_path, "wb") as f:
        writer.write(f)


def load_users(csv_path="users.csv"):
    """CSV se user list load karo"""
    users = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            users.append(row)
    return users


def generate_for_all_users():
    """Main function — sare users ke liye PDF generate karo"""

    # Output folder banao
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    # Users load karo
    if not os.path.exists("users.csv"):
        # Demo users banao agar file nahi hai
        print("users.csv nahi mili — demo users use kar raha hoon...")
        users = [
            {"name": "Aagnik Chanda",   "email": "aagnick@gmail.com"} 
        ]
    else:
        users = load_users("users.csv")

    if not os.path.exists(SOURCE_PDF):
        print(f"ERROR: {SOURCE_PDF} nahi mili!")
        return

    # Password log file
    log_rows = []

    print(f"\n{'='*55}")
    print(f"  SECURE PDF GENERATOR")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*55}\n")

    for i, user in enumerate(users, 1):
        name  = user.get("name", f"User_{i}")
        email = user.get("email", f"user{i}@example.com")

        # Safe filename (spaces hataao)
        safe_name = name.replace(" ", "_").lower()
        output_filename = f"{OUTPUT_FOLDER}/{safe_name}_confidential.pdf"

        # Unique password generate karo
        password = generate_password()

        # PDF banao
        create_encrypted_pdf(SOURCE_PDF, output_filename, password)

        # Log mein save karo
        log_rows.append({
            "name":       name,
            "email":      email,
            "password":   password,
            "filename":   output_filename,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        print(f"  ✓ [{i}/{len(users)}] {name}")
        print(f"       File:     {output_filename}")
        print(f"       Password: {password}\n")

    # Password log CSV save karo
    with open(PASSWORD_LOG, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["name", "email", "password", "filename", "created_at"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(log_rows)

    print(f"{'='*55}")
    print(f"  COMPLETE! {len(users)} PDFs generate ho gayi")
    print(f"  Password log: {PASSWORD_LOG}")
    print(f"{'='*55}\n")
    print("  ⚠️ Protect the  password_log.csv \n")


if __name__ == "__main__":
    generate_for_all_users()




#{"name": "Priya Verma",    "email": "priya@example.com"},
#{"name": "Amit Patel",     "email": "amit@example.com"},
#{"name": "Neha Singh",     "email": "neha@example.com"},
