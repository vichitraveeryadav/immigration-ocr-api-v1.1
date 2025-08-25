#!/bin/bash
apt-get update
apt-get install -y tesseract-ocr tesseract-ocr-eng tesseract-ocr-hin
pip install pytesseract==0.3.10
