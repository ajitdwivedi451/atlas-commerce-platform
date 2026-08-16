import pandas as pd
import random
from faker import Faker

# 1. 🎯 FAKERS DEFINE KARNA ZAROORI HAI
generic_faker = Faker()
fakers = {
    "India": Faker('en_IN'),
    "United States": Faker('en_US'),
    "United Kingdom": Faker('en_GB'),
    "United Arab Emirates": Faker('ar_AE')
    # Baaki countries default (generic) use karengi
}

NUM_CUSTOMERS = 10_000

# location_mapping = { ... TUMHARA MEGA DICTIONARY YAHAN AAYEGA ... }
location_mapping = {
    "India": {
        "states": [
            "Maharashtra", "Karnataka", "Delhi", "Gujarat", "Tamil Nadu", 
            "Uttar Pradesh", "Rajasthan", "West Bengal", "Kerala", "Punjab", 
            "Haryana", "Bihar", "Madhya Pradesh", "Andhra Pradesh", "Telangana", 
            "Odisha", "Assam", "Jharkhand", "Chhattisgarh", "Uttarakhand"
        ],
        "cities": {
            "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad", "Thane"],
            "Karnataka": ["Bangalore", "Mysore", "Mangalore", "Hubli", "Belgaum", "Dharwad"],
            "Delhi": ["New Delhi", "Dwarka", "Rohini", "Saket", "Karol Bagh", "Vasant Kunj"],
            "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar", "Jamnagar"],
            "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Trichy", "Salem", "Tirunelveli"],
            "Uttar Pradesh": ["Lucknow", "Kanpur", "Agra", "Varanasi", "Noida", "Ghaziabad"],
            "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Bikaner", "Ajmer"],
            "West Bengal": ["Kolkata", "Darjeeling", "Siliguri", "Asansol", "Durgapur", "Howrah"],
            "Kerala": ["Thiruvananthapuram", "Kochi", "Kozhikode", "Thrissur", "Kollam", "Kannur"],
            "Punjab": ["Ludhiana", "Amritsar", "Jalandhar", "Patiala", "Bathinda", "Mohali"],
            "Haryana": ["Gurugram", "Faridabad", "Panipat", "Ambala", "Rohtak", "Hisar"],
            "Bihar": ["Patna", "Gaya", "Bhagalpur", "Muzaffarpur", "Purnia", "Darbhanga"],
            "Madhya Pradesh": ["Bhopal", "Indore", "Gwalior", "Jabalpur", "Ujjain", "Sagar"],
            "Andhra Pradesh": ["Visakhapatnam", "Vijayawada", "Guntur", "Nellore", "Tirupati", "Kurnool"],
            "Telangana": ["Hyderabad", "Warangal", "Nizamabad", "Karimnagar", "Khammam", "Ramagundam"],
            "Odisha": ["Bhubaneswar", "Cuttack", "Rourkela", "Berhampur", "Sambalpur", "Puri"],
            "Assam": ["Guwahati", "Silchar", "Dibrugarh", "Jorhat", "Nagaon", "Tezpur"],
            "Jharkhand": ["Ranchi", "Jamshedpur", "Dhanbad", "Bokaro", "Hazaribagh", "Deoghar"],
            "Chhattisgarh": ["Raipur", "Bhilai", "Bilaspur", "Korba", "Durg", "Rajnandgaon"],
            "Uttarakhand": ["Dehradun", "Haridwar", "Roorkee", "Haldwani", "Rudrapur", "Rishikesh"]
        }
    },
    
    "United States": {
        "states": [
            "California", "Texas", "New York", "Florida", "Illinois", 
            "Pennsylvania", "Ohio", "Georgia", "North Carolina", "Michigan", 
            "New Jersey", "Virginia", "Washington", "Arizona", "Massachusetts", 
            "Tennessee", "Indiana", "Missouri", "Maryland", "Wisconsin"
        ],
        "cities": {
            "California": ["Los Angeles", "San Francisco", "San Diego", "San Jose", "Fresno", "Sacramento"],
            "Texas": ["Houston", "Austin", "Dallas", "San Antonio", "Fort Worth", "El Paso"],
            "New York": ["New York City", "Buffalo", "Rochester", "Yonkers", "Syracuse", "Albany"],
            "Florida": ["Miami", "Orlando", "Tampa", "Jacksonville", "Tallahassee", "Fort Lauderdale"],
            "Illinois": ["Chicago", "Aurora", "Naperville", "Joliet", "Springfield", "Peoria"],
            "Pennsylvania": ["Philadelphia", "Pittsburgh", "Allentown", "Erie", "Reading", "Scranton"],
            "Ohio": ["Columbus", "Cleveland", "Cincinnati", "Toledo", "Akron", "Dayton"],
            "Georgia": ["Atlanta", "Augusta", "Columbus", "Macon", "Savannah", "Athens"],
            "North Carolina": ["Charlotte", "Raleigh", "Greensboro", "Durham", "Winston-Salem", "Fayetteville"],
            "Michigan": ["Detroit", "Grand Rapids", "Warren", "Sterling Heights", "Ann Arbor", "Lansing"],
            "New Jersey": ["Newark", "Jersey City", "Paterson", "Elizabeth", "Edison", "Trenton"],
            "Virginia": ["Virginia Beach", "Norfolk", "Chesapeake", "Richmond", "Newport News", "Alexandria"],
            "Washington": ["Seattle", "Spokane", "Tacoma", "Vancouver", "Bellevue", "Everett"],
            "Arizona": ["Phoenix", "Tucson", "Mesa", "Chandler", "Scottsdale", "Glendale"],
            "Massachusetts": ["Boston", "Worcester", "Springfield", "Cambridge", "Lowell", "Brockton"],
            "Tennessee": ["Nashville", "Memphis", "Knoxville", "Chattanooga", "Clarksville", "Murfreesboro"],
            "Indiana": ["Indianapolis", "Fort Wayne", "Evansville", "South Bend", "Carmel", "Bloomington"],
            "Missouri": ["Kansas City", "St. Louis", "Springfield", "Independence", "Columbia", "Lee's Summit"],
            "Maryland": ["Baltimore", "Frederick", "Rockville", "Gaithersburg", "Bowie", "Annapolis"],
            "Wisconsin": ["Milwaukee", "Madison", "Green Bay", "Kenosha", "Racine", "Appleton"]
        }
    },

    "Australia": {
        "states": ["New South Wales", "Victoria", "Queensland", "Western Australia", "South Australia", "Tasmania"],
        "cities": {
            "New South Wales": ["Sydney", "Newcastle", "Wollongong", "Central Coast", "Maitland", "Tamworth"],
            "Victoria": ["Melbourne", "Geelong", "Ballarat", "Bendigo", "Melton", "Shepparton"],
            "Queensland": ["Brisbane", "Gold Coast", "Sunshine Coast", "Townsville", "Cairns", "Toowoomba"],
            "Western Australia": ["Perth", "Mandurah", "Bunbury", "Kalgoorlie", "Albany", "Geraldton"],
            "South Australia": ["Adelaide", "Mount Gambier", "Gawler", "Whyalla", "Murray Bridge", "Port Lincoln"],
            "Tasmania": ["Hobart", "Launceston", "Devonport", "Burnie", "Kingston", "Ulverstone"]
        }
    },

    "France": {
        "states": ["Île-de-France", "Auvergne-Rhône-Alpes", "Provence-Alpes-Côte d'Azur", "Nouvelle-Aquitaine", "Occitanie", "Hauts-de-France"],
        "cities": {
            "Île-de-France": ["Paris", "Boulogne-Billancourt", "Saint-Denis", "Argenteuil", "Montreuil", "Nanterre"],
            "Auvergne-Rhône-Alpes": ["Lyon", "Grenoble", "Saint-Étienne", "Villeurbanne", "Valence", "Chambéry"],
            "Provence-Alpes-Côte d'Azur": ["Marseille", "Nice", "Toulon", "Aix-en-Provence", "Avignon", "Cannes"],
            "Nouvelle-Aquitaine": ["Bordeaux", "Limoges", "Poitiers", "Pau", "La Rochelle", "Mérignac"],
            "Occitanie": ["Toulouse", "Montpellier", "Nîmes", "Perpignan", "Béziers", "Montauban"],
            "Hauts-de-France": ["Lille", "Amiens", "Roubaix", "Tourcoing", "Dunkirk", "Calais"]
        }
    },

    "Singapore": {
        "states": ["Central Region", "East Region", "North Region", "North-East Region", "West Region", "Changi District"],
        "cities": {
            "Central Region": ["Downtown Core", "Marina Bay", "Orchard", "Newton", "River Valley", "Bukit Merah"],
            "East Region": ["Tampines", "Pasir Ris", "Bedok", "Paya Lebar", "Simei", "Kembangan"],
            "North Region": ["Woodlands", "Yishun", "Sembawang", "Mandai", "Simpang", "Kranji"],
            "North-East Region": ["Ang Mo Kio", "Hougang", "Punggol", "Sengkang", "Serangoon", "Seletar"],
            "West Region": ["Jurong East", "Jurong West", "Clementi", "Bukit Batok", "Tuas", "Boon Lay"],
            "Changi District": ["Changi Village", "Loyang", "Changi Bay", "Tanah Merah", "Changi Airport", "Xilin"]
        }
    },

    "United Arab Emirates": {
        "states": ["Dubai", "Abu Dhabi", "Sharjah"],
        "cities": {
            "Dubai": ["Downtown Dubai", "Deira", "Bur Dubai", "Jumeirah", "Business Bay", "Al Barsha"],
            "Abu Dhabi": ["Abu Dhabi City", "Al Ain", "Al Ruwais", "Zayed City", "Mussafah", "Khalifa City"],
            "Sharjah": ["Sharjah City", "Khor Fakkan", "Kalba", "Dibba Al-Hisn", "Al Dhaid", "Al Majaz"]
           
        }
    },

    "Japan": {
        "states": ["Tokyo", "Osaka", "Kyoto"],
        "cities": {
            "Tokyo": ["Shinjuku", "Shibuya", "Minato", "Chuo", "Taito", "Setagaya"],
            "Osaka": ["Osaka City", "Sakai", "Higashiosaka", "Hirakata", "Toyonaka", "Suita"],
            "Kyoto": ["Kyoto City", "Uji", "Kameoka", "Maizuru", "Nagaokakyo", "Yawata"]
        }
    }
}


