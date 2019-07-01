from django.shortcuts import render, redirect
from django.conf import settings
from django.core.files.storage import FileSystemStorage, Storage, default_storage
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.images import ImageFile

from uploads.core.models import Document
from uploads.core.forms import DocumentForm
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from PIL import Image

import nltk
nltk.download('stopwords')
nltk.download('punkt')
from nltk.corpus import stopwords
from collections import Counter
from nltk import word_tokenize
from sklearn.feature_extraction.text import CountVectorizer

import re
import os
import io
import urllib, base64
import matplotlib.pyplot as plt



def home(request):
    documents = Document.objects.all()
    return render(request, 'core/home.html', { 'documents': documents })


def simple_upload(request):
    error_text = {
        'file_size' : "The selected file is too large for this example analysis...",
        'file_type' : "Choose an appropriate text file with .txt extension..." 
        }

    if request.method == 'POST' and request.FILES['myfile']:
        if request.FILES['myfile'].size > 30000000:
            return render(request, 'core/simple_upload.html', {
            'error_text': error_text['file_size']
        })
        elif request.FILES['myfile'].content_type != 'text/plain':
            return render(request, 'core/simple_upload.html', {
            'error_text': error_text['file_type']
        })
        else:
            myfile = request.FILES['myfile']
            file_name = default_storage.save(myfile.name, myfile)
            with default_storage.open(file_name) as file:
                alltext = file.read()
            top_five_words = find_top_five_words(alltext)
            
            return render(request, 'core/simple_upload.html', {
                'top_five_url': top_five_words
            })
    return render(request, 'core/simple_upload.html')


def remove_stop_words(corpus):
    english_stop_words = stopwords.words('english')
    removed_stop_words = []
    removed_stop_words.append(
        ' '.join([word for word in corpus.split() 
                    if word not in english_stop_words])
    )
    return removed_stop_words


def find_top_five_words(textfile):
    the_text = ''.join(chr(character) for character in textfile)

    relevant = remove_stop_words(the_text.lower())
    relevant_words = relevant[0]
    wordcloud = WordCloud(max_font_size=50, max_words=100, background_color="white").generate(relevant_words)

    buff = io.BytesIO()
    plt.figure()
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")    
    plt.savefig(buff, format="png")
    content_file = ImageFile(buff)
    stored_image = default_storage.save('newimage.jpeg', content_file)
    file_url = default_storage.url(stored_image)
       
    return file_url

""" 
def model_form_upload(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = DocumentForm()
    return render(request, 'core/model_form_upload.html', {
        'form': form
    }) """
