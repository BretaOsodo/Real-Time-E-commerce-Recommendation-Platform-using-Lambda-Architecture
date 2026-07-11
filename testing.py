from data_generator.ecommerce_data import HighVolumeDataGenerator
import json
data=HighVolumeDataGenerator()

user_data= data.fetch_users_from_api()
print(type(user_data))
print(json.dumps(user_data,indent=4))