import anvil.files
from anvil.files import data_files
import anvil.email
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from datetime import datetime
import numpy as np, pandas as pd
import pickle

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

# Must match training feature names exactly
FEATURES = [
  "day_encoded","acousticness_%","bpm","valence_%","release_month",
  "liveness_%","energy_%","instrumentalness_%","danceability_%","speechiness_%","artist_count",
]



with app_files.open("spoticast_rf_pipeline.pkl", "rb") as f:
  PIPE = pickle.load(f)
  
def _f(x):
  if x in ("", None): return np.nan
  try: return float(x)
  except: return np.nan

def _i(x):
  if x in ("", None): return np.nan
  try: return int(x)
  except: return np.nan
def predict_stream_count(form_data: dict) -> int:
  """
    form_data keys must match FEATURES.
    Values may be strings; we coerce to numeric and allow NaNs (imputer handles them).
    """
  row = {
    "day_encoded": _i(form_data.get("day_encoded")),
    "acousticness_%": _f(form_data.get("acousticness_%")),
    "bpm": _f(form_data.get("bpm")),
    "valence_%": _f(form_data.get("valence_%")),
    "release_month": _i(form_data.get("release_month")),
    "liveness_%": _f(form_data.get("liveness_%")),
    "energy_%": _f(form_data.get("energy_%")),
    "instrumentalness_%": _f(form_data.get("instrumentalness_%")),
    "danceability_%": _f(form_data.get("danceability_%")),
    "speechiness_%": _f(form_data.get("speechiness_%")),
    "artist_count": _i(form_data.get("artist_count")),
  }
  X = pd.DataFrame([row], columns=FEATURES)
  y_log = PIPE.predict(X)[0]
  y = float(np.expm1(y_log))
  return int(round(y))