country_details = {
    "India": {
        "market": "India",
        "currency": "INR"
    },
    "United States": {
        "market": "North America",
        "currency": "USD"
    },
    "United Kingdom": {
        "market": "Europe",
        "currency": "GBP"
    },
    "United Arab Emirates": {
        "market": "Middle East",
        "currency": "AED"
    },
    "Australia": {
        "market": "APAC",
        "currency": "AUD"
    },
    "France": {
        "market": "Europe",
        "currency": "EUR"
    },
    "Singapore": {
        "market": "APAC",
        "currency": "SGD"
    },
    "Japan": {
        "market": "APAC",
        "currency": "JPY"
    }
}
loyalty_tiers = ["Bronze", "Silver", "Gold", "Platinum"]
customer_statuses = ["Active", "Inactive"]

customers = []

# ==========================================
# PHASE 1: GENERATE CLEAN DATA
# ==========================================
for i in range(1, NUM_CUSTOMERS + 1):
    registration_date = generic_faker.date_between(start_date="-5y", end_date="today")
    date_of_birth = generic_faker.date_between(start_date="-70y", end_date="-18y")
    
    country = random.choice(list(location_mapping.keys()))
    state = random.choice(location_mapping[country]["states"])
    city = random.choice(location_mapping[country]["cities"][state])
    market = country_details[country]["market"]
    currency = country_details[country]["currency"]

    # 2. 🎯 LOCAL FAKER SELECT KARNA (Agar country fakers dict mein nahi hai, toh generic use hoga)
    local_faker = fakers.get(country, generic_faker)

    first_name = local_faker.first_name()
    last_name = local_faker.last_name()

    clean_first = first_name.replace(" ", "").lower()
    clean_last = last_name.replace(" ", "").lower()

    domain = generic_faker.free_email_domain()
    random_num = random.randint(10, 99)
    email = f"{clean_first}.{clean_last}{random_num}@{domain}"

    customer = {
        "customer_id": f"CUST{i:06d}",
        "first_name": first_name,      
        "last_name": last_name,        
        "email": email,                
        "phone": local_faker.phone_number(),
        "gender": random.choice(["Male", "Female", "Other"]),
        "date_of_birth": date_of_birth,
        "city": city,           
        "state": state,         
        "country": country,
        "market": market,
        "currency": currency,     
        "registration_date": registration_date,
        "customer_status": random.choice(customer_statuses),
        "loyalty_tier": random.choice(loyalty_tiers)
    }

    # 3. 🎯 BUG 1 FIXED: APPEND YAHAN HONA CHAHIYE (For loop ke andar)
    customers.append(customer)


