"""
Ecommerce Recommendation Data Generator
"""

import json
import random
import uuid
import csv
from datetime import datetime, timedelta
from pathlib import Path
import sys

class EcommerceDataGenerator:
    def __init__(self):
        # Product Catalog - Simple but realistic
        self.products = [
            {"sku": "ARC-ATOM-M-BLK", "name": "Atom Hoody", "brand": "Arc'teryx", 
             "category": "Jackets", "price": 259.99, "in_stock": True},
            {"sku": "SAL-XULTRA-4-10", "name": "X Ultra 4 GTX", "brand": "Salomon", 
             "category": "Footwear", "price": 174.95, "in_stock": True},
            {"sku": "PAT-NANO-M-BLK", "name": "Nano Puff Hoody", "brand": "Patagonia", 
             "category": "Jackets", "price": 249.00, "in_stock": True},
            {"sku": "NIK-AIR-MAX", "name": "Air Max 270", "brand": "Nike", 
             "category": "Footwear", "price": 150.00, "in_stock": True},
            {"sku": "ADID-ULTRABOOST", "name": "Ultraboost 22", "brand": "Adidas", 
             "category": "Footwear", "price": 180.00, "in_stock": True},
        ]
        
        # User data - we'll generate this
        self.users = []
        
        # Event types
        self.event_types = ["page_view", "product_view", "add_to_cart", "purchase", "search"]
        
        # User agents
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/120.0",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15",
            "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36"
        ]
        
        print(" Data generator initialized!")

    def generate_users(self, num_users=50):
        """Generate realistic user profiles"""
        print(f"👤 Generating {num_users} users...")
        
        first_names = ["James", "Mary", "Robert", "Patricia", "John", "Jennifer", 
                       "Michael", "Linda", "David", "Elizabeth", "William", "Susan"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", 
                      "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez"]
        cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", 
                  "Philadelphia", "San Antonio", "San Diego", "Dallas", "Austin"]
        states = ["NY", "CA", "IL", "TX", "AZ", "PA", "TX", "CA", "TX", "TX"]
        
        for i in range(num_users):
            first = random.choice(first_names)
            last = random.choice(last_names)
            age = random.randint(18, 65)
            city_idx = random.randint(0, len(cities) - 1)
            
            # Generate some past purchases
            num_purchases = random.randint(0, 3)
            past_purchases = random.sample(self.products, num_purchases) if num_purchases > 0 else []
            
            user = {
                "user_id": f"usr_{uuid.uuid4().hex[:8]}",
                "email": f"{first.lower()}.{last.lower()}@email.com",
                "name": {"first": first, "last": last},
                "gender": random.choice(["male", "female"]),
                "age": age,
                "location": {"city": cities[city_idx], "state": states[city_idx]},
                "preferences": {
                    "preferred_brands": random.sample(
                        list(set([p["brand"] for p in self.products])), 
                        random.randint(1, 2)
                    )
                },
                "past_purchases": [p["sku"] for p in past_purchases],
                "loyalty_tier": random.choice(["Bronze", "Silver", "Gold"])
            }
            self.users.append(user)
        
        print(f" Generated {len(self.users)} users")
        return self.users

    def generate_event(self, user_id=None, platform=None, timestamp=None):
        """Generate a single event"""
        if timestamp is None:
            timestamp = datetime.now()
        
        if platform is None:
            platform = random.choice(["web", "ios", "android"])
        
        if user_id is None and self.users:
            user_id = random.choice(self.users)["user_id"] if random.random() > 0.2 else None
        
        # Select event type
        event_type = random.choice(self.event_types)
        
        # Build the event
        event = {
            "event_id": f"evt_{uuid.uuid4().hex[:12]}",
            "timestamp": timestamp.isoformat() + "Z",
            "platform": platform,
            "user_id": user_id,
            "session_id": f"sess_{uuid.uuid4().hex[:10]}",
            "device_id": f"dev_{uuid.uuid4().hex[:12]}",
            "event_type": event_type,
            "user_agent": random.choice(self.user_agents),
            "ip": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
        }
        
        # Add product data for relevant events
        if event_type in ["product_view", "add_to_cart", "purchase"]:
            product = random.choice(self.products)
            event["product"] = {
                "sku": product["sku"],
                "name": product["name"],
                "category": product["category"],
                "price": product["price"],
                "brand": product["brand"],
                "quantity": random.randint(1, 2)
            }
            
            if event_type == "purchase":
                event["order_id"] = f"ORD-{random.randint(1000, 9999)}"
                event["total_amount"] = product["price"] * event["product"]["quantity"]
        
        # Add search data
        if event_type == "search":
            event["search_query"] = random.choice([
                "hiking boots", "winter jacket", "running shoes", 
                "waterproof jacket", "camping gear"
            ])
            event["search_results"] = random.randint(5, 50)
        
        # Add recommendation source for some events
        if event_type == "product_view" and random.random() > 0.5:
            event["recommendation_source"] = {
                "placement": random.choice(["Homepage", "Product_Page", "Email"]),
                "algorithm": random.choice(["collaborative_filtering", "popular", "personalized"]),
                "position": random.randint(1, 10)
            }
        
        return event

    def generate_streaming_data(self, num_events=1000):
        """Generate streaming events over time"""
        print(f"📊 Generating {num_events} streaming events...")
        
        events = []
        start_time = datetime.now() - timedelta(hours=24)
        current_time = start_time
        
        for i in range(num_events):
            # Random time between events (5-120 seconds)
            seconds = random.randint(5, 120)
            current_time += timedelta(seconds=seconds)
            
            # Sometimes switch users
            if events and random.random() < 0.7:
                user_id = events[-1].get("user_id")
                platform = events[-1].get("platform")
            else:
                user_id = random.choice(self.users)["user_id"] if self.users and random.random() > 0.2 else None
                platform = random.choice(["web", "ios", "android"])
            
            event = self.generate_event(
                user_id=user_id,
                platform=platform,
                timestamp=current_time
            )
            events.append(event)
        
        print(f" Generated {len(events)} streaming events")
        return events

    def generate_batch_data(self, num_days=7, events_per_day=100):
        """Generate historical batch data"""
        print(f" Generating {num_days} days of batch data...")
        
        all_events = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=num_days)
        
        current_date = start_date
        
        while current_date <= end_date:
            # More events on weekends
            is_weekend = current_date.weekday() >= 5
            day_events = int(events_per_day * (1.5 if is_weekend else 1.0))
            
            for _ in range(day_events):
                hour = random.randint(8, 22)
                minute = random.randint(0, 59)
                second = random.randint(0, 59)
                timestamp = current_date.replace(hour=hour, minute=minute, second=second)
                
                user_id = random.choice(self.users)["user_id"] if self.users and random.random() > 0.3 else None
                platform = random.choice(["web", "ios", "android"])
                
                event = self.generate_event(
                    user_id=user_id,
                    platform=platform,
                    timestamp=timestamp
                )
                all_events.append(event)
            
            current_date += timedelta(days=1)
        
        print(f" Generated {len(all_events)} batch events")
        return all_events

    def save_data(self, events, output_dir="data_generator"):
        """Save data to files"""
        print(f"\n Saving data to {output_dir}/")
        
        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # 1. Save events as JSON Lines (for streaming)
        with open(f"{output_dir}/events_stream.jsonl", "w") as f:
            for event in events:
                f.write(json.dumps(event) + "\n")
        print(f"   events_stream.jsonl ({len(events)} events)")
        
        # 2. Save users
        with open(f"{output_dir}/user_profiles.json", "w") as f:
            json.dump(self.users, f, indent=2)
        print(f"   user_profiles.json ({len(self.users)} users)")
        
        # 3. Save users as CSV (easier to read)
        if self.users:
            with open(f"{output_dir}/user_profiles.csv", "w", newline="") as f:
                fieldnames = ["user_id", "email", "first_name", "last_name", "gender", 
                             "age", "city", "state", "loyalty_tier"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for user in self.users:
                    writer.writerow({
                        "user_id": user["user_id"],
                        "email": user["email"],
                        "first_name": user["name"]["first"],
                        "last_name": user["name"]["last"],
                        "gender": user["gender"],
                        "age": user["age"],
                        "city": user["location"]["city"],
                        "state": user["location"]["state"],
                        "loyalty_tier": user["loyalty_tier"]
                    })
            print(f"   user_profiles.csv ({len(self.users)} users)")
        
        # 4. Save products
        with open(f"{output_dir}/product_catalog.json", "w") as f:
            json.dump(self.products, f, indent=2)
        print(f"   product_catalog.json ({len(self.products)} products)")
        
        # 5. Generate clickstream summary
        clickstream = []
        for event in events:
            if event["event_type"] in ["product_view", "add_to_cart", "purchase"] and "product" in event:
                clickstream.append({
                    "date": event["timestamp"][:10],
                    "user_id": event["user_id"],
                    "event_type": event["event_type"],
                    "product_sku": event["product"]["sku"],
                    "platform": event["platform"]
                })
        
        if clickstream:
            with open(f"{output_dir}/clickstream_summary.csv", "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["date", "user_id", "event_type", "product_sku", "platform"])
                writer.writeheader()
                writer.writerows(clickstream)
            print(f"   clickstream_summary.csv ({len(clickstream)} records)")
        
        print(f"\n All data saved successfully!")

    def generate_all_data(self, num_users=50, num_stream_events=1000, 
                          num_batch_days=7, events_per_day=100, output_dir="data_generator"):
        """Generate all data"""
        print("=" * 60)
        print(" ECOMMERCE RECOMMENDATION DATA GENERATOR")
        print("=" * 60)
        
        # Step 1: Generate users
        self.generate_users(num_users)
        
        # Step 2: Generate streaming events
        stream_events = self.generate_streaming_data(num_stream_events)
        
        # Step 3: Generate batch events
        batch_events = self.generate_batch_data(num_batch_days, events_per_day)
        
        # Combine all events
        all_events = stream_events + batch_events
        
        # Step 4: Save all data
        self.save_data(all_events, output_dir)
        
        # Print summary
        print("\n" + "=" * 60)
        print(" DATA SUMMARY")
        print("=" * 60)
        print(f"Total users: {len(self.users)}")
        print(f"Total events: {len(all_events)}")
        print(f"  - Streaming events: {len(stream_events)}")
        print(f"  - Batch events: {len(batch_events)}")
        print(f"Total products: {len(self.products)}")
        
        # Event type distribution
        event_types = {}
        for event in all_events:
            event_types[event["event_type"]] = event_types.get(event["event_type"], 0) + 1
        
        print("\nEvent type distribution:")
        for event_type, count in sorted(event_types.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {event_type}: {count} ({count/len(all_events)*100:.1f}%)")
        
        # Platform distribution
        platforms = {}
        for event in all_events:
            platforms[event["platform"]] = platforms.get(event["platform"], 0) + 1
        
        print("\nPlatform distribution:")
        for platform, count in platforms.items():
            print(f"  - {platform}: {count} ({count/len(all_events)*100:.1f}%)")
        
        print("\n DATA GENERATION COMPLETE!")
        print(f"Files saved in: {output_dir}/")
        
        return all_events


def main():
    """Main function to run the generator"""
    try:
        # Create generator instance
        generator = EcommerceDataGenerator()
        
        # Generate all data
        generator.generate_all_data(
            num_users=50,           # Number of users
            num_stream_events=500,  # Streaming events
            num_batch_days=7,       # Days of batch data
            events_per_day=80,      # Events per day
            output_dir="data_generator"
        )
        
        # Show a sample event
        print("\n Sample Event:")
        with open("data_generator/events_stream.jsonl", "r") as f:
            first_line = f.readline()
            sample_event = json.loads(first_line)
            print(json.dumps(sample_event, indent=2))
        
        # Show a sample user
        print("\n👤 Sample User:")
        with open("data_generator/user_profiles.json", "r") as f:
            users = json.load(f)
            if users:
                print(json.dumps(users[0], indent=2))
        
        print("\n All done! Check the 'data_generator' folder for  files.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()