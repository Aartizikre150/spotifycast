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
import joblib
import numpy as np, pandas as pd
from anvil.files import data_files

# Load pipeline from Data Files
PIPE = joblib.load(data_files['final_streams_random_forest_pipeline.joblib'])

# Map client keys -> model's training feature names
CLIENT_TO_MODEL = {
  "day_encoded":     "release_day",        # UI "day" -> training "release_day"
  "bpm":             "bpm",
  "artist_count":    "artist_count",
  "year":            "release_year",       # UI "year" -> training "release_year"
  "release_month":   "release_month",
  "danceability":    "danceability_%",
  "acousticness":    "acousticness_%",
  "valence":         "valence_%",
  "liveness":        "liveness_%",
  "energy":          "energy_%",
  "instrumentalness":"instrumentalness_%",
  "speechiness":     "speechiness_%",
}

# Types: which features should be integers
INT_FEATURES = {"release_day", "release_month", "release_year", "artist_count"}

def _f(x):
  if x in ("", None): return np.nan
  try: return float(x)
  except: return np.nan

def _i(x):
  if x in ("", None): return np.nan
  try: return int(x)
  except: return np.nan

@anvil.server.callable
def predict_stream_count(form_data: dict) -> int:
  """
  Accepts client keys; maps to training feature names; orders to match training.
  """
  # Get exact training feature order if available
  expected = list(getattr(PIPE, "feature_names_in_", []))
  if not expected:
    # Fallback to mapped names order
    expected = list(CLIENT_TO_MODEL.values())

  # Convert client payload -> model-feature dict with proper types
  tmp = {}
  for client_key, model_key in CLIENT_TO_MODEL.items():
    v = form_data.get(client_key)
    if model_key in INT_FEATURES:
      tmp[model_key] = _i(v)
    else:
      tmp[model_key] = _f(v)

  # Ensure all expected features exist; fill any missing with NaN
  row = {name: tmp.get(name, np.nan) for name in expected}

  # Predict
  X = pd.DataFrame([row], columns=expected)
  y_pred = PIPE.predict(X)[0]

  # If the model was trained on log1p(y), expm1; otherwise return raw
  try:
    y = float(np.expm1(y_pred))
  except Exception:
    y = float(y_pred)

  return int(round(y))

# (Optional) Quick debug endpoint to see what the model expects:
@anvil.server.callable
def debug_expected_features():
  return list(getattr(PIPE, "feature_names_in_", []))