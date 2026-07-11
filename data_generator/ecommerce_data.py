"""
Ecommerce Recommendation Data Generator 
Generates 100K+ records with realistic user data from randomuser.me
"""

import json
import random
import uuid
import csv
import requests
from datetime import datetime, timedelta
from pathlib import Path
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from typing import Dict, List, Optional, Any

class HighVolumeDataGenerator:
    def __init__(self):
        # Product Catalog - Expanded
        self.products = [
            {"sku": "ARC-ATOM-M-BLK", "name": "Atom Hoody", "brand": "Arc'teryx", 
             "category": "Jackets", "subcategory": "Insulated", "price": 259.99, "in_stock": True},
            {"sku": "SAL-XULTRA-4-10", "name": "X Ultra 4 GTX", "brand": "Salomon", 
             "category": "Footwear", "subcategory": "Hiking", "price": 174.95, "in_stock": True},
            {"sku": "PAT-NANO-M-BLK", "name": "Nano Puff Hoody", "brand": "Patagonia", 
             "category": "Jackets", "subcategory": "Insulated", "price": 249.00, "in_stock": True},
            {"sku": "NIK-AIR-MAX", "name": "Air Max 270", "brand": "Nike", 
             "category": "Footwear", "subcategory": "Lifestyle", "price": 150.00, "in_stock": True},
            {"sku": "ADID-ULTRABOOST", "name": "Ultraboost 22", "brand": "Adidas", 
             "category": "Footwear", "subcategory": "Running", "price": 180.00, "in_stock": True},
            {"sku": "COL-NORTH-FACE", "name": "Thermoball Eco", "brand": "The North Face", 
             "category": "Jackets", "subcategory": "Insulated", "price": 199.00, "in_stock": True},
            {"sku": "ARC-ATOM-W-BLK", "name": "Atom Hoody Womens", "brand": "Arc'teryx", 
             "category": "Womens", "subcategory": "Jackets", "price": 259.99, "in_stock": True},
            {"sku": "PAT-NANO-W-BLK", "name": "Nano Puff Womens", "brand": "Patagonia", 
             "category": "Womens", "subcategory": "Jackets", "price": 249.00, "in_stock": True},
            {"sku": "NIK-AIR-WHITE", "name": "Air Max 270 White", "brand": "Nike", 
             "category": "Footwear", "subcategory": "Lifestyle", "price": 150.00, "in_stock": True},
            {"sku": "ADID-ULTRABOOST-W", "name": "Ultraboost 22 Womens", "brand": "Adidas", 
             "category": "Womens", "subcategory": "Running", "price": 180.00, "in_stock": True},
            {"sku": "SAL-XULTRA-W", "name": "X Ultra 4 GTX Womens", "brand": "Salomon", 
             "category": "Womens", "subcategory": "Hiking", "price": 174.95, "in_stock": True},
            {"sku": "NORTH-DENALI", "name": "Denali Jacket", "brand": "The North Face", 
             "category": "Jackets", "subcategory": "Fleece", "price": 159.00, "in_stock": True},
            {"sku": "PAT-BETTER-SWEAT", "name": "Better Sweater", "brand": "Patagonia", 
             "category": "Jackets", "subcategory": "Fleece", "price": 139.00, "in_stock": True},
            {"sku": "ARC-COVERT", "name": "Covert Cardigan", "brand": "Arc'teryx", 
             "category": "Jackets", "subcategory": "Fleece", "price": 199.00, "in_stock": True},
            {"sku": "NIK-AIR-FORCE", "name": "Air Force 1", "brand": "Nike", 
             "category": "Footwear", "subcategory": "Lifestyle", "price": 120.00, "in_stock": True},
            {"sku": "HOKA-SPEEDGOAT", "name": "Speedgoat 5", "brand": "Hoka", 
             "category": "Footwear", "subcategory": "Trail Running", "price": 155.00, "in_stock": True},
            {"sku": "BROOKS-GHOST", "name": "Ghost 15", "brand": "Brooks", 
             "category": "Footwear", "subcategory": "Running", "price": 140.00, "in_stock": True},
            {"sku": "UNDER-ARMOUR", "name": "Rush Jacket", "brand": "Under Armour", 
             "category": "Jackets", "subcategory": "Running", "price": 120.00, "in_stock": True},
        ]
        
        # Expanded datasets for variety
        self.event_types = [
            "page_view", "product_view", "add_to_cart", "remove_from_cart",
            "checkout", "purchase", "search", "scroll", "app_open", 
            "wishlist", "share", "review", "signup"
        ]
        
        self.search_terms = [
            "hiking boots", "winter jacket", "running shoes", "waterproof jacket",
            "camping gear", "backpack", "insulated jacket", "trail running shoes",
            "everyday sneakers", "lightweight jacket", "ski jacket", "trekking pants",
            "fleece jacket", "down jacket", "rain jacket", "hiking shoes",
            "walking shoes", "athletic shoes", "outdoor gear", "snow jacket"
        ]
        
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/17.1 Safari/605.1.15",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15",
            "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 Chrome/120.0.0.0",
            "Mozilla/5.0 (Linux; Android 14; Pixel 7 Pro) AppleWebKit/537.36 Chrome/120.0.0.0",
            "Mozilla/5.0 (iPad; CPU OS 17_2 like Mac OS X) AppleWebKit/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Edge/120.0.0.0"
        ]
        
        self.countries = ["US", "GB", "CA", "AU", "DE", "FR", "ES", "IT", "NL", "SE", "NO", "DK"]
        
        self.users = []
        self.user_map = {}  # For quick lookup
        self.products_cache = self.products
        self.lock = threading.Lock()
        
        print(f" Initialized with {len(self.products)} products")

    def fetch_users_from_api(self, num_users: int = 1000, batch_size: int = 50) -> List[ Dict]:
        """
        Fetch realistic user profiles from Random User API with parallel processing
        """
        print(f"👤 Fetching {num_users} users from Random User API...")
        
        users = []
        total_batches = (num_users + batch_size - 1) // batch_size
        
        def fetch_batch(batch_num):
            """Fetch a single batch of users"""
            remaining = min(batch_size, num_users - (batch_num * batch_size))
            if remaining <= 0:
                return []
            
            try:
                # Add delay between requests to avoid rate limiting
                time.sleep(random.uniform(0.2, 0.5))
                
                response = requests.get(
                    "https://randomuser.me/api/",
                    params={
                        "results": remaining,
                        "inc": "name,email,location,phone,gender,dob,registered,login,id,picture,nat",
                        "nat": ",".join(random.sample(self.countries, min(5, len(self.countries))))
                    },
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    batch_users = []
                    for user_data in data["results"]:
                        user = self._transform_api_user(user_data)
                        batch_users.append(user)
                    
                    print(f"  Batch {batch_num + 1}/{total_batches}:  Got {len(batch_users)} users")
                    return batch_users
                else:
                    print(f"  Batch {batch_num + 1}/{total_batches}:  API error {response.status_code}")
                    return self._generate_fallback_users(remaining)
                    
            except requests.exceptions.Timeout:
                print(f"  Batch {batch_num + 1}/{total_batches}:  Timeout, using fallback")
                return self._generate_fallback_users(remaining)
            except Exception as e:
                print(f"  Batch {batch_num + 1}/{total_batches}:  Error: {e}")
                return self._generate_fallback_users(remaining)
        
        # Use ThreadPoolExecutor for parallel fetching
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(fetch_batch, i) for i in range(total_batches)]
            
            for future in as_completed(futures):
                try:
                    batch_users = future.result()
                    with self.lock:
                        users.extend(batch_users)
                except Exception as e:
                    print(f"Error processing batch: {e}")
        
        # Store users
        with self.lock:
            self.users = users
            self.user_map = {u["user_id"]: u for u in users}
        
        print(f" Total users fetched: {len(users)}")
        return users

    def _transform_api_user(self, api_user: Dict) -> Dict:
        """Transform Random User API response to our format"""
        user_id = f"usr_{api_user['login']['uuid'][:8]}"
        
        # Determine preferred categories based on gender
        gender = api_user['gender']
        age = int(api_user['dob']['age'])
        
        if gender == 'female':
            preferred_categories = ['Womens > Jackets', 'Womens > Footwear', 'Accessories']
        else:
            preferred_categories = ['Mens > Jackets', 'Mens > Footwear', 'Accessories']
        
        # Generate purchase history (0-8 purchases)
        num_purchases = random.randint(0, min(8, len(self.products)))
        past_purchases = random.sample(self.products, num_purchases) if num_purchases > 0 else []
        
        # Generate preferences
        brands = list(set([p["brand"] for p in self.products]))
        num_brands = random.randint(1, min(3, len(brands)))
        preferred_brands = random.sample(brands, num_brands)
        
        return {
            "user_id": user_id,
            "email": api_user['email'],
            "name": {
                "first": api_user['name']['first'],
                "last": api_user['name']['last'],
                "title": api_user['name']['title']
            },
            "gender": gender,
            "phone": api_user['phone'],
            "age": age,
            "location": {
                "city": api_user['location']['city'],
                "state": api_user['location']['state'],
                "country": api_user['location']['country'],
                "postcode": str(api_user['location']['postcode']),
                "latitude": float(api_user['location']['coordinates']['latitude']),
                "longitude": float(api_user['location']['coordinates']['longitude'])
            },
            "nationality": api_user.get('nat', 'US'),
            "picture": api_user.get('picture', {}).get('large', ''),
            "preferences": {
                "preferred_brands": preferred_brands,
                "preferred_category": random.choice(preferred_categories),
                "price_sensitivity": random.choice(["Low", "Medium", "High"]),
                "shopping_frequency": random.choice(["Daily", "Weekly", "Monthly", "Occasional"])
            },
            "past_purchases": [p["sku"] for p in past_purchases],
            "loyalty_tier": random.choice(["Bronze", "Silver", "Gold", "Platinum"]),
            "avg_order_value": round(random.uniform(80, 350), 2),
            "registered_date": api_user['registered']['date'],
            "last_active": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat()
        }

    def _generate_fallback_users(self, num_users: int) -> List[Dict]:
        """Generate synthetic users if API fails"""
        first_names = ["James", "Mary", "Robert", "Patricia", "John", "Jennifer", 
                       "Michael", "Linda", "David", "Elizabeth", "William", "Susan"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", 
                      "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez"]
        cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", 
                  "Philadelphia", "San Antonio", "San Diego", "Dallas", "Austin"]
        states = ["NY", "CA", "IL", "TX", "AZ", "PA", "TX", "CA", "TX", "TX"]
        
        fallback_users = []
        for i in range(num_users):
            first = random.choice(first_names)
            last = random.choice(last_names)
            age = random.randint(18, 65)
            city_idx = random.randint(0, len(cities) - 1)
            gender = random.choice(["male", "female"])
            
            # Generate past purchases
            num_purchases = random.randint(0, 5)
            past_purchases = random.sample(self.products, num_purchases) if num_purchases > 0 else []
            
            # Generate preferences
            brands = list(set([p["brand"] for p in self.products]))
            preferred_brands = random.sample(brands, min(random.randint(1, 3), len(brands)))
            
            user = {
                "user_id": f"usr_{uuid.uuid4().hex[:8]}",
                "email": f"{first.lower()}.{last.lower()}{random.randint(1,999)}@email.com",
                "name": {"first": first, "last": last, "title": random.choice(["Mr", "Ms", "Mrs", "Dr"])},
                "gender": gender,
                "phone": f"+1-{random.randint(200,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}",
                "age": age,
                "location": {
                    "city": cities[city_idx],
                    "state": states[city_idx],
                    "country": "US",
                    "postcode": str(random.randint(10000, 99999))
                },
                "nationality": "US",
                "preferences": {
                    "preferred_brands": preferred_brands,
                    "preferred_category": random.choice(["Jackets", "Footwear", "Womens"]),
                    "price_sensitivity": random.choice(["Low", "Medium", "High"]),
                    "shopping_frequency": random.choice(["Daily", "Weekly", "Monthly", "Occasional"])
                },
                "past_purchases": [p["sku"] for p in past_purchases],
                "loyalty_tier": random.choice(["Bronze", "Silver", "Gold", "Platinum"]),
                "avg_order_value": round(random.uniform(80, 350), 2),
                "registered_date": (datetime.now() - timedelta(days=random.randint(1, 730))).isoformat(),
                "last_active": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat()
            }
            fallback_users.append(user)
        
        return fallback_users

    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user profile by ID"""
        return self.user_map.get(user_id)

    def generate_events_batch(self, num_events: int = 50000, start_time: Optional[datetime] = None) -> List[Dict]:
        """Generate events in batch for high performance"""
        if start_time is None:
            start_time = datetime.now() - timedelta(hours=24)
        
        if not self.users:
            print(" No users available! Generating fallback users...")
            self.users = self._generate_fallback_users(1000)
            self.user_map = {u["user_id"]: u for u in self.users}
        
        events = []
        current_time = start_time
        
        # Pre-calculate for speed
        user_ids = [u["user_id"] for u in self.users]
        products = self.products
        event_types = self.event_types
        search_terms = self.search_terms
        user_agents = self.user_agents
        
        print(f" Generating {num_events:,} events...")
        
        for i in range(num_events):
            # Time increment (1-60 seconds)
            seconds = random.randint(1, 60)
            current_time += timedelta(seconds=seconds)
            
            # Select user (75% chance of logged in)
            if random.random() < 0.75 and user_ids:
                user_id = random.choice(user_ids)
            else:
                user_id = None
            
            # Platform
            platform = random.choice(["web", "ios", "android"])
            
            # Event type
            event_type = random.choice(event_types)
            
            # Build event
            event = {
                "event_id": f"evt_{uuid.uuid4().hex[:12]}",
                "timestamp": current_time.isoformat() + "Z",
                "platform": platform,
                "user_id": user_id,
                "session_id": f"sess_{uuid.uuid4().hex[:10]}",
                "device_id": f"dev_{uuid.uuid4().hex[:12]}",
                "event_type": event_type,
                "user_agent": random.choice(user_agents),
                "ip": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
            }
            
            # Add user demographics if available
            if user_id and user_id in self.user_map:
                user = self.user_map[user_id]
                event["user_age"] = user.get("age")
                event["user_gender"] = user.get("gender")
                event["user_location"] = user["location"]["city"]
                event["loyalty_tier"] = user.get("loyalty_tier")
            
            # Add product data for relevant events
            if event_type in ["product_view", "add_to_cart", "remove_from_cart", "purchase", "wishlist"]:
                product = random.choice(products)
                event["product"] = {
                    "sku": product["sku"],
                    "name": product["name"],
                    "category": product["category"],
                    "subcategory": product["subcategory"],
                    "price": product["price"],
                    "brand": product["brand"],
                    "quantity": random.randint(1, 3)
                }
                
                if event_type in ["add_to_cart", "remove_from_cart"]:
                    event["cart_total_items"] = random.randint(1, 5)
                    event["cart_total_value"] = round(random.uniform(50, 600), 2)
                
                if event_type == "purchase":
                    event["order_id"] = f"ORD-{random.randint(10000, 99999)}"
                    event["total_amount"] = product["price"] * event["product"]["quantity"]
                    event["payment_method"] = random.choice(["Credit_Card", "PayPal", "Apple_Pay", "Google_Pay"])
                    event["shipping_method"] = random.choice(["Standard", "Express", "Next-Day"])
            
            # Add search data
            if event_type == "search":
                event["search_query"] = random.choice(search_terms)
                event["search_results"] = random.randint(5, 100)
                event["filters"] = {
                    "size": random.choice(["S", "M", "L", "XL"]),
                    "gender": random.choice(["Mens", "Womens", "Unisex"]),
                    "price_min": random.choice([0, 50, 100]),
                    "price_max": random.choice([200, 300, 500])
                }
            
            # Add recommendation source
            if event_type == "product_view" and random.random() > 0.4:
                event["recommendation"] = {
                    "source": random.choice(["homepage", "category", "product_page", "email", "push", "search"]),
                    "algorithm": random.choice(["collaborative_filtering", "content_based", "popular", "personalized", "trending"]),
                    "position": random.randint(1, 15)
                }
            
            # Add scroll depth for page views
            if event_type == "scroll":
                event["scroll_depth"] = random.randint(10, 100)
            
            # Add page info for web
            if platform == "web":
                event["page_url"] = random.choice([
                    "https://www.example.com/",
                    "https://www.example.com/category/jackets",
                    "https://www.example.com/category/footwear",
                    "https://www.example.com/sale",
                    "https://www.example.com/new-arrivals",
                    "https://www.example.com/cart",
                    "https://www.example.com/checkout"
                ])
                event["referrer"] = random.choice([
                    "https://www.google.com/",
                    "https://www.facebook.com/",
                    "https://www.instagram.com/",
                    "https://www.youtube.com/",
                    "https://www.tiktok.com/",
                    None
                ])
            else:
                event["app_version"] = random.choice(["3.2.1", "3.2.0", "3.1.9", "3.2.2"])
                event["screen"] = random.choice(["home", "category", "product", "search", "cart", "checkout"])
                event["network_type"] = random.choice(["WiFi", "5G", "4G", "3G"])
            
            events.append(event)
            
            # Progress indicator
            if (i + 1) % 10000 == 0:
                print(f"  Generated {i + 1:,} / {num_events:,} events...")
        
        print(f"✅ Generated {len(events):,} events")
        return events

    def generate_batch_historical(self, num_days: int = 30, events_per_day: int = 2000) -> List[Dict]:
        """Generate historical batch data"""
        print(f" Generating {num_days} days of historical data...")
        
        if not self.users:
            print(" No users available! Generating fallback users...")
            self.users = self._generate_fallback_users(1000)
            self.user_map = {u["user_id"]: u for u in self.users}
        
        all_events = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=num_days)
        
        current_date = start_date
        day_count = 0
        
        # Pre-calculate for speed
        user_ids = [u["user_id"] for u in self.users]
        products = self.products
        event_types = self.event_types
        search_terms = self.search_terms
        user_agents = self.user_agents
        
        while current_date <= end_date:
            # Weekend multiplier
            is_weekend = current_date.weekday() >= 5
            day_events = int(events_per_day * (1.5 if is_weekend else 1.0))
            
            # Generate events for this day
            for _ in range(day_events):
                hour = random.randint(8, 23)
                minute = random.randint(0, 59)
                second = random.randint(0, 59)
                timestamp = current_date.replace(hour=hour, minute=minute, second=second)
                
                # Select user
                user_id = random.choice(user_ids) if random.random() > 0.3 else None
                platform = random.choice(["web", "ios", "android"])
                
                # Generate event
                event_type = random.choice(event_types)
                
                event = {
                    "event_id": f"evt_{uuid.uuid4().hex[:12]}",
                    "timestamp": timestamp.isoformat() + "Z",
                    "platform": platform,
                    "user_id": user_id,
                    "session_id": f"sess_{uuid.uuid4().hex[:10]}",
                    "device_id": f"dev_{uuid.uuid4().hex[:12]}",
                    "event_type": event_type,
                    "user_agent": random.choice(user_agents),
                    "ip": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
                }
                
                # Add product data
                if event_type in ["product_view", "add_to_cart", "purchase"]:
                    product = random.choice(products)
                    event["product"] = {
                        "sku": product["sku"],
                        "name": product["name"],
                        "category": product["category"],
                        "price": product["price"],
                        "brand": product["brand"],
                        "quantity": random.randint(1, 2)
                    }
                    
                    if event_type == "purchase":
                        event["order_id"] = f"ORD-{random.randint(10000, 99999)}"
                        event["total_amount"] = product["price"] * event["product"]["quantity"]
                
                if event_type == "search":
                    event["search_query"] = random.choice(search_terms)
                    event["search_results"] = random.randint(5, 50)
                
                all_events.append(event)
            
            day_count += 1
            
            if day_count % 7 == 0:
                print(f"  Generated {day_count} / {num_days} days of data...")
            
            current_date += timedelta(days=1)
        
        print(f" Generated {len(all_events):,} historical events")
        return all_events

    def save_data_parallel(self, events: List[Dict], output_dir: str = "ecommerce_data"):
        """Save data efficiently"""
        print(f"\n Saving {len(events):,} events to {output_dir}/")
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # 1. Save events in chunks (for large files)
        print("  Saving events...")
        chunk_size = 50000
        total_saved = 0
        for i in range(0, len(events), chunk_size):
            chunk = events[i:i+chunk_size]
            mode = 'a' if i > 0 else 'w'
            with open(f"{output_dir}/events_stream.jsonl", mode) as f:
                for event in chunk:
                    f.write(json.dumps(event) + "\n")
            total_saved += len(chunk)
            if (i + chunk_size) < len(events):
                print(f"    Saved {total_saved:,} / {len(events):,} events")
        
        print(f"  events_stream.jsonl ({len(events):,} events)")
        
        # 2. Save users (with progress)
        print("  Saving users...")
        with open(f"{output_dir}/user_profiles.json", "w") as f:
            json.dump(self.users, f, indent=2)
        print(f"   user_profiles.json ({len(self.users):,} users)")
        
        # 3. Save users as CSV
        with open(f"{output_dir}/user_profiles.csv", "w", newline="", encoding='utf-8') as f:
            fieldnames = ["user_id", "email", "first_name", "last_name", "gender", 
                         "age", "city", "state", "country", "loyalty_tier", 
                         "avg_order_value", "registered_date"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for user in self.users:
                writer.writerow({
                    "user_id": user["user_id"],
                    "email": user["email"],
                    "first_name": user["name"]["first"],
                    "last_name": user["name"]["last"],
                    "gender": user.get("gender", ""),
                    "age": user.get("age", ""),
                    "city": user["location"]["city"],
                    "state": user["location"]["state"],
                    "country": user["location"].get("country", ""),
                    "loyalty_tier": user.get("loyalty_tier", ""),
                    "avg_order_value": user.get("avg_order_value", 0),
                    "registered_date": user.get("registered_date", "")
                })
        print(f"  ✅ user_profiles.csv ({len(self.users):,} users)")
        
        # 4. Save products
        with open(f"{output_dir}/product_catalog.json", "w") as f:
            json.dump(self.products, f, indent=2)
        print(f"  ✅ product_catalog.json ({len(self.products)} products)")
        
        # 5. Generate and save clickstream summary
        print("  Generating clickstream summary...")
        clickstream = []
        # Sample for performance
        sample_size = min(50000, len(events))
        sampled_events = random.sample(events, sample_size)
        
        for event in sampled_events:
            if event["event_type"] in ["product_view", "add_to_cart", "purchase"] and "product" in event:
                clickstream.append({
                    "date": event["timestamp"][:10],
                    "user_id": event["user_id"],
                    "event_type": event["event_type"],
                    "product_sku": event["product"]["sku"],
                    "product_name": event["product"].get("name", ""),
                    "platform": event["platform"]
                })
        
        with open(f"{output_dir}/clickstream_summary.csv", "w", newline="", encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["date", "user_id", "event_type", "product_sku", "product_name", "platform"])
            writer.writeheader()
            writer.writerows(clickstream)
        print(f"  ✅ clickstream_summary.csv ({len(clickstream):,} records)")
        
        # 6. Save a sample of events for quick viewing
        sample_size = min(2000, len(events))
        with open(f"{output_dir}/events_sample.json", "w") as f:
            json.dump(events[:sample_size], f, indent=2)
        print(f"  ✅ events_sample.json ({sample_size:,} events)")
        
        # 7. Save statistics
        stats = self.generate_statistics(events)
        with open(f"{output_dir}/data_statistics.json", "w") as f:
            json.dump(stats, f, indent=2)
        print(f"  ✅ data_statistics.json")
        
        # 8. Save a README file
        readme = f"""# Ecommerce Recommendation Data

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Statistics
- Total Events: {len(events):,}
- Total Users: {len(self.users):,}
- Total Products: {len(self.products)}
- Date Range: {stats['date_range'].get('start', 'N/A')} to {stats['date_range'].get('end', 'N/A')}

