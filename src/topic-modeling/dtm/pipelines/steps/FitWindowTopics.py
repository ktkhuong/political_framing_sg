import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
import logging
import os
import subprocess
from subprocess import Popen, CREATE_NEW_CONSOLE

class FitWindowTopics(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass
    
    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        
        return