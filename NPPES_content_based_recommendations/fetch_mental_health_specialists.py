"""
NPPES API Data Collection for Mental Health Specialists
Fetches provider data for content-based recommendation system
"""

import requests
import pandas as pd
import json
import time
from typing import List, Dict, Any
from pathlib import Path

# Mental health related taxonomy descriptions to search
MENTAL_HEALTH_TAXONOMIES = [
    "Psychiatry",
    "Psychologist",
    "Clinical Social Worker",
    "Mental Health Counselor",
    "Behavioral Health",
    "Psychotherapy",
    "Clinical Psychologist",
    "Psychiatry & Neurology",
    "Mental Health",
]

class NPPESDataCollector:
    """Collector for mental health specialist data from NPPES API v2.1"""
    
    BASE_URL = "https://npiregistry.cms.hhs.gov/api/"
    
    def __init__(self, output_dir: str = "data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.session = requests.Session()
        
    def fetch_providers_by_taxonomy(
        self, 
        taxonomy_desc: str, 
        limit: int = 200,
        max_records: int = 1200
    ) -> List[Dict[str, Any]]:
        """
        Fetch providers for a given taxonomy description.
        API limits: 200 results per request, max 1200 with skip parameter.
        """
        all_results = []
        skip = 0
        
        print(f"Fetching providers for taxonomy: {taxonomy_desc}")
        
        while skip < max_records:
            params = {
                "version": "2.1",
                "taxonomy_description": taxonomy_desc,
                "limit": limit,
                "skip": skip,
                "country_code": "US"
            }
            
            try:
                response = self.session.get(self.BASE_URL, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                results = data.get("results", [])
                if not results:
                    print(f"  No more results at skip={skip}")
                    break
                    
                all_results.extend(results)
                print(f"  Collected {len(results)} records (total: {len(all_results)})")
                
                # Check if we got fewer results than requested (last page)
                if len(results) < limit:
                    break
                    
                skip += limit
                time.sleep(0.5)  # Be respectful to the API
                
            except requests.exceptions.RequestException as e:
                print(f"  Error fetching data: {e}")
                break
                
        return all_results
    
    def extract_provider_info(self, provider: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant information from provider record for RAG system"""
        
        # Basic info
        npi = provider.get("number")
        enum_type = provider.get("enumeration_type")
        
        # Individual vs Organization
        if enum_type == "NPI-1":
            basic = provider.get("basic", {})
            first_name = basic.get("first_name", "").strip()
            last_name = basic.get("last_name", "").strip()
            name = f"{first_name} {last_name}".strip()
            credential = basic.get("credential", "").strip()
        else:
            # Clean organization name - remove quotes and extra characters
            org_name = provider.get("basic", {}).get("organization_name", "")
            name = org_name.strip().strip("'\"").strip()
            credential = ""
            
        # Taxonomies - get primary and all specialties
        taxonomies = provider.get("taxonomies", [])
        primary_taxonomy = None
        all_taxonomies = []
        
        for tax in taxonomies:
            # Clean taxonomy description
            desc = tax.get("desc", "").strip() if tax.get("desc") else None
            code = tax.get("code", "").strip() if tax.get("code") else None
            
            tax_info = {
                "code": code,
                "desc": desc,
                "state": tax.get("state"),
                "license": tax.get("license"),
                "primary": tax.get("primary", False)
            }
            all_taxonomies.append(tax_info)
            if tax.get("primary") and desc:  # Only set if has description
                primary_taxonomy = tax_info
        
        # If no primary found but taxonomies exist, use first one with description
        if not primary_taxonomy and all_taxonomies:
            for tax in all_taxonomies:
                if tax.get("desc"):
                    primary_taxonomy = tax
                    break
                
        # Addresses - Primary Practice Location and Mailing
        addresses = provider.get("addresses", [])
        practice_location = None
        mailing_address = None
        
        if addresses:
            # First address is Primary Practice Location
            practice_location = addresses[0] if len(addresses) > 0 else None
            # Second address is Mailing Address
            mailing_address = addresses[1] if len(addresses) > 1 else None
            
        # Extract practice location details
        if practice_location:
            location_info = {
                "address_1": practice_location.get("address_1"),
                "address_2": practice_location.get("address_2"),
                "city": practice_location.get("city"),
                "state": practice_location.get("state"),
                "postal_code": practice_location.get("postal_code"),
                "country_code": practice_location.get("country_code"),
                "telephone": practice_location.get("telephone_number")
            }
        else:
            location_info = {}
            
        # Other identifiers
        identifiers = provider.get("identifiers", [])
        
        # Endpoints
        endpoints = provider.get("endpoints", [])
        
        # Construct structured record for RAG
        record = {
            "npi": str(npi).strip() if npi else None,
            "provider_type": "Individual" if enum_type == "NPI-1" else "Organization",
            "name": name if name else None,
            "credential": credential if credential else None,
            "primary_taxonomy": primary_taxonomy.get("desc") if primary_taxonomy else None,
            "primary_taxonomy_code": primary_taxonomy.get("code") if primary_taxonomy else None,
            "all_taxonomies": json.dumps(all_taxonomies),  # Store as JSON string for CSV
            "practice_location": json.dumps(location_info),  # Store as JSON string for CSV
            "mailing_address": json.dumps(mailing_address) if mailing_address else None,
            "identifiers": json.dumps(identifiers),
            "endpoints": json.dumps(endpoints),
            "last_updated": provider.get("basic", {}).get("last_updated"),
            "status": provider.get("basic", {}).get("status")
        }
        
        return record
    
    def collect_all_mental_health_providers(self) -> pd.DataFrame:
        """Collect providers for all mental health taxonomies"""
        
        all_providers = []
        seen_npis = set()
        
        for taxonomy in MENTAL_HEALTH_TAXONOMIES:
            providers = self.fetch_providers_by_taxonomy(taxonomy)
            
            for provider in providers:
                npi = provider.get("number")
                # Avoid duplicates
                if npi not in seen_npis:
                    seen_npis.add(npi)
                    extracted = self.extract_provider_info(provider)
                    all_providers.append(extracted)
                    
            print(f"Total unique providers so far: {len(all_providers)}\n")
            
        df = pd.DataFrame(all_providers)
        return df
    
    def save_data(self, df: pd.DataFrame):
        """Save collected data in multiple formats"""
        
        # Clean data before saving
        # Remove any rows with missing critical fields
        df_clean = df.dropna(subset=['npi', 'name', 'primary_taxonomy'])
        print(f"Cleaned data: {len(df)} -> {len(df_clean)} records (removed {len(df) - len(df_clean)} invalid)")
        
        # Save as CSV with proper quoting
        csv_path = self.output_dir / "mental_health_specialists_raw.csv"
        df_clean.to_csv(csv_path, index=False, quoting=1)  # QUOTE_ALL
        print(f"Saved CSV to: {csv_path}")
        
        # Save as JSON for RAG system
        json_path = self.output_dir / "mental_health_specialists_raw.json"
        df.to_json(json_path, orient="records", indent=2)
        print(f"Saved JSON to: {json_path}")
        
        # Save metadata
        metadata = {
            "total_records": len(df),
            "collection_date": pd.Timestamp.now().isoformat(),
            "taxonomies_searched": MENTAL_HEALTH_TAXONOMIES,
            "columns": list(df.columns)
        }
        
        metadata_path = self.output_dir / "collection_metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
        print(f"Saved metadata to: {metadata_path}")
        

def main():
    """Main execution function"""
    print("="*60)
    print("NPPES Mental Health Specialist Data Collection")
    print("="*60)
    print()
    
    collector = NPPESDataCollector(output_dir="data")
    
    # Collect data
    print("Starting data collection...")
    df = collector.collect_all_mental_health_providers()
    
    print("\n" + "="*60)
    print(f"Collection complete! Total providers: {len(df)}")
    print("="*60)
    print()
    
    # Save data
    collector.save_data(df)
    
    print("\nData collection finished successfully!")
    

if __name__ == "__main__":
    main()
