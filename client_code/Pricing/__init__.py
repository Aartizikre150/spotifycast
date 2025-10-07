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
    DAY_MAP = {
      "Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4,
      "Friday": 5, "Saturday": 6, "Sunday": 7
    }
    MONTH_MAP = {
      "January": 1, "February": 2, "March": 3, "April": 4,
      "May": 5, "June": 6, "July": 7, "August": 8,
      "September": 9, "October": 10, "November": 11, "December": 12
    }
    try:
      # Get text values from dropdowns (these are human-readable)
      day_text = self.day.selected_value           # e.g., "Monday"
      month_text = self.month.selected_value       # e.g., "January"
      
      # numeric for the model
      day_num = DAY_MAP.get(day_text, 0)
      month_num = MONTH_MAP.get(month_text, 0)

      data = {
        "day_encoded": day_num,
        "bpm": float(self.bpm.text),
        #"release_month": self.month.selected_value,
        "artist_count": int(self.artist_count.text),
        "year": int(self.year.text),
        "danceability": float(self.danceability.text),        # keys match server
        "acousticness": float(self.acousticness.text),
        "valence": float(self.valence.text),
        "liveness": float(self.liveness.text),
        "energy": float(self.energy.text),
        "instrumentalness": float(self.instrumentalness.text),
        "speechiness": float(self.speechiness.text),
        "predicted_streams": 0,
        "release_month": month_num,
        
      }
      row_id = anvil.server.call('save_prediction', data)
      # predict
      predicted = anvil.server.call('predict_stream_count', data)

      # show result
      self.stream_count.text = f"Predicted Streams: {predicted:,}"
      self.stream_count.visible = True
      self.disclaimer.visible = True

    except Exception as e:
      alert(f"Error: {e}")

     
