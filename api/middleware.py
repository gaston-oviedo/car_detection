import time
import settings
import uuid
import json
import redis

db = redis.Redis(
    host=settings.REDIS_IP, port=settings.REDIS_PORT, db=settings.REDIS_DB_ID
)


def model_predict(image_name):
    """
    Receives an image name and queues the job into Redis.
    Will loop until getting the answer from the ML service.

    Parameters
    ----------
    image_name : str
        Name for the image uploaded by the user.

    Returns
    -------
    prediction, score : tuple(str, float)
        Model predicted class as a string and the corresponding confidence
        score as a number.
    """
    job_id = str(uuid.uuid4())
    msg_to_send = {"id": job_id, "image_name": image_name}
    job_data = msg_to_send

    # Sending the job to the model service using Redis
    db.rpush(settings.REDIS_QUEUE, json.dumps(job_data))

    # Loop until the response is received from the ML model

    while True:
        # Attempt to get model predictions using job_id
        output = db.get(job_id)

        # Sleep some time waiting for model results
        time.sleep(settings.API_SLEEP)

        if output == None:
            continue
        else:
            output_dict = json.loads(output)
            db.delete(job_id)
            break
    return output_dict["prediction"], output_dict["score"]