print("😈 Injecting Data Engineering Edge Cases (Dirty Data)...")

# ==========================================
# PHASE 2: THE DIRTY DATA INJECTOR
# ==========================================
num_duplicates = int(NUM_CUSTOMERS * random.uniform(0.01, 0.02))
duplicates = random.choices(customers, k=num_duplicates)
customers.extend(duplicates)

for cust in customers:
    chance = random.random()
    
    if chance < 0.05:  
        cust['phone'] = None
        if random.random() < 0.5: 
            cust['city'] = None

    elif 0.05 <= chance < 0.07:  
        if cust['email']:
            cust['email'] = cust['email'].replace('@', '')

    elif 0.07 <= chance < 0.09:  
        cust['loyalty_tier'] = random.choice(["Diamond", "Unknown_Tier", "Level 99"])
        cust['customer_status'] = "Pending_Verification"

    elif 0.09 <= chance < 0.11:  
        cust['registration_date'] = generic_faker.date_between(start_date="+1y", end_date="+5y")
        cust['date_of_birth'] = generic_faker.date_between(start_date="-2y", end_date="+1y")

# ==========================================
# PHASE 3: SHUFFLE & SAVE
# ==========================================
random.shuffle(customers)

# Yahan se maine galat customers.append() hata diya hai

import os
output_dir = r"D:\Projects\atlas-commerce-platform\data-generation\customers"
os.makedirs(output_dir, exist_ok=True)
file_path = os.path.join(output_dir, "customers.csv")

df = pd.DataFrame(customers)
df.to_csv(file_path, index=False)

print(f"✅ Generated {len(df)} customer records (with Dirty Data).")
print(f"📁 Saved at: {file_path}")