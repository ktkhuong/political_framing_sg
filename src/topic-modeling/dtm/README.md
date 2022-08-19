# How to run

**Requirements**:
* Python 3.8
* Pip >= 22.2.2
* gcloud
* PuTTy

1. Create a virtual environment
```python
python -m venv env
```
2. Activate the virtual environment
```bash
env\Script\activate
```
3. Install plug-ins:
```python
pip install -r requirements.txt
```
4. Install `en-core-web-sm`
```python
python -m spacy download en_core_web_sm
```
4. See run.bat to see examples of how to run