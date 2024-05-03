FROM python:3.11
COPY . /usr/run/py
 
# LABEL about the custom image
LABEL maintainer="reymond.bolambao@churchillre.com"
 
# Installing packages
RUN pip3 install requests boto3
RUN pip3 install requests numpy
RUN pip3 install requests matplotlib
RUN pip3 install requests scikit-learn
RUN pip3 install requests pandas
RUN pip3 install requests scipy
RUN pip3 install requests us
RUN pip3 install tabulate us

# WORKDIR
WORKDIR /usr/run/py

# Script
CMD [ "python3", "findaddresses.py" ]
