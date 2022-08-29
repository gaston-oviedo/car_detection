import utils
import settings
from werkzeug.utils import secure_filename
import os

from middleware import model_predict
import json


from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    jsonify,
)

router = Blueprint("app_router", __name__, template_folder="templates")


@router.route("/", methods=["GET"])
def index():
    """
    Index endpoint, renders the HTML code.
    """
    return render_template("index.html")


@router.route("/", methods=["POST"])
def upload_image():
    """
    Function used in the frontend so we can upload and show an image.
    When it receives an image from the UI, it also calls the ML model to
    get and display the predictions.
    """
    # No file received, show basic UI
    if "file" not in request.files:
        flash("No file part")
        return redirect(request.url)

    # File received but no filename is provided, show basic UI
    file = request.files["file"]
    if file.filename == "":
        flash("No image selected for uploading")
        return redirect(request.url)

    # File received and it's an image, must show it and get predictions
    if file and utils.allowed_file(file.filename):
        file.filename = utils.get_file_hash(file)
        image_full_path = os.path.join(
            settings.UPLOAD_FOLDER, secure_filename(file.filename)
        )
        if (
            os.path.exists(image_full_path) == False
        ):  # To avoid overwritte the image on disk
            file.save(image_full_path)

        prediction_r, score_r = model_predict(file.filename)

        context = {
            "prediction": " ".join(prediction_r.split("_")).capitalize(),
            "score": str(round(score_r * 100, 2)) + "%",
            "filename": file.filename,
        }
        return render_template("index.html", filename=file.filename, context=context)
    # File received and but it isn't an image
    else:
        flash("Allowed image types are -> png, jpg, jpeg, gif")
        return redirect(request.url)


@router.route("/display/<filename>")
def display_image(filename):
    """
    Display uploaded image in the UI.
    """
    return redirect(url_for("static", filename="uploads/" + filename), code=301)


@router.route("/predict", methods=["POST"])
def predict():
    """
    Endpoint used to get predictions without need to access the UI.

    Parameters
    ----------
    file : str
        Input image we want to get predictions from.

    Returns
    -------
    flask.Response
        JSON response from our API having the following format:
            {
                "success": bool,
                "prediction": str,
                "score": float,
            }

        - "success" will be True if the input file is valid and we get a
          prediction from our ML model.
        - "prediction" model predicted class as string.
        - "score" model confidence score for the predicted class as float.
    """
    if "file" not in request.files:
        rpse = {"success": False, "prediction": None, "score": None}
        return jsonify(rpse), 400

    # File received but no filename is provided
    file = request.files["file"]
    if file.filename == "":
        rpse = {"success": False, "prediction": None, "score": None}
        return jsonify(rpse), 400

    # File received and it's an image, we must show it and get predictions
    if file and utils.allowed_file(file.filename):
        file.filename = utils.get_file_hash(file)
        image_full_path = os.path.join(
            settings.UPLOAD_FOLDER, secure_filename(file.filename)
        )
        if (
            os.path.exists(image_full_path) == False
        ):  # To avoid overwritte the image on disk
            file.save(image_full_path)

        prediction_r, score_r = model_predict(file.filename)

        rpse = {"success": True, "prediction": prediction_r, "score": score_r}
        return jsonify(rpse), 200
    else:
        rpse = {"success": False, "prediction": None, "score": None}
        return jsonify(rpse), 200


@router.route("/feedback", methods=["GET", "POST"])
def feedback():
    """
    Store feedback from users about wrong predictions on a text file.

    Parameters
    ----------
    report : request.form
        Feedback given by the user with the following JSON format:
            {
                "filename": str,
                "prediction": str,
                "score": float
            }

        - "filename" corresponds to the image used stored in the uploads
          folder.
        - "prediction" is the model predicted class as string reported as
          incorrect.
        - "score" model confidence score for the predicted class as float.
    """
    report = request.form.get("report")

    # Store the reported data to a file on the corresponding path
    # already provided in settings.py module
    if report is not None:
        fb_file = open(settings.FEEDBACK_FILEPATH, "a")
        fb_file.write(report + "\n")
        fb_file.close()

    return render_template("index.html")
