import time
from config import settings
from redis_om import get_redis_connection

redis = get_redis_connection(
    host=settings.redis_host,
    port=settings.redis_port,
    password=settings.redis_password,
    decode_responses=True
)

CONSUMER_GROUP = "notification-group"
CONSUMER_NAME  = "notification-consumer-1"
STREAMS = ["order_completed", "refund_order"]

for stream in STREAMS:
    try:
        redis.xgroup_create(stream, CONSUMER_GROUP, id="0", mkstream=True)
        print(f"[*] Grupa '{CONSUMER_GROUP}' aktivna za stream '{stream}'")
    except Exception:
        pass


def notify_order_completed(data: dict):
    order_id = data.get("pk", "N/A")
    product = data.get("product_id", "N/A")
    total = data.get("total", "N/A") 
    return f"Order Completed: ID {order_id} | Product {product} | Total {total} RSD"

def notify_order_refunded(data: dict):
    order_id = data.get("pk", "N/A")
    return f"Order Refunded: ID {order_id}"

HANDLERS = {
    "order_completed": notify_order_completed,
    "refund_order": notify_order_refunded
}

print("[*] Notification servis pokrenut. Ceka poruke...")

while True:
    try:
        result = redis.xreadgroup(
            groupname=CONSUMER_GROUP,
            consumername=CONSUMER_NAME,
            streams={stream: ">" for stream in STREAMS},
            count=1,
            block=5000
        )

        if result:
            for stream_name, messages in result:
                for message_id, data in messages:
                    handler = HANDLERS.get(stream_name)
                    if handler:
                        print(f"\n[OBRADENO] {handler(data)}")
                    
                    redis.xack(stream_name, CONSUMER_GROUP, message_id)

    except Exception as e:
        print(f"[!] Greška pri citanju: {e}")
        time.sleep(2)