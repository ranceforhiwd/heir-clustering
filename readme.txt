Bellow commands for creating docker image:
 
Build image : docker buildx build --platform=linux/amd64 -t <imageName> .
For Developer: docker run -d -it -v ${PWD}:/usr/run/py <imageName> tail -f

* To run this image and check the code, run below commands
- go the docker terminal
- type below command 
- python3 findAddresses.py

* it will take pdf file name from statmechine input and process that input and save vocabulary, state
* zip code information in to markup table in dynamo db