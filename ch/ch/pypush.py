from pywebpush import generate_vapid_keys

# Generate VAPID keys
public_key, private_key = generate_vapid_keys()

# Print your VAPID keys (store them securely)
print(f"Public Key: {public_key}")
print(f"Private Key: {private_key}")
