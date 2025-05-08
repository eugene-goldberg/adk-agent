#!/usr/bin/env python3
"""
Script to create a sample booking in the Firestore database.
"""

import datetime
import uuid
from google.cloud import firestore

# Initialize Firestore client
db = firestore.Client(project='pickuptruckapp')

# Generate a unique booking ID
booking_id = f"booking_{int(datetime.datetime.now().timestamp())}"

# Create a sample booking document
booking_data = {
    "id": booking_id,
    "customerId": "user123",
    "customerName": "Test Customer",
    "customerEmail": "test@example.com",
    "customerPhone": "+1-555-123-4567",
    "vehicleId": "vehicle_1746034884335",  # Using existing vehicle ID from your Firestore query result
    "vehicleMake": "Ford",
    "vehicleModel": "F-150",
    "vehicleYear": "2021",
    "ownerId": "s29gaZxv32ZVlO7wuXoAtxIAKo82",  # Using existing owner ID from your Firestore query result
    "ownerName": "Vehicle Owner",
    "pickupAddress": "123 Main St, Chicago, IL 60601",
    "destinationAddress": "456 Oak Ave, Chicago, IL 60611",
    "pickupDateTime": datetime.datetime.now() + datetime.timedelta(days=3),
    "estimatedHours": 3,
    "needsAssistance": True,
    "ridingAlong": True,
    "status": "confirmed",
    "totalCost": 210.00,
    "truckCost": 135.00,
    "assistanceCost": 75.00,
    "cargoDescription": "Couch, bed, dining table, and about 10 boxes",
    "createdAt": datetime.datetime.now(),
    "updatedAt": datetime.datetime.now()
}

# Add booking to Firestore
print(f"Creating booking with ID: {booking_id}")
db.collection('bookings').document(booking_id).set(booking_data)
print(f"Successfully created booking: {booking_id}")

# Verify by reading the booking back
booking_ref = db.collection('bookings').document(booking_id).get()
if booking_ref.exists:
    print(f"Verified booking exists: {booking_ref.to_dict()}")
else:
    print(f"Error: Could not verify booking {booking_id}")

print("\nVerifying bookings collection:")
bookings = list(db.collection('bookings').limit(10).stream())
print(f'Found {len(bookings)} booking documents:')
for doc in bookings:
    print(f'- {doc.id}: {doc.to_dict().get("status")}')