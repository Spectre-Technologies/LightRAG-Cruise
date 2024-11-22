from dataclasses import dataclass
from typing import List, Dict, Optional, Union, Any
from datetime import datetime
import json
from zoneinfo import ZoneInfo
import html
import logging

from lightrag import LightRAG, QueryParam
from helpers.parser import parse_description  # Ensure the correct import path

class CruiseRAG:
    def __init__(self, working_dir: str = "./cruise_rag_cache"):
        self.rag = LightRAG(
            working_dir=working_dir,
            entity_extract_max_gleaning=2,
            chunk_token_size=2000,
            addon_params={
                "entity_types": [
                    "ship", "cruise_line", "itinerary", "port", 
                    "cabin_type", "dining", "entertainment", "amenity",
                    "deck", "accommodation"
                ]
            }
        )

    async def ingest_cruise_line(self, line_data: dict):
        """Ingest cruise line data with all its ships and features"""
        description = f"""
        CRUISE LINE INFORMATION
        Name: {line_data['title']}
        
        Description:
        {html.unescape(line_data['description'])}
        
        Unique Features:
        {html.unescape(line_data['unique_text'])}
        
        Reasons To Book:
        {html.unescape(line_data['reasons_to_book'])}
        
        Loyalty Program:
        {html.unescape(line_data['members_club'])}

        Ships In Fleet:
        {self._format_fleet(line_data.get('ships', []))}

        Social Media:
        - Website: {line_data.get('website_url', '')}
        - Twitter: {line_data.get('twitter_url', '')}
        - Facebook: {line_data.get('facebook_url', '')}
        """
        
        await self.rag.insert(description)

    async def ingest_cruise_ship(self, ship_data: dict):
        """Ingest cruise ship data with all its features and amenities"""
        operator_name = ship_data.get('operator', {}).get('name', 'Unknown Operator')
        operator_profile = ship_data.get('operator', {}).get('profile_image_href', '')
        operator_cover = ship_data.get('operator', {}).get('cover_image_href', '')

        description = f"""
        SHIP INFORMATION
        Name: {ship_data.get('title', 'Unknown Name')}
        Operator: {operator_name}
        Profile Image: {operator_profile}
        Cover Image: {operator_cover}
        Class: {ship_data.get('ship_class', 'N/A')}
        Size: {ship_data.get('size', 'N/A')}
        Style: {ship_data.get('style', 'N/A')}
        Ship Type: {ship_data.get('ship_type', 'N/A')}
        IMO: {ship_data.get('imo', 'N/A')}

        Introduction:
        {html.unescape(ship_data.get('introduction', 'No introduction available.'))}

        Unique Features:
        {html.unescape(ship_data.get('unique_feature', 'No unique features listed.'))}

        Ship Facts:
        - Launch Year: {ship_data.get('ship_facts', {}).get('launch_year', 'N/A')}
        - Refit Year: {ship_data.get('ship_facts', {}).get('refit_year', 'N/A')}
        - Passenger Capacity: {ship_data.get('ship_facts', {}).get('capacity', 'N/A')}
        - Crew Count: {ship_data.get('ship_facts', {}).get('crew_count', 'N/A')}
        - Gross Tonnage: {ship_data.get('ship_facts', {}).get('gross_tonnage', 'N/A')}
        - Length: {ship_data.get('ship_facts', {}).get('length', 'N/A')}m
        - Width: {ship_data.get('ship_facts', {}).get('width', 'N/A')}m
        - Speed: {ship_data.get('ship_facts', {}).get('speed', 'N/A')} knots
        - Decks: {ship_data.get('ship_facts', {}).get('deck_count', 'N/A')}
        - Total Cabins: {ship_data.get('ship_facts', {}).get('cabin_count', 'N/A')}

        Accommodation Overview:
        {html.unescape(ship_data.get('accommodation', {}).get('intro', 'No accommodation details available.'))}

        Cabin Types:
        {self._format_accommodations(ship_data.get('accomodation_types', []))}

        Deck Plans:
        {self._format_decks(ship_data.get('deckplans', []))}

        Dining Venues:
        {self._format_dining_venues(ship_data.get('dining_options', []))}

        Entertainment & Activities:
        {self._format_entertainment(ship_data.get('entertainment_types', []))}

        Health & Fitness:
        {self._format_health_fitness(ship_data.get('health_fitness_types', []))}

        Policies & Requirements:
        Adults Only: {ship_data.get('adults_only', 'N/A')}
        Children's Facilities: {ship_data.get('childrens_facilities', 'N/A')}
        Smoking Policy: {ship_data.get('smoking', 'N/A')}
        Gratuities: {html.unescape(ship_data.get('gratuities', 'N/A'))}

        Accessibility & Special Needs:
        {self._format_accessibility(ship_data.get('useful_types', []))}
        """
        
        await self.rag.insert(description)

    async def ingest_cruise(self, cruise_data: dict):
        """Ingest specific cruise/itinerary data"""
        if not isinstance(cruise_data, dict):
            raise TypeError("cruise_data must be a dictionary")

        # Updated required_keys without 'detailed_itinerary'
        required_keys = [
            'name', 'ref', 'cruise_nights', 'cruise_type', 'regions',
            'starts_at', 'starts_on', 'ends_at', 'ends_on',
            'ship_title', 'operator_title', 'fare_sets'
        ]
        missing_keys = [key for key in required_keys if key not in cruise_data]
        if missing_keys:
            raise KeyError(f"Missing required keys in cruise_data: {missing_keys}")

        # Handle 'detailed_itinerary' optionally
        detailed_itinerary = cruise_data.get('detailed_itinerary', [])

        description = f"""
        CRUISE ITINERARY
        Name: {cruise_data['name']}
        Reference: {cruise_data['ref']}
        Duration: {cruise_data['cruise_nights']} nights
        Type: {', '.join(cruise_data['cruise_type'])}
        Regions: {', '.join(cruise_data['regions'])}

        Schedule:
        Departure: From {cruise_data['starts_at']} on {cruise_data['starts_on']}
        Return: To {cruise_data['ends_at']} on {cruise_data['ends_on']}
        Vacation Days: {cruise_data.get('vacation_days', '')}
        Hotel Nights: {cruise_data.get('hotel_nights', 0)}
        Post Cruise Stay: {cruise_data.get('post_cruise', 0)}

        Ship: {cruise_data['ship_title']}
        Operator: {cruise_data['operator_title']}
        Rating: {cruise_data.get('rating', '')}

        Pricing:
        Cruise Only From: ${cruise_data.get('cruise_only_price', '')}
        Fly Cruise From: ${cruise_data.get('fly_cruise_price', '')}
        Inside Cabins From: ${cruise_data.get('inside_price', '')}
        Outside Cabins From: ${cruise_data.get('outside_price', '')}
        Balcony Cabins From: ${cruise_data.get('balcony_price', '')}
        Suites From: ${cruise_data.get('suite_price', '')}

        """

        # Add Itinerary Details only if available
        if detailed_itinerary:
            description += f"""
            Itinerary Details:
            {self._format_detailed_itinerary(detailed_itinerary)}
            """
        else:
            logging.info(f"No detailed itinerary provided for cruise: {cruise_data.get('name', 'Unknown')}")
            description += "Itinerary Details: Not available.\n"

        description += f"""
        Available Fares:
        {self._format_fare_sets(cruise_data.get('fare_sets', []))}

        Departure Airports: {', '.join(cruise_data.get('airports', []))}
        """

        await self.rag.insert(description)

    async def search(
        self,
        query: str,
        departure_date_lower: str,
        departure_date_upper: str,
        duration_lower: int,
        duration_upper: int,
        price_lower: float,
        price_upper: float,
        cruise_lines: List[str],
        departure_ports: List[str],
        adults_only: bool
    ) -> Dict[str, Union[str, List[Dict[str, Any]]]]:
        """
        Perform a search with the given parameters.
        """
        search_query = f"""
        SEARCH CRUISES
        Query: {query}
        Departure Date Range: {departure_date_lower} to {departure_date_upper}
        Duration: {duration_lower} to {duration_upper} nights
        Price Range: ${price_lower} to ${price_upper}
        Cruise Lines: {', '.join(cruise_lines)}
        Departure Ports: {', '.join(departure_ports)}
        Adults Only: {adults_only}
        """

        await self.rag.insert_async(search_query)

        # Await the asynchronous 'query' method
        raw_results = await self.rag.query(query)

        # Parse each raw result string into a dict
        parsed_results = [parse_description(result) for result in raw_results]

        # Process the results based on search parameters
        filtered_results = [
            result for result in parsed_results
            if departure_date_lower <= result.get('Departure Date', '') <= departure_date_upper
            and duration_lower <= result.get('Duration', 0) <= duration_upper
            and price_lower <= result.get('Cruise Only From', 0) <= price_upper
            and result.get('Cruise Lines', '').split(', ')[-1] in cruise_lines
            and result.get('Departure Ports', '').split(', ')[-1] in departure_ports
            and result.get('Adults Only', False) == adults_only
        ]

        return {
            "query": query,
            "results": filtered_results,
            "filters_applied": {
                "departure_date": f"{departure_date_lower} to {departure_date_upper}",
                "duration": f"{duration_lower} to {duration_upper} nights",
                "price": f"${price_lower} to ${price_upper}",
                "cruise_lines": cruise_lines,
                "departure_ports": departure_ports,
                "adults_only": adults_only
            }
        }

    def _format_fleet(self, ships: List[dict]) -> str:
        formatted = []
        for ship in ships:
            formatted.append(f"""
            Ship: {ship['name']}
            ID: {ship['id']}
            """)
        return "\n".join(formatted)

    def _format_accommodations(self, accommodations: List[dict]) -> str:
        formatted = []
        for cabin in accommodations:
            formatted.append(f"""
            Type: {cabin['name']}
            Details: {html.unescape(cabin.get('description', ''))}
            Statistics: {html.unescape(cabin.get('stats', ''))}
            """)
        return "\n".join(formatted)

    def _format_decks(self, decks: List[dict]) -> str:
        formatted = []
        for deck in decks:
            formatted.append(f"""
            Deck: {deck['name']}
            Features: {html.unescape(deck.get('description', ''))}
            """)
        return "\n".join(formatted)

    def _format_dining_venues(self, venues: List[dict]) -> str:
        formatted = []
        for venue in venues:
            formatted.append(f"""
            Venue: {venue['name']}
            Experience: {venue.get('experience', '')}
            Food Type: {venue.get('food', '')}
            Description: {html.unescape(venue.get('description', ''))}
            """)
        return "\n".join(formatted)

    def _format_entertainment(self, venues: List[dict]) -> str:
        formatted = []
        for venue in venues:
            formatted.append(f"""
            Venue: {venue['name']}
            Description: {html.unescape(venue.get('description', ''))}
            """)
        return "\n".join(formatted)

    def _format_health_fitness(self, facilities: List[dict]) -> str:
        formatted = []
        for facility in facilities:
            formatted.append(f"""
            Facility: {facility['name']}
            Description: {html.unescape(facility.get('description', ''))}
            """)
        return "\n".join(formatted)

    def _format_accessibility(self, policies: List[dict]) -> str:
        formatted = []
        for policy in policies:
            if policy['name'] in ['Disabled Facilities', 'Special Dietary Requirements']:
                formatted.append(f"""
                {policy['name']}:
                {html.unescape(policy.get('description', ''))}
                """)
        return "\n".join(formatted)

    def _format_detailed_itinerary(self, itinerary: List[dict]) -> str:
        if not itinerary:
            return "No itinerary details available."

        formatted = []
        for stop in itinerary:
            port = stop.get('port', {})
            summary = self._safe_get(port, 'summary')
            
            if not summary:
                logging.warning(f"Missing summary for port: {port.get('name', 'Unknown')}")
            
            formatted.append(f"""
            Day {self._safe_get(stop, 'day')}: {self._safe_get(port, 'name')}, {self._safe_get(port, 'country')}
            Port Code: {self._safe_get(port, 'unlocode')}
            Location: {self._safe_get(port, 'latitude')}, {self._safe_get(port, 'longitude')}
            Arrival: {self._safe_get(stop, 'arrives_on')}
            Departure: {self._safe_get(stop, 'departs_on')}
            About: {html.unescape(summary)}
            Programme: {self._safe_get(stop, 'programme')}
            Notes: {self._safe_get(stop, 'notes')}
            """)
        return "\n".join(formatted)

    def _format_fare_sets(self, fare_sets: List[dict]) -> str:
        formatted = []
        for fare_set in fare_sets:
            formatted.append(f"""
            Deal: {fare_set['name']}
            Code: {fare_set['deal_code']}
            Airport: {fare_set.get('airport', 'Any')}
            Port Charge: ${fare_set.get('port_charge', 0)}
            
            Available Cabins:
            {self._format_fares(fare_set.get('fares', []))}
            """)
        return "\n".join(formatted)

    def _format_fares(self, fares: List[dict]) -> str:
        formatted = []
        for fare in fares:
            if fare.get('price'):
                formatted.append(f"""
                Grade: {fare['grade_name']} ({fare['grade_code']})
                Base Price: ${fare['price']}
                Single Price: ${fare.get('price_single', 'N/A')}
                Flight Price: ${fare.get('flight_price', 'N/A')}
                3rd/4th Guest Price: ${fare.get('price_3_4_pax', 'N/A')}
                Flight Price (3rd/4th): ${fare.get('flight_price_3_4_pax', 'N/A')}
                Availability: {fare.get('availability', '')}
                Non-Comm Charges: ${fare.get('non_comm_charges', 0)}
                """)
        return "\n".join(formatted)

    def _safe_get(self, data: dict, key: str, default: Union[str, int, float] = '') -> Union[str, int, float]:
        value = data.get(key, default)
        return value if isinstance(value, (str, int, float)) else default

# Example usage:
async def ingest_all_data(cruise_rag: CruiseRAG, cruise_data: dict, ship_data: dict, line_data: dict):
    """Ingest all cruise related data"""
    # First ingest the cruise line since ships reference it
    await cruise_rag.ingest_cruise_line(line_data)
    
    # Then ingest the ship since cruises reference it
    await cruise_rag.ingest_cruise_ship(ship_data)
    
    # Finally ingest the specific cruise
    await cruise_rag.ingest_cruise(cruise_data)