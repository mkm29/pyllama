from kafka import KafkaConsumer

consumer = KafkaConsumer(bootstrap_servers="127.0.0.1:19092", auto_offset_reset="earliest") 

consumer.subscribe(topics=["kubernetes"])
for message in consumer:
    print(message)