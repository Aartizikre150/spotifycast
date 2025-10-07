from ._anvil_designer import PricingTemplate
from anvil import *
import anvil.server
from anvil.tables import app_tables
from datetime import datetime

class Pricing(PricingTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

    # Day and Month as (label, value) tuples → selected_value is already numeric
    self.day.items = [
      ("Monday", 1), ("Tuesday", 2), ("Wednesday", 3),
      ("Thursday", 4), ("Friday", 5), ("Saturday", 6), ("Sunday", 7)
    ]
    self.month.items = [
      ("January", 1), ("February", 2), ("March", 3), ("April", 4),
      ("May", 5), ("June", 6), ("July", 7), ("August", 8),
      ("September", 9), ("October", 10), ("November", 11), ("December", 12)
    ]

  # --- helpers ---
  def _f(self, txt):
    try:
      return float(txt)
    except:
      return None

  def _i(self, txt):
    try:
      return int(txt)
    except:
      return None

  def Submit_click(self, **event_args):
    """Called when the Submit button is clicked"""
    try:
      # Grab numeric selected values directly (already 1..7 / 1..12)
      day_num = self.day.selected_value
      month_num = self.month.selected_value

      # Basic required-fields check
      required = {
        "day": day_num, "month": month_num,
        "bpm": self.bpm.text, "artist_count": self.artist_count.text, "year": self.year.text,
        "danceability": self.danceability.text, "acousticness": self.acousticness.text,
        "valence": self.valence.text, "liveness": self.liveness.text,
        "energy": self.energy.text, "instrumentalness": self.instrumentalness.text,
        "speechiness": self.speechiness.text,
      }
      missing = [k for k, v in required.items() if v in ("", None)]
      if missing:
        alert(f"Please fill: {', '.join(missing)}")
        return

      data = {
        "day_encoded": self._i(day_num),
        "release_month": self._i(month_num),
        "bpm": self._f(self.bpm.text),
        "artist_count": self._i(self.artist_count.text),
        "year": self._i(self.year.text),
        "danceability": self._f(self.danceability.text),
        "acousticness": self._f(self.acousticness.text),
        "valence": self._f(self.valence.text),
        "liveness": self._f(self.liveness.text),
        "energy": self._f(self.energy.text),
        "instrumentalness": self._f(self.instrumentalness.text),
        "speechiness": self._f(self.speechiness.text),
        "predicted_streams": 0,
      }

      # Save, then predict
      anvil.server.call('save_prediction', data)
      predicted = anvil.server.call('predict_stream_count', data)

      # Show result
      self.stream_Count.text = f"Predicted Streams: {predicted:,}"
      self.stream_Count.visible = True
      self.diclaimer.visible = True

    except Exception as e:
      alert(f"Error: {e}")
