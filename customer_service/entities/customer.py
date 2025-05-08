# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Customer entity module for Pickup Truck App."""

from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict
import json


class SavedAddress(BaseModel):
    """
    Represents a customer's saved address.
    """
    home: Optional[str] = None
    work: Optional[str] = None
    other: Optional[List[str]] = None
    model_config = ConfigDict(from_attributes=True)


class NotificationPreferences(BaseModel):
    """
    Represents a customer's notification preferences.
    """
    email: bool = True
    sms: bool = True
    push: bool = True
    model_config = ConfigDict(from_attributes=True)


class Vehicle(BaseModel):
    """
    Represents a vehicle in the system.
    """
    id: str
    ownerId: str
    type: Literal['pickup', 'van', 'box truck', 'flatbed', 'other']
    make: str
    model: str
    year: str
    licensePlate: str
    capacity: str
    hourlyRate: float
    offerAssistance: bool
    assistanceRate: Optional[float] = None
    isActive: bool
    photos: Dict[str, str] = Field(default_factory=dict)
    model_config = ConfigDict(from_attributes=True)


class BookingInfo(BaseModel):
    """
    Represents a booking in a customer's history
    """
    id: str
    vehicleId: str
    pickupAddress: str
    destinationAddress: str
    pickupDateTime: str
    estimatedHours: int
    needsAssistance: bool
    ridingAlong: bool
    status: Literal['pending', 'confirmed', 'in-progress', 'completed', 'cancelled', 'declined']
    totalCost: float
    cargoDescription: str
    assistanceCost: Optional[float] = None
    notes: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class CustomerProfile(BaseModel):
    """
    Represents a customer profile.
    """
    uid: str
    name: str
    email: str
    phone: Optional[str] = None
    role: Literal['user'] = 'user'
    createdAt: str
    updatedAt: str
    profilePicture: Optional[str] = None
    hasCompletedOnboarding: bool
    preferredNotifications: Optional[NotificationPreferences] = None
    savedAddresses: Optional[SavedAddress] = None
    model_config = ConfigDict(from_attributes=True)


class Customer(BaseModel):
    """
    Represents a customer in the Pickup Truck App.
    """
    profile: CustomerProfile
    bookings: List[BookingInfo] = Field(default_factory=list)
    favoriteVehicles: List[str] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)

    def to_json(self) -> str:
        """
        Converts the Customer object to a JSON string.

        Returns:
            A JSON string representing the Customer object.
        """
        return self.model_dump_json(indent=4)

    @staticmethod
    def get_customer(current_customer_id: str) -> "Customer":
        """
        Retrieves a customer based on their ID.

        Args:
            customer_id: The ID of the customer to retrieve.

        Returns:
            The Customer object if found, None otherwise.
        """
        # In a real application, this would involve a Firestore lookup.
        # For this example, we'll return a dummy customer for the truck sharing app.
        return Customer(
            profile=CustomerProfile(
                uid=current_customer_id,
                name="Alex Johnson",
                email="alex.johnson@example.com",
                phone="+1-702-555-1212",
                role="user",
                createdAt="2024-01-15T10:30:00Z",
                updatedAt="2024-05-01T14:22:00Z",
                profilePicture="https://example.com/profiles/alex.jpg",
                hasCompletedOnboarding=True,
                preferredNotifications=NotificationPreferences(
                    email=True,
                    sms=True,
                    push=True
                ),
                savedAddresses=SavedAddress(
                    home="123 Main St, Anytown, CA 12345",
                    work="456 Business Ave, Commerce City, CA 12345",
                    other=["789 Vacation Dr, Beach City, FL 98765"]
                )
            ),
            bookings=[
                BookingInfo(
                    id="booking123",
                    vehicleId="vehicle456",
                    pickupAddress="123 Main St, Anytown, CA 12345",
                    destinationAddress="789 Storage Ln, Anytown, CA 12345",
                    pickupDateTime="2024-04-15T10:00:00Z",
                    estimatedHours=3,
                    needsAssistance=True,
                    ridingAlong=True,
                    status="completed",
                    totalCost=175.00,
                    cargoDescription="Moving furniture from apartment to storage",
                    assistanceCost=75.00
                ),
                BookingInfo(
                    id="booking124",
                    vehicleId="vehicle789",
                    pickupAddress="456 Business Ave, Commerce City, CA 12345",
                    destinationAddress="321 New Home St, Anytown, CA 12345",
                    pickupDateTime="2024-05-20T09:00:00Z",
                    estimatedHours=5,
                    needsAssistance=True,
                    ridingAlong=True,
                    status="confirmed",
                    totalCost=325.00,
                    cargoDescription="Moving office furniture to new location",
                    assistanceCost=125.00
                )
            ],
            favoriteVehicles=["vehicle456", "vehicle789"]
        )