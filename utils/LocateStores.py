import json
import requests
from math import cos, asin, sqrt, pi

# Locate stores nearby.
class LocateStores:

    @staticmethod
    def distance(latitude_1: float, longitude_1: float, latitude_2: float, longitude_2: float):
        # Diameter of the earth in KMs.
        earth_diameter_kms = 12742
        # Factor to convert an angle from degrees to radians.
        p = 0.017453292519943295 # (pi / 180)
        # Haversine
        hav = (
                0.5
                - cos((latitude_2 - latitude_1) * p) / 2
                + cos(latitude_1 * p) * cos(latitude_2 * p) * (1 - cos((longitude_2 - longitude_1) * p)) / 2
        )
        # Return the distance.
        return earth_diameter_kms * asin(sqrt(hav))

    @staticmethod
    def get_stores_nearby(lat: float, long: float):
        # Make a request to obtain all stores.
        stores = json.loads(requests.get(
            'https://uberall.com/api/storefinders/yw1Z9mcwR18Z5wPB8NSjLFyHhvPAMc/locations/all?v=20211005&language=pt&fieldMask=id&fieldMask=identifier&fieldMask=googlePlaceId&fieldMask=lat&fieldMask=lng&fieldMask=name&fieldMask=country&fieldMask=city&fieldMask=province&fieldMask=streetAndNumber&fieldMask=zip&fieldMask=businessId&fieldMask=addressExtra&'
        ).content)['response']['locations']
        # New array of distances.
        distance_array = []
        # Obtain the distances to current location.
        for store in stores:
            # Compute the distance.
            distance = LocateStores.distance(
                lat, long, store['lat'], store['lng']
            )
            # Store the distance on the array.
            distance_array.append((distance, store))
        # Sort the array.
        distance_array.sort(key=(lambda sd: sd[0]), reverse=False)
        # Closest stores.
        for i in range(0, 5):
            # Print the closest stores.
            print(
                f"The closest store is \'{distance_array[i][1]['name']}\' on " +
                f"\'{distance_array[i][1]['streetAndNumber']}\' " +
                f"{distance_array[i][0]:.2f} KMs away."
            )


LocateStores.get_stores_nearby(38.789106, -9.173745)