## Files
- events_stream.jsonl - All events (JSON lines format)
- events_sample.json - Sample of events (2,000 records)
- user_profiles.json - User profiles (from Random User API)
- user_profiles.csv - User profiles (CSV format)
- product_catalog.json - Product catalog
- clickstream_summary.csv - Clickstream data
- data_statistics.json - Data statistics

## Usage
- Use events_stream.jsonl for streaming pipeline testing
- Use user_profiles.json for user data enrichment
- Use product_catalog.json for product catalog
- Use clickstream_summary.csv for analysis

## Data Quality
- Realistic user profiles from randomuser.me API
- Realistic event patterns with session clustering
- Weekend traffic multiplier (50% more events)
- Realistic product catalog with categories and pricing
"""
        with open(f"{output_dir}/README.md", "w") as f:
            f.write(readme)
        print(f"  ✅ README.md")
        
        print(f"\n✅ All data saved successfully!")

    def generate_statistics(self, events: List[Dict]) -> Dict:
        """Generate statistics about the data"""
        stats = {
            "total_events": len(events),
            "total_users": len(self.users),
            "total_products": len(self.products),
            "event_types": {},
            "platforms": {},
            "date_range": {},
            "unique_users": len(set(e.get("user_id") for e in events if e.get("user_id"))),
            "purchase_count": len([e for e in events if e["event_type"] == "purchase"]),
            "total_revenue": 0
        }
        
        for event in events:
            stats["event_types"][event["event_type"]] = stats["event_types"].get(event["event_type"], 0) + 1
            stats["platforms"][event["platform"]] = stats["platforms"].get(event["platform"], 0) + 1
            
            if event["event_type"] == "purchase":
                stats["total_revenue"] += event.get("total_amount", 0)
        
        if events:
            # events aren't guaranteed to be in chronological order once batch + stream
            # data are combined, so derive start/end from actual min/max timestamps.
            timestamps = sorted(e["timestamp"] for e in events)
            stats["date_range"]["start"] = timestamps[0]
            stats["date_range"]["end"] = timestamps[-1]

        stats["total_revenue"] = round(stats["total_revenue"], 2)

        # Add user demographics summary
        if self.users:
            ages = [u.get("age", 0) for u in self.users if u.get("age")]
            if ages:
                stats["avg_age"] = round(sum(ages) / len(ages), 1)
                stats["age_range"] = {"min": min(ages), "max": max(ages)}
            
            genders = {}
            for user in self.users:
                gender = user.get("gender", "unknown")
                genders[gender] = genders.get(gender, 0) + 1
            stats["gender_distribution"] = genders
        
        return stats

    def generate_all_data(self, num_users: int = 2000, num_stream_events: int = 50000, 
                          num_batch_days: int = 30, events_per_day: int = 2000, 
                          output_dir: str = "ecommerce_data"):
        """Generate all data with high volume"""
        print("=" * 70)
        print("🚀 HIGH VOLUME ECOMMERCE DATA GENERATOR")
        print("📡 Using Random User API for realistic profiles")
        print("=" * 70)
        
        # Step 1: Fetch users from API
        self.fetch_users_from_api(num_users)
        
        if not self.users:
            print("⚠️ No users fetched, using fallback...")
            self.users = self._generate_fallback_users(num_users)
            self.user_map = {u["user_id"]: u for u in self.users}

        # Step 2: Generate real-time-style stream events (last 24h, second-level granularity)
        print("\n" + "-" * 70)
        print("STEP 2: Real-time stream events")
        print("-" * 70)
        stream_events = self.generate_events_batch(num_events=num_stream_events)

        # Step 3: Generate historical batch data (N days, day-level seeding)
        print("\n" + "-" * 70)
        print("STEP 3: Historical batch data")
        print("-" * 70)
        historical_events = self.generate_batch_historical(
            num_days=num_batch_days, events_per_day=events_per_day
        )

        # Step 4: Combine both sets — this is your bronze-layer "raw events" table.
        # Historical data feeds the batch layer; stream events simulate what a
        # Kafka consumer would be ingesting right now for the speed layer.
        all_events = historical_events + stream_events
        print(f"\n📦 Combined total events: {len(all_events):,} "
              f"({len(historical_events):,} historical + {len(stream_events):,} stream)")

        # Step 5: Persist everything to disk
        print("\n" + "-" * 70)
        print("STEP 4: Saving all data")
        print("-" * 70)
        self.save_data_parallel(all_events, output_dir=output_dir)

        # Step 6: Print a quick summary to console
        stats = self.generate_statistics(all_events)
        print("\n" + "=" * 70)
        print("📈 SUMMARY")
        print("=" * 70)
        print(f"  Total events:     {stats['total_events']:,}")
        print(f"  Total users:      {stats['total_users']:,}")
        print(f"  Unique active users in events: {stats['unique_users']:,}")
        print(f"  Total products:   {stats['total_products']}")
        print(f"  Purchases:        {stats['purchase_count']:,}")
        print(f"  Total revenue:    ${stats['total_revenue']:,.2f}")
        print(f"  Event types:      {stats['event_types']}")
        print(f"  Platform split:   {stats['platforms']}")
        print("=" * 70)

        return all_events


if __name__ == "__main__":
    # Reasonable defaults for a portfolio-scale run. Tune these up if you want
    # a heavier stress-test dataset (e.g. num_users=5000, num_stream_events=100000).
    generator = HighVolumeDataGenerator()
    generator.generate_all_data(
        num_users=2000,
        num_stream_events=50000,
        num_batch_days=30,
        events_per_day=2000,
        output_dir="ecommerce_data"
    )