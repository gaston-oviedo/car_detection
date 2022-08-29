import time
import settings
import json
import redis
from tensorflow.keras.applications import resnet50
from tensorflow.keras.preprocessing import image
import numpy as np
import os


db = redis.Redis(
    host=settings.REDIS_IP, port=settings.REDIS_PORT, db=settings.REDIS_DB_ID
)

model = resnet50.ResNet50(include_top=True, weights="imagenet")


def predict(image_name):
    """
    Load image from the corresponding folder based on the image name
    received, then, run our ML model to get predictions.

    Parameters
    ----------
    image_name : str
        Image filename.

    Returns
    -------
    class_name, pred_probability : tuple(str, float)
        Model predicted class as a string and the corresponding confidence
        score as a number.
    """

    image_path = os.path.join(settings.UPLOAD_FOLDER, image_name)

    img = image.load_img(image_path, target_size=(224, 224))

    image_array = image.img_to_array(img)

    x = np.expand_dims(image_array, axis=0)
    x = resnet50.preprocess_input(x)

    # Get predictions
    preds = model.predict(x)

    # Get the most probable prediction
    most_prob_pred = resnet50.decode_predictions(preds, top=1)

    predict_class = most_prob_pred[0][0][1]
    predict_score = round(float(most_prob_pred[0][0][2]), 4)

    return predict_class, predict_score


def classify_process():
    """
    Loop indefinitely asking Redis for new jobs.
    When a new job arrives, takes it from the Redis queue, uses the loaded ML
    model to get predictions and stores the results back in Redis using
    the original job ID so other services can see it was processed and access
    the results.

    Load image from the corresponding folder based on the image name
    received, then, run our ML model to get predictions.
    """

    while True:
        queue_name, msg = db.brpop(settings.REDIS_QUEUE)

        msg = json.loads(msg)

        prediction_c, prediction_s = predict(msg["image_name"])

        received_msg = {"prediction": prediction_c, "score": prediction_s}

        db.set(msg["id"], json.dumps(received_msg))

        time.sleep(settings.SERVER_SLEEP)


if __name__ == "__main__":
    # Now launch process
    print("Launching ML service...")
    classify_process()
