# ===== server_module.py =====
import anvil.files
from anvil.files import data_files
import anvil.email
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from datetime import datetime
import numpy as np, pandas as pd
import joblib  # use joblib for .joblib models

# ---------------------------
# Contact form (unchanged)
# ---------------------------
@anvil.server.callable
def add_contact_info(name, email, topic, question):
  app_tables.contact.add_row(
    name=name, email=email, topic=topic, question=question, time=datetime.now()
  )
  anvil.email.send(
    from_name="Contact Form",
    subject="New Web Contact",
    text=(f"New web contact from {name} ({email})\n"
          f"Topic: {topic}\nComment/Question: {question}")
  )

# ---------------------------
# Save user submission
# ---------------------------
@anvil.server.callable  # optional but handy to call from client
def save_prediction(data: dict):
  def f(x): 
    return None if x in ("", None) else float(x)
  def i(x): 
    return None if x in ("", None) else int(x)

  row = app_tables.user_predictions.add_row(
    day_encoded = i(data.get("day_encoded")),
    bpm = f(data.get("bpm")),
    year = i(data.get("year")),                 # matches client "year"
    release_month = i(data.get("release_month")),
    artist_count = i(data.get("artist_count")),
    danceability = f(data.get("danceability")), # no % in names
    acousticness = f(data.get("acousticness")),
    valence = f(data.get("valence")),
    liveness = f(data.get("liveness")),
    energy = f(data.get("energy")),
    instrumentalness = f(data.get("instrumentalness")),
    speechiness = f(data.get("speechiness")),
    predicted_streams = i(data.get("predicted_streams", 0)),
    created_at = datetime.now()
  )
  return row  # your client stores this; you’re not using it further but it won’t be None

# ---------------------------
# Inference
# ---------------------------

# The model was trained on these feature names (aligned to your client code)
FEATURES = [
  'day_encoded', 'bpm', 'artist_count', 'year', 'release_month',
  'danceability', 'acousticness', 'valence', 'liveness',
  'energy', 'instrumentalness', 'speechiness'
]

# Load pipeline from Data Files (upload final_streams_random_forest_pipeline.joblib)
# Avoid hardcoded theme path; use data_files[] instead.
PIPE = joblib.load(data_files['final_streams_random_forest_pipeline.joblib'])

def _f(x):
  if x in ("", None): return np.nan
  try:
    return float(x)
  except:
    return np.nan

def _i(x):
  if x in ("", None): return np.nan
  try:
    return int(x)
  except:
    return np.nan

@anvil.server.callable
def predict_stream_count(form_data: dict) -> int:
  """
  Expects keys that match the FEATURES list above (same naming as client).
  Coerces types; allows NaNs (pipeline imputer should handle them).
  Returns a rounded int of expm1(pred) if your model predicts log(1+y).
  If your model predicts raw counts, remove the expm1 step.
  """
  row = {
    "day_encoded": _i(form_data.get("day_encoded")),
    "bpm": _f(form_data.get("bpm")),
    "artist_count": _i(form_data.get("artist_count")),
    "year": _i(form_data.get("year")),
    "release_month": _i(form_data.get("release_month")),
    "danceability": _f(form_data.get("danceability")),
    "acousticness": _f(form_data.get("acousticness")),
    "valence": _f(form_data.get("valence")),
    "liveness": _f(form_data.get("liveness")),
    "energy": _f(form_data.get("energy")),
    "instrumentalness": _f(form_data.get("instrumentalness")),
    "speechiness": _f(form_data.get("speechiness")),
  }

  X = pd.DataFrame([row], columns=FEATURES)
  y_pred = PIPE.predict(X)[0]

  # If the pipeline was trained on log1p(y), keep this. Otherwise, return int(round(y_pred)).
  try:
    y = float(np.expm1(y_pred))
  except Exception:
    y = float(y_pred)

  return int(round(y))
