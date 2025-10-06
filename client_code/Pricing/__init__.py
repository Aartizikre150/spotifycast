from ._anvil_designer import PricingTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from datetime import datetime
from anvil.tables import app_tables

class Pricing(PricingTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
  

  def Submit_click(self, **event_args):
    """This method is called when the button is clicked"""
    try:
      data = {
        "day_encoded": self.day.selected_value,
        "bpm": float(self.bpm.text),
        "release_month": self.month.selected_value,
        "artist_count": int(self.artist_count.text),
        "danceability": float(self.danceability.text),        # keys match server
        "acousticness": float(self.acousticness.text),
        "valence": float(self.valence.text),
        "liveness": float(self.liveness.text),
        "energy": float(self.energy.text),
        "instrumentalness": float(self.instrumentalness.text),
        "speechiness": float(self.speechiness.text),
        "predicted_streams": 0
      }
      row_id = anvil.server.call('save_prediction', data)
      self.stream_count.text = f"Predicted streams : {pred:,}"
      self.stream_count.visible = True
      self.disclaimer.visible = True
    except Exception as e:
      alert(f"Error: {e}")

     
