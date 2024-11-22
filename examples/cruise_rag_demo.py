import json
import asyncio
from pathlib import Path
import logging
from lightrag.CruiseRag import CruiseRAG

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

async def main():
    rag = CruiseRAG(working_dir="./cruise_search_cache")

    # Load sample data
    cruise_lines = json.loads(Path("operators.json").read_text())
    cruise_ships = json.loads(Path("ships.json").read_text())
    cruises = json.loads(Path("cruise.json").read_text())

    # Ingest all data
    # Uncomment these lines if ingestion is needed
    # print("Ingesting cruise lines...")
    # for line in cruise_lines:
    #     await rag.ingest_cruise_line(line)
 
    # print("\nIngesting cruise ships...")
    # for ship in cruise_ships:
    #     await rag.ingest_cruise_ship(ship)
        
    # print("\nIngesting cruises...")
    # for cruise in cruises:
    #     await rag.ingest_cruise(cruise)

    # Example search
    print("\nPerforming sample search...")
    search_params = {
        "query": "luxury cruise with good dining and entertainment",
        "departure_date_lower": "2024-06-01",
        "departure_date_upper": "2024-08-31",
        "duration_lower": 7,
        "duration_upper": 14,
        "price_lower": 1000.0,
        "price_upper": 3000.0,
        "cruise_lines": ["Viking", "Norwegian"],
        "departure_ports": ["Miami", "Fort Lauderdale"],
        "adults_only": True
    }
    
    results = await rag.search(**search_params)
    
    print("\nSearch Query:", results["query"])
    print("\nSearch Results:")
    print(results)
    # for result in results["results"]:
    #     print(json.dumps(result, indent=4))
    print("\nFilters Applied:", results["filters_applied"])

if __name__ == "__main__":
    asyncio.run(main())