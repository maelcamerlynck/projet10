# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.


class BookingDetails:
    def __init__(
        self,
        destination: str = None,
        origin: str = None,
        travel_date: str = None,
        travel_date_back: str = None,
        money: str = None,
            unsupported_airports=None,
    ):
        if unsupported_airports is None:
            unsupported_airports = []
            
        self.destination = destination
        self.origin = origin
        self.travel_date = travel_date
        self.travel_date_back = travel_date_back
        self.money = money
        self.unsupported_airports = unsupported_airports
