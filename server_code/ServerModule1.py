import anvil.files
from anvil.files import data_files
import anvil.email
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from datetime import datetime


@anvil.server.callable
def add_contact_info(name, email, topic, question):
  app_tables.contact.add_row(name=name, email=email, topic=topic, question=question, time=datetime.now())
  anvil.email.send(from_name="Contact Form", 
                   subject="New Web Contact",
                   text=f"New web contact from {name} ({email})\nTopic: {topic}\nComment/Question: {question}")

@anvil.server.callable  # add require_user=True if you use anvil.users
def save_prediction(data):
  # Basic type coercion/safety (adjust as needed)
  def f(x): return None if x in ("", None) else float(x)
  def i(x): return None if x in ("", None) else int(x)

  # IMPORTANT: column names here must match your Data Table exactly
  row = app_tables.user_predictions.add_row(
    day_encoded=data.get("day_encoded"),
    bpm=f(data.get("bpm")),
    release_month=data.get("release_month"),
    artist_count=i(data.get("artist_count")),
    danceability=f(data.get("danceability")),       # no % in the column name
    acousticness=f(data.get("acousticness")),       # no %
    valence=f(data.get("valence")),                 # no %
    liveness=f(data.get("liveness")),               # no %
    energy=f(data.get("energy")),                   # no %
    instrumentalness=f(data.get("instrumentalness")),
    speechiness=f(data.get("speechiness")),
    predicted_streams=i(data.get("predicted_streams", 0)),
    created_at=datetime.now()
  )

  