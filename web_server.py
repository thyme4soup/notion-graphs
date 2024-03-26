from flask import Flask, render_template, send_file, Response
import grapher
import os
import subprocess

app = Flask(__name__)
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 30


# Route that takes a task ID as the last argument and gives the embed
@app.route("/task/<string:task_id>")
def get_embed(task_id):
    return render_template("task_embed.html", task_id=task_id)


# Route that takes a task ID as the last argument and gives the graph image
@app.route("/graph/<string:task_id>")
def get_graph(task_id):
    img_path = grapher.get_image_path(task_id)
    if os.path.exists(img_path) and os.path.isfile(img_path):
        # refresh the image in the background and return the cached image
        subprocess.Popen(["python", "grapher.py", task_id, "&"])
        return send_file(img_path)
    else:
        # create the image fresh if it doesn't exist already
        return send_file(grapher.get_image(task_id))


# Route for the index in case someone gets curious
@app.route("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True, port=8080, host="0.0.0.0")